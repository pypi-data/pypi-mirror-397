import os
import hashlib
import requests
import gc
import re
import pandas as pd
import torch
import torch.nn as nn
from typing import Literal
from collections import namedtuple
import sys
import psutil
import numpy as np

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
from sentence_transformers import SentenceTransformer

from tqdm import tqdm, trange
from transformers import AutoTokenizer, AutoModel
from loguru import logger

# Set environment variables for better performance
os.environ["PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT"] = "10"
torch.set_num_threads(1)

from sentence_transformers.util import (
    batch_to_device,
    truncate_embeddings,
)

### 
# Taken from fense (https://github.com/blmoistawinde/fense/)
RemoteFileMetadata = namedtuple('RemoteFileMetadata',
                                ['filename', 'url', 'checksum'])

def fetch_memory_usage():
    """
    Log current memory usage for debugging and optimization monitoring.
    
    Args:
        stage (str): Label indicating the current processing stage.
    """
    pid = os.getpid()
    process = psutil.Process(pid)
    mem_info = process.memory_info()
    memory_mb = mem_info.rss / 1024 / 1024 / 1024
    return f"{memory_mb:.2f} GB"

def get_data_home(data_home=None):
    if data_home is None:
        data_home = os.environ.get('FENSE_DATA',
                                os.path.join('~', '.fense_data'))
    data_home = os.path.expanduser(data_home)
    if not os.path.exists(data_home):
        os.makedirs(data_home)
    return data_home

def _sha256(path):
    """Calculate the sha256 hash of the file at path."""
    sha256hash = hashlib.sha256()
    chunk_size = 8192
    with open(path, "rb") as f:
        while True:
            buffer = f.read(chunk_size)
            if not buffer:
                break
            sha256hash.update(buffer)
    return sha256hash.hexdigest()

def _download_with_bar(url, file_path):
    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024    # 1 KB
    progress_bar = tqdm(total=total_size_in_bytes, unit='B', unit_scale=True)
    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise Exception("ERROR, something went wrong with the downloading")
    return file_path

def _fetch_remote(remote, dirname=None):
    file_path = (remote.filename if dirname is None
                 else os.path.join(dirname, remote.filename))
    file_path = _download_with_bar(remote.url, file_path)
    checksum = _sha256(file_path)
    if remote.checksum != checksum:
        raise IOError("{} has an SHA256 checksum ({}) "
                      "differing from expected ({}), "
                      "file may be corrupted.".format(file_path, checksum,
                                                      remote.checksum))
    return file_path

def download(remote, file_path=None):
    data_home = get_data_home()
    file_path = _fetch_remote(remote, data_home)
    return file_path

def check_download_resource(remote):
    data_home = get_data_home()
    file_path = os.path.join(data_home, remote.filename)
    if not os.path.exists(file_path):
        # currently don't capture error at this level, assume download success
        file_path = download(remote, data_home)
    return file_path

####

class BERTFlatClassifier(nn.Module):
    """
    BERT-based flat classifier for error detection in generated text.

    This classifier is used to detect errors in generated captions and apply
    penalty scores accordingly.

    Args:
        model_type (str): The BERT model type to use as backbone
        num_classes (int): Number of output classes (default: 5)
    """

    def __init__(self, model_type, num_classes=5) -> None:
        super().__init__()
        self.model_type = model_type
        self.num_classes = num_classes

        # Load pre-trained BERT model
        self.encoder = AutoModel.from_pretrained(model_type)
        self.dropout = nn.Dropout(self.encoder.config.hidden_dropout_prob)

        # Classification head
        self.clf = nn.Linear(self.encoder.config.hidden_size, num_classes)

    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None, **kwargs):
        """
        Forward pass of the classifier.

        Args:
            input_ids: Token IDs for input text
            attention_mask: Attention mask for input text
            token_type_ids: Token type IDs for input text

        Returns:
            logits: Classification logits
        """
        # Get BERT outputs
        outputs = self.encoder(input_ids, attention_mask, token_type_ids)

        # Use [CLS] token representation
        x = outputs.last_hidden_state[:, 0, :]
        x = self.dropout(x)

        # Generate classification logits
        logits = self.clf(x)
        return logits


class RefinedErrorChecker(nn.Module):
    """
    Refined error checker for detecting and penalizing errors in generated text.

    This module loads a pre-trained error detection model and applies penalties
    to generated captions that contain errors. It's used to improve the quality
    of evaluation by considering the correctness of generated text.

    Args:
        model_name_or_path (str): Name or path of the pre-trained error checker model
        device (str): Device to run the model on ('cuda' or 'cpu')
        error_threshold (float): Threshold for error detection (default: 0.9)
        penalty (float): Penalty factor for detected errors (default: 0.9)
        use_proxy (bool): Whether to use proxy for downloading models
        proxies (str): Proxy configuration
    """

    def __init__(
        self,
        model_name_or_path: str,
        device: Literal["cuda", "cpu"] = None,
        error_threshold: float = 0.9,
        penalty: float = 0.9,
        use_proxy: bool = False,
        proxies: str = None,
    ):
        super().__init__()
        # Disable tokenizer parallelism to avoid warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.error_threshold = error_threshold
        self.penalty = penalty

        # Load pre-trained error checker model from FENSE
        self.model = self.load_pretrain_echecker(model_name_or_path, device=self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model.model_type)

    def load_pretrain_echecker(
        self,
        model_name_or_path: str,
        device: Literal["cuda", "cpu"] = None,
        use_proxy: bool = False,

        proxies: str = None,
    ):
        """
        Load pre-trained error checker model from remote repository.

        Args:
            model_name_or_path (str): Model identifier
            device (str): Target device for the model
            use_proxy (bool): Whether to use proxy for downloading
            proxies (str): Proxy configuration

        Returns:
            torch.nn.Module: Loaded error checker model
        """
        # Available pre-trained error checker models
        PRETRAIN_ECHECKERS = {
            "echecker_clotho_audiocaps_base": (
                "https://github.com/blmoistawinde/fense/releases/download/V0.1/echecker_clotho_audiocaps_base.ckpt",
                "1a719f090af70614bbdb9f9437530b7e133c48cfa4a58d964de0d47fc974a2fa",
            ),
            "echecker_clotho_audiocaps_tiny": (
                "https://github.com/blmoistawinde/fense/releases/download/V0.1/echecker_clotho_audiocaps_tiny.ckpt",
                "90ed0ac5033ec497ec66d4f68588053813e085671136dae312097c96c504f673",
            ),
            "none": (None, None),
        }

        # Download model if needed
        url, checksum = PRETRAIN_ECHECKERS[model_name_or_path]
        remote = RemoteFileMetadata(filename=f"{model_name_or_path}.ckpt", url=url, checksum=checksum)
        file_path = check_download_resource(remote)

        # Load model state and create classifier
        model_states = torch.load(file_path, weights_only=True)
        clf = BERTFlatClassifier(model_type=model_states["model_type"], num_classes=model_states["num_classes"])

        # Load pre-trained weights
        dict_new = clf.state_dict().copy()
        trained_list = [i for i in model_states["state_dict"].keys() if "encoder.embeddings.position_ids" not in i]
        for i in range(len(trained_list)):
            dict_new[trained_list[i]] = model_states["state_dict"][trained_list[i]]

        clf.load_state_dict(dict_new)
        clf.eval()
        clf.to(device)
        return clf

    def text_preprocess(self, inp):
        """
        Preprocess input text by removing punctuation and converting to lowercase.

        Args:
            inp (str or list): Input text(s) to preprocess

        Returns:
            str or list: Preprocessed text(s)
        """
        if type(inp) == str:
            return re.sub(r"[^\w\s]", "", inp).lower()
        else:
            return [re.sub(r"[^\w\s]", "", x).lower() for x in inp]

    def infer_preprocess(self, tokenizer, texts, max_len):
        """
        Preprocess texts for inference using the tokenizer.

        Args:
            tokenizer: HuggingFace tokenizer
            texts (list): List of texts to tokenize
            max_len (int): Maximum sequence length

        Returns:
            dict: Tokenized batch ready for model input
        """
        texts = self.text_preprocess(texts)
        batch = tokenizer(texts, truncation=True, padding="max_length", max_length=max_len)

        # Convert to tensors
        for k in ["input_ids", "attention_mask", "token_type_ids"]:
            batch[k] = torch.LongTensor(batch[k])
        return batch

    def forward(
        self,
        sentences: str | list,
        batch_size: int = 32,
    ):
        """
        Detect errors in input sentences and apply penalties.

        Args:
            sentences (str or list): Input sentence(s) to check for errors
            batch_size (int): Batch size for processing multiple sentences

        Returns:
            torch.Tensor: Penalty scores (1.0 for no error, penalty factor for errors)
        """
        if type(sentences) == str:
            sentences = [sentences]

        if len(sentences) == 1:
            # Process single sentence
            batch = self.infer_preprocess(self.tokenizer, sentences, max_len=64)
            for k, v in batch.items():
                batch[k] = v.to(self.device)

            with torch.no_grad():
                logits = self.model(**batch)
                probs = torch.sigmoid(logits).detach().cpu().numpy()

            # Check if error probability exceeds threshold
            has_error = probs[0][-1] > self.error_threshold
            output = (1 - self.penalty) if has_error else 1
            output = torch.tensor([output])
        else:
            # Process multiple sentences in batches
            probs = []
            for i in trange(0, len(sentences), batch_size):
                batch = self.infer_preprocess(self.tokenizer, sentences[i : i + batch_size], max_len=256)
                for k, v in batch.items():
                    batch[k] = v.to(self.device)

                with torch.no_grad():
                    batch_logits = self.model(**batch)
                    batch_probs = torch.sigmoid(batch_logits)[:, -1]
                probs.append(batch_probs)

            # Combine all probabilities and apply penalties
            probs = torch.cat(probs)
            has_error = probs > self.error_threshold
            output = has_error * (1 - self.penalty)
            output[output == 0] = 1

        return output


class RefinedSentenceTransformers(nn.Module):
    """
    Enhanced sentence transformer wrapper for generating various types of embeddings.

    This class provides a unified interface for generating different types of embeddings
    from text input, including word embeddings, token embeddings, and sentence embeddings.
    It serves as the core text encoding component for the DATE evaluation system.

    Args:
        model_name_or_path (str): Name or path of the sentence transformer model
        device (str): Device to run the model on ('cuda' or 'cpu')
    """

    def __init__(
        self,
        model_name_or_path: str,
        device: Literal["cuda", "cpu"] = None,
    ):
        super().__init__()
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # CPU priority strategy: keep data on CPU by default, only move to GPU when needed
        self.compute_device = self.device  # Device for actual computation
        self.storage_device = "cpu"  # Device for data storage (always CPU)

        # Load the sentence transformer model
        self.sbert = SentenceTransformer(model_name_or_path, device=self.device)

        # Extract the underlying BERT model for direct access
        for name, module in self.sbert.named_children():
            self.auto_model = module.auto_model
            break

    def encode_features(
        self,
        features: dict,
        output_value: Literal[
            "input_ids", "word_embeddings", "token_embeddings", "sentence_embedding"
        ] = "sentence_embedding",
    ):
        """
        Generate embeddings from input features.

        This method can generate different types of embeddings based on the output_value parameter:
        - input_ids: Return the input token IDs (no embedding computation)
        - word_embeddings: Return word-level embeddings from the embedding layer
        - token_embeddings: Return token-level embeddings from the transformer
        - sentence_embedding: Return sentence-level embeddings (default)

        Args:
            features (dict): Input features containing input_ids, attention_mask, etc.
            output_value (str): Type of embedding to generate

        Returns:
            dict: Dictionary containing the requested embeddings and metadata
        """
        # Move features to the target device
        features = batch_to_device(features, self.device)

        if output_value != "input_ids":
            with torch.no_grad():
                if output_value == "word_embeddings":
                    # Generate word embeddings directly from the embedding layer
                    embeddings = self.auto_model.embeddings.word_embeddings(features["input_ids"])
                else:
                    # Generate embeddings using the sentence transformer
                    out_features = self.sbert.forward(features)

                    # Apply truncation if specified
                    out_features["sentence_embedding"] = truncate_embeddings(
                        out_features["sentence_embedding"], self.sbert.truncate_dim
                    )

                    if output_value == "token_embeddings":
                        # Keep the original shape [n_sents, seq_len, emb_dim] for compatibility
                        # with DATE_detailed.py which expects this format
                        embeddings = out_features[output_value]
                        embeddings = embeddings.to(torch.float16)
                    else:
                        # For sentence embeddings, use the output directly
                        embeddings = out_features[output_value]
        else:
            # Return input IDs without processing
            embeddings = features["input_ids"]

        # Prepare output features dictionary
        output_features = {"embeddings": embeddings, "features": features}
        # Always move output to CPU for storage
        output_features = batch_to_device(output_features, self.storage_device)
        return output_features

    def encode_sentences(
        self,
        sentences: str | list,
        batch_size: int = 32,
        output_value: Literal[
            "input_ids", "word_embeddings", "token_embeddings", "sentence_embedding"
        ] = "sentence_embedding",
    ):
        """
        Encode sentences into embeddings with batched processing.

        This method tokenizes input sentences and generates embeddings using the
        specified embedding type. It supports both single sentences and batches.

        Args:
            sentences (str or list): Input sentence(s) to encode
            batch_size (int): Batch size for processing multiple sentences
            output_value (str): Type of embedding to generate

        Returns:
            dict: Dictionary containing embeddings and tokenization features
        """
        # Ensure sentences is a list
        if isinstance(sentences, str):
            sentences = [sentences]

        # If there are fewer sentences than batch_size, process all at once
        if len(sentences) <= batch_size:
            features = self.sbert.tokenize(sentences)
            return self.encode_features(features, output_value=output_value)
        
        # Process sentences in batches
        all_embeddings = []
        all_features_list = []
        
        # First pass: find maximum sequence length across all batches
        max_length = 0
        for i in range(0, len(sentences), batch_size):
            batch_sentences = sentences[i:i + batch_size]
            batch_features = self.sbert.tokenize(batch_sentences)
            max_length = max(max_length, batch_features["input_ids"].shape[1])
        
        # Second pass: process all batches with consistent padding
        for i in tqdm(range(0, len(sentences), batch_size)):
            batch_sentences = sentences[i:i + batch_size]
            batch_features = self.sbert.tokenize(batch_sentences)
            
            # Pad to max_length if needed
            current_length = batch_features["input_ids"].shape[1]
            if current_length < max_length:
                pad_length = max_length - current_length
                
                # Pad input_ids
                batch_features["input_ids"] = torch.cat([
                    batch_features["input_ids"],
                    torch.zeros(batch_features["input_ids"].shape[0], pad_length, dtype=torch.long, device=batch_features["input_ids"].device)
                ], dim=1)
                
                # Pad attention_mask
                batch_features["attention_mask"] = torch.cat([
                    batch_features["attention_mask"],
                    torch.zeros(batch_features["attention_mask"].shape[0], pad_length, dtype=torch.long, device=batch_features["attention_mask"].device)
                ], dim=1)
                
                # Pad token_type_ids if it exists
                if "token_type_ids" in batch_features:
                    batch_features["token_type_ids"] = torch.cat([
                        batch_features["token_type_ids"],
                        torch.zeros(batch_features["token_type_ids"].shape[0], pad_length, dtype=torch.long, device=batch_features["token_type_ids"].device)
                    ], dim=1)
            
            # Process this batch
            batch_output = self.encode_features(batch_features, output_value=output_value)
            
            # Collect results
            all_embeddings.append(batch_output["embeddings"])
            all_features_list.append(batch_output["features"])
            
            # Clear GPU memory if using CUDA
            if self.device == "cuda":
                torch.cuda.empty_cache()
        
        # Concatenate embeddings
        concatenated_embeddings = torch.cat(all_embeddings, dim=0)
        
        # Concatenate features - ensure all tensors have the same size
        concatenated_features = {}
        if all_features_list:
            for key in all_features_list[0].keys():
                if isinstance(all_features_list[0][key], torch.Tensor):
                    # Check if all tensors have the same size except for the first dimension
                    first_tensor = all_features_list[0][key]
                    tensor_shape = first_tensor.shape[1:]  # All dimensions except batch dimension
                    
                    # Verify all tensors have the same shape
                    for f in all_features_list[1:]:
                        if f[key].shape[1:] != tensor_shape:
                            raise ValueError(f"Tensor size mismatch for key '{key}'. Expected shape {tensor_shape}, got {f[key].shape[1:]}")
                    
                    concatenated_features[key] = torch.cat([f[key] for f in all_features_list], dim=0)
                elif isinstance(all_features_list[0][key], list):
                    concatenated_features[key] = []
                    for f in all_features_list:
                        concatenated_features[key].extend(f[key])
                else:
                    concatenated_features[key] = all_features_list[0][key]
        
        return {
            "embeddings": concatenated_embeddings,
            "features": concatenated_features
        }


class DATE(nn.Module):
    """
    DATE (Discriminability based Audio Task Evaluation) - Main evaluation class.

    This class implements the DATE metric for evaluating audio captioning and QA systems.
    DATE combines similarity and discrimination components using a harmonic mean to provide
    a comprehensive evaluation score. It supports both FENSE and DATE evaluation modes.

    Key Features:
    - Dual evaluation modes: FENSE (similarity only) and DATE (similarity + discrimination)
    - TF-IDF weighted embeddings for improved text representation
    - Error detection and penalty mechanisms
    - Batch processing for efficiency
    - Support for various audio content types

    Args:
        sbert_name_or_path (str): Name or path of the sentence transformer model
        echecker_name_or_path (str): Name or path of the error checker model
        device (str): Device to run models on ('cuda' or 'cpu')
        error_threshold (float): Threshold for error detection (default: 0.9)
        penalty (float): Penalty factor for detected errors (default: 0.9)
        use_proxy (bool): Whether to use proxy for model downloads
        proxies (str): Proxy configuration
        is_clamp_neg_similarity (bool): Whether to clamp negative similarities
        return_type (str): Evaluation mode ('fense' or 'date')
    """

    def __init__(
        self,
        sbert_name_or_path: str = "paraphrase-TinyBERT-L6-v2",
        echecker_name_or_path: str = "echecker_clotho_audiocaps_base",
        device: Literal["cuda", "cpu"] = None,
        error_threshold: float = 0.9,  # parameter of echecker model
        penalty: float = 0.9,  # parameter of echecker model
        use_proxy: bool = False,  # parameter of echecker model
        proxies: str = None,  # parameter of echecker model
        is_clamp_neg_similarity: bool = False,
        return_type: Literal["fense", "date"] = "date",
        cpu_priority: bool = True,  # New parameter for CPU-first strategy
    ):
        super().__init__()
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # CPU priority strategy: keep data on CPU by default, only move to GPU when needed
        self.cpu_priority = cpu_priority
        self.compute_device = self.device  # Device for actual computation
        self.storage_device = "cpu" if cpu_priority else self.device  # Device for data storage
        
        # Log device selection
        if torch.cuda.is_available():
            logger.info(f"CUDA available. Using device: {self.device}")
            if self.device == "cuda":
                logger.info(f"GPU: {torch.cuda.get_device_name()}")
                if self.cpu_priority:
                    logger.info("CPU priority mode enabled: data will be stored on CPU and moved to GPU only for computation")
        else:
            logger.info(f"CUDA not available. Using device: {self.device}")
            
        self.return_type = return_type
        self.is_clamp_neg_similarity = is_clamp_neg_similarity

        # Initialize core components
        self.model = RefinedSentenceTransformers(sbert_name_or_path, device)
        self.echecker = RefinedErrorChecker(echecker_name_or_path, device, error_threshold, penalty, use_proxy, proxies)

        # Pre-computed delta values for different field types and data variants
        # These values are optimized for different audio content categories
        self.subset_data_delta = {
            "long": {"all": 0.1703},  # Long-form captions (x)
            "short": {"all": 0.1772},  # Short-form captions (x)
            "speech": {"pure": 0.2078, "mixed": 0.2078},  # Speech content
            "music": {"pure": 0.1566, "mixed": 0.1851},  # Music content
            "sound": {"pure": 0.1988, "mixed": 0.2593},  # General sound effects
            "environment": {"all": 0.2150},  # Environmental sounds (x)
        }

    def calcualte_tf_idf_weight(
        self,
        word_similarity: torch.Tensor,
        word2doc_similarity: None, # This argument is None in the optimized version
        batch_output: dict,
        idf_type: Literal["token", "embedding"] = "embedding",
    ):
        """
        Calculate TF-IDF weights using precomputed statistics to improve text representation.
        
        This method computes the final TF-IDF weights based on pre-calculated IDF sums and 
        word similarity matrices. It supports mixed precision (FP16 storage, FP32 compute)
        to maintain numerical stability while optimizing memory.

        Args:
            word_similarity (torch.Tensor or np.ndarray): Word-to-word similarity matrix
            word2doc_similarity (None): Unused in optimized version (passed as None)
            batch_output (dict): Batch output containing features and precomputed stats
            idf_type (str): Type of IDF calculation ('token' or 'embedding')

        Returns:
            torch.Tensor: Flat tensor containing TF-IDF weights for each token (FP16)
        """
        
        # Retrieve precomputed IDF sum from batch_output
        idf_sum = batch_output["_precomputed_idf_sum"]
        n_sents, seq_len = batch_output["features"]["input_ids"].shape

        # Calculate final IDF values using log normalization (FP32)
        idf = torch.log((n_sents + 1) / (idf_sum + 1)) + 1
        idf = idf.to(self.device)

        # Calculating the tf-idf weight 
        # Initialize weight matrix (FP16 storage on CPU)
        flat_tfidf_weights = torch.ones((n_sents, seq_len), dtype=torch.float16, device="cpu")
        input_ids = batch_output["features"]["input_ids"].detach().cpu().numpy()
        mapping_jsonkey2sentidx = batch_output["mapping_jsonkey2sentidx"]
        mapping_wordkey2vecidx = batch_output["mapping_wordkey2vecidx"]

        # Ensure word_similarity is in numpy format for indexing
        if isinstance(word_similarity, torch.Tensor):
            word_sim_cpu = word_similarity.numpy()
        else:
            word_sim_cpu = word_similarity

        for tmp_json_key, (tmp_start, tmp_end) in tqdm(mapping_jsonkey2sentidx.items(), desc="Final TF-IDF"):
            batch_ids = input_ids[tmp_start:tmp_end]
            segment_weights = []

            for i, input_id in enumerate(batch_ids):
                # Strictly match DATE0 logic: Filter out PAD(0), CLS(101), SEP(102)
                valid_ids = input_id[(input_id != 0) & (input_id != 101) & (input_id != 102)]
                word_indices = [mapping_wordkey2vecidx[tmp_id] for tmp_id in valid_ids if tmp_id in mapping_wordkey2vecidx]
                
                # DATE0 logic: Use FP32 for intermediate calculations to preserve precision
                # Length + 2 accommodates [CLS] and [SEP]
                tmp_tf_idf = torch.ones(len(word_indices) + 2, device=self.device, dtype=torch.float32)

                if word_indices:
                    # Read similarity from FP16 storage, convert to FP32 for computation
                    selected_slice = word_sim_cpu[np.ix_(word_indices, word_indices)]
                    selected = torch.from_numpy(selected_slice).to(self.device, dtype=torch.float32)
                    
                    # Calculate TF (Term Frequency)
                    tf_weights = torch.sum(selected**2, dim=1)
                    idf_weights = idf[word_indices]
                    
                    # Fill middle section (corresponding to actual words)
                    tmp_tf_idf[1:-1] = tf_weights * idf_weights
                    
                    # Normalize weights
                    mean_val = tmp_tf_idf[1:-1].mean()
                    if mean_val > 1e-9:
                         tmp_tf_idf[1:-1] = tmp_tf_idf[1:-1] / mean_val

                    # Set weights for special tokens ([CLS] max, [SEP] min)
                    tmp_tf_idf[0] = torch.max(tmp_tf_idf)
                    tmp_tf_idf[-1] = torch.min(tmp_tf_idf)

                # Map calculated weights back to sequence length
                padded_tfidf = torch.ones(seq_len, device=self.device, dtype=torch.float32)
                
                # Determine actual length of non-padding tokens
                actual_len = len(input_id[input_id != 0])
                # Truncate or pad safely to avoid index errors
                safe_len = min(len(tmp_tf_idf), actual_len)
                if safe_len > 0:
                    padded_tfidf[:safe_len] = tmp_tf_idf[:safe_len]

                segment_weights.append(padded_tfidf)
            
            if segment_weights:
                # Convert back to FP16 and store in CPU memory
                segment_stack = torch.stack(segment_weights).to("cpu", dtype=torch.float16)
                flat_tfidf_weights[tmp_start:tmp_end] = segment_stack
                
        return flat_tfidf_weights

    def calculate_penalty(self, batch_output: dict, batch_size: int = 32):
        """
        Calculate penalty scores for all sentences using the error checker.

        This method applies the error detection model to identify potential errors
        in generated text and assigns penalty scores accordingly.

        Args:
            batch_output (dict): Batch output containing sentence data
            batch_size (int): Batch size for error checking

        Returns:
            torch.Tensor: Penalty scores for each sentence
        """
        all_sentences = batch_output["all_sentences"]
        mapping_jsonkey2sentidx = batch_output["mapping_jsonkey2sentidx"]
        penalities = self.echecker(all_sentences.copy(), batch_size=batch_size)

        return penalities

    def fetch_word_embeddings(self, input_ids_all: torch.Tensor):
        """
        Calculate word similarity and IDF statistics using optimized static embeddings.
        
        This method strictly aligns with the original logic by using static embeddings from the 
        input layer (rather than transformer outputs) to calculate similarity and IDF stats.
        It significantly reduces memory usage by processing unique tokens only.

        Args:
            input_ids_all (torch.Tensor): Tensor containing input IDs for all sentences.

        Returns:
            tuple: (word_sim, idf_accumulator, unique_id_map)
                - word_sim: Word-to-word similarity matrix
                - idf_accumulator: Accumulated IDF statistics
                - unique_id_map: Mapping from token ID to index in similarity matrix
        """
        
        # 1. Get Unique Token IDs
        unique_input_ids = torch.unique(input_ids_all)
        # Filter out special tokens
        valid_mask = (unique_input_ids != 0) & (unique_input_ids != 101) & (unique_input_ids != 102)
        unique_input_ids = unique_input_ids[valid_mask]
        
        logger.info(f"Unique tokens to process: {len(unique_input_ids)}")

        # 2. Calculate Static Embeddings for unique tokens only
        # Key Correction: The original logic uses static embeddings from the input layer,
        # not the transformer output. This is faster and saves memory.
        unique_embeddings_list = []
        process_batch_size = 4096 
        
        with torch.no_grad():
            for i in range(0, len(unique_input_ids), process_batch_size):
                batch_ids = unique_input_ids[i : i + process_batch_size].to(self.device)
                
                # Directly access the Embedding layer, skipping the Transformer
                emb = self.model.auto_model.embeddings.word_embeddings(batch_ids)
                unique_embeddings_list.append(emb.cpu())
        
        if not unique_embeddings_list:
             return None, None, {}

        unique_embeddings = torch.cat(unique_embeddings_list, dim=0)
        unique_id_map = {uid.item(): idx for idx, uid in enumerate(unique_input_ids)}
        
        # 3. Calculate Word-Word Similarity Matrix (FP16 is sufficient and aligns with original)
        unique_embeddings = unique_embeddings.to(self.device, dtype=torch.float16)
        unique_embeddings = torch.nn.functional.normalize(unique_embeddings, p=2, dim=-1)
        
        n_words = len(unique_input_ids)
        word_sim = torch.zeros((n_words, n_words), dtype=torch.float16, device='cpu')
        
        with torch.no_grad():
            for i in range(0, n_words, 1024):
                end_i = min(i + 1024, n_words)
                block = torch.mm(unique_embeddings[i:end_i], unique_embeddings.t())
                if self.is_clamp_neg_similarity:
                    block = torch.clamp(block, min=0)
                word_sim[i:end_i] = block.cpu()
        
        # 4. Calculate IDF Stats (Streaming + Static Embeddings)
        # Use FP32 for IDF accumulator to ensure precision alignment
        idf_accumulator = torch.zeros(n_words, dtype=torch.float32, device=self.device)
        
        # Build Lookup Table (FP16)
        vocab_size = self.model.sbert.tokenizer.vocab_size
        full_emb_table = torch.zeros((vocab_size, unique_embeddings.shape[1]), dtype=torch.float16, device=self.device)
        
        indices = unique_input_ids.long().to(self.device)
        full_emb_table.index_copy_(0, indices, unique_embeddings)
        
        idf_batch_size = 256
        n_sents = len(input_ids_all)
        
        for i in tqdm(range(0, n_sents, idf_batch_size), desc="IDF Stream"):
            end_i = min(i + idf_batch_size, n_sents)
            batch_ids = input_ids_all[i:end_i].to(self.device).long()
            
            # Lookup Static Embeddings from table
            batch_embs = torch.nn.functional.embedding(batch_ids, full_emb_table)
            
            # Mask special tokens (keep FP16)
            batch_mask = (batch_ids != 0) & (batch_ids != 101) & (batch_ids != 102)
            batch_mask = batch_mask.unsqueeze(-1).to(dtype=batch_embs.dtype)
            
            batch_embs = batch_embs * batch_mask
            
            # Calculate similarity (FP16)
            flat_input = batch_embs.reshape(-1, unique_embeddings.shape[1])
            sim_flat = torch.mm(unique_embeddings, flat_input.t())
            
            sim_3d = sim_flat.reshape(n_words, end_i - i, -1)
            
            sim_sq = sim_3d.pow(2)
            doc_scores = torch.sum(sim_sq, dim=2)
            doc_scores = torch.clamp(doc_scores, min=0, max=1.0)
            
            # Accumulate scores (Convert to FP32)
            idf_accumulator += torch.sum(doc_scores.float(), dim=1)
            
        del full_emb_table, unique_embeddings
        return word_sim, idf_accumulator, unique_id_map

    def update_word_embeddings(
        self,
        json_data: dict,
        subtask: str = "long",
        n_sents: int = None,
        tf_idf_weighted: bool = True,
        idf_type: Literal["token", "embedding"] = "embedding",
        batch_size: int = 32,
    ):
        """
        Generates only TF-IDF weights, avoiding full Word Embedding storage.

        This method processes input data to generate TF-IDF weights without keeping the 
        entire word embedding matrix in memory. It uses the `fetch_word_embeddings`
        routine to calculate necessary statistics efficiently.

        Args:
            json_data (dict): Input data containing text samples
            subtask (str): Field name to extract text from (default: 'long')
            n_sents (int): Number of sentences to use (None for all)
            tf_idf_weighted (bool): Whether to apply TF-IDF weighting
            idf_type (str): Type of IDF calculation ('token' or 'embedding')
            batch_size (int): Batch size for processing

        Returns:
            dict: Enhanced batch output with TF-IDF weights and metadata
        """
        all_sentences = []
        mapping_jsonkey2sentidx = {}
        start_idx = 0
        sorted_keys = sorted(json_data.keys())
        
        for tmp_key in sorted_keys:
            tmp_value = json_data[tmp_key]
            if type(tmp_value[subtask]) == str:
                tmp_value[subtask] = [tmp_value[subtask]]
            sentences = tmp_value[subtask] if n_sents is None else [tmp_value[subtask][-1]]
            all_sentences.extend(sentences)
            mapping_jsonkey2sentidx[tmp_key] = (start_idx, start_idx + len(sentences))
            start_idx = start_idx + len(sentences)

        # Tokenizing all sentences (CPU)...
        # 1. Tokenize only, do not Encode. Store results on CPU.
        # encode_sentences with output_value="input_ids" is very fast.
        batch_output = self.model.encode_sentences(all_sentences, batch_size=batch_size, output_value="input_ids")
        batch_output["all_sentences"] = all_sentences
        batch_output["mapping_jsonkey2sentidx"] = mapping_jsonkey2sentidx

        if self.return_type == "fense" or not tf_idf_weighted:
            # Return directly if weighting is not needed
            return batch_output

        input_ids = batch_output["features"]["input_ids"].cpu() # CPU Tensor
        
        # 2. Calculate auxiliary statistics (Low Memory)
        word_sim, idf_sum, unique_id_map = self.fetch_word_embeddings(input_ids)
        
        # 3. Calculate TF-IDF weights (CPU)
        # Convert idf_sum to IDF vector
        n_docs = len(all_sentences)
        idf_vec = torch.log((n_docs + 1) / (idf_sum + 1)) + 1
        idf_vec = idf_vec.cpu() # (V,)
        
        # Calculating final TF-IDF weights matrix...
        # Result matrix: (N, L) float16, minimal memory usage (e.g. 50k * 64 * 2B = 6.4MB)
        tf_idf_weights = torch.ones_like(input_ids, dtype=torch.float16)
        
        word_sim_np = word_sim.numpy() # (V, V)
        idf_np = idf_vec.numpy()
        
        # Iterate to calculate weights for each sentence
        # Bottleneck is random access to word_sim_np
        
        for i in tqdm(range(len(input_ids)), desc="TF-IDF Weights"):
            row_ids = input_ids[i].numpy()
            
            valid_indices = []
            pos_in_seq = []
            
            for j, tid in enumerate(row_ids):
                if tid != 0 and tid != 101 and tid != 102 and tid in unique_id_map:
                    valid_indices.append(unique_id_map[tid])
                    pos_in_seq.append(j)
            
            if not valid_indices:
                continue
                
            sub_sim = word_sim_np[np.ix_(valid_indices, valid_indices)]
            sub_idf = idf_np[valid_indices]
            
            tf = np.sum(sub_sim**2, axis=1)
            weights = tf * sub_idf
            
            mean_val = np.mean(weights)
            if mean_val > 1e-9:
                weights = weights / mean_val
            
            current_weights = torch.tensor(weights, dtype=torch.float16)
            tf_idf_weights[i, pos_in_seq] = current_weights
            
            if len(weights) > 0:
                max_w = weights.max()
                min_w = weights.min()
                
                # CLS Token logic
                if row_ids[0] == 101:
                    # Fix: Explicitly cast to float
                    tf_idf_weights[i, 0] = float(max_w)
                    
                # SEP Token logic
                sep_idx = np.where(row_ids == 102)[0]
                if len(sep_idx) > 0:
                    # Fix: Explicitly cast to float
                    tf_idf_weights[i, sep_idx[0]] = float(min_w)
                    
        batch_output["tf_idf_weights"] = tf_idf_weights
        
        del word_sim, idf_sum, unique_id_map
        gc.collect()
        
        return batch_output
        
    def update_sentence_embeddings(
        self,
        batch_output,
        normalize_embeddings: bool = True,
        return_type: Literal["fense", "date"] = "date",
        batch_size: int = 32,
    ):
        """
        Restores TF-IDF weighting at the Input layer to ensure consistency while keeping memory low.

        This method generates sentence embeddings. If in DATE mode, it applies the 
        pre-calculated TF-IDF weights directly to the input embeddings before passing 
        them through the Transformer, matching the mathematical logic of the original version.

        Args:
            batch_output: Batch output containing TF-IDF weights and input IDs
            normalize_embeddings (bool): Whether to normalize sentence embeddings
            return_type (str): Evaluation mode ('fense' or 'date')
            batch_size (int): Batch size for processing

        Returns:
            tuple: (sentence_embeddings, penalties)
                - sentence_embeddings: Normalized sentence-level embeddings
                - penalties: Error penalty scores for each sentence
        """
        all_sentences = batch_output["all_sentences"]
        n_samples = len(all_sentences)
        
        # Pre-determine output dimension
        with torch.no_grad():
            dummy_out = self.model.encode_sentences(all_sentences[0:1], batch_size=1)
            embed_dim = dummy_out["embeddings"].shape[-1]
        
        # Result Tensor (CPU)
        final_embeddings = torch.zeros((n_samples, embed_dim), dtype=torch.float32, device="cpu")
        
        # Retrieve precomputed weights (CPU)
        tf_idf_weights = batch_output.get("tf_idf_weights", None) # (N, L)
        input_ids_all = batch_output["features"]["input_ids"]     # (N, L)
        attention_mask_all = batch_output["features"]["attention_mask"]
        
        # Ensure token_type_ids exists (Required by BERT)
        token_type_ids_all = batch_output["features"].get("token_type_ids", None)
        
        for i in tqdm(range(0, n_samples, batch_size), desc="Sent Embeddings"):
            end_i = min(i + batch_size, n_samples)
            
            # 1. Prepare Batch Data (Move to GPU)
            b_input_ids = input_ids_all[i:end_i].to(self.device)
            b_mask = attention_mask_all[i:end_i].to(self.device)
            
            batch_inputs = {
                "input_ids": b_input_ids, 
                "attention_mask": b_mask
            }
            if token_type_ids_all is not None:
                batch_inputs["token_type_ids"] = token_type_ids_all[i:end_i].to(self.device)
            
            with torch.no_grad():
                # 2. If DATE mode and weights exist: Apply weights BEFORE BERT!
                if return_type == "date" and tf_idf_weights is not None:
                    # A. Get Static Word Embeddings (Input Layer)
                    # Note: self.model.auto_model is the huggingface BertModel
                    word_embeddings = self.model.auto_model.embeddings.word_embeddings(b_input_ids)
                    
                    # B. Get weights and broadcast
                    b_weights = tf_idf_weights[i:end_i].to(self.device) # (B, L)
                    # Ensure consistent types (FP16/FP32)
                    if b_weights.dtype != word_embeddings.dtype:
                        b_weights = b_weights.to(dtype=word_embeddings.dtype)
                    
                    # (B, L, D) * (B, L, 1)
                    inputs_embeds = word_embeddings * b_weights.unsqueeze(-1)
                    
                    # C. Construct new input dict, replacing input_ids with inputs_embeds
                    # SBERT/BERT will prioritize inputs_embeds if present
                    batch_inputs["inputs_embeds"] = inputs_embeds
                    # Delete input_ids to be safe (though usually not required)
                    del batch_inputs["input_ids"]
                
                # 3. Forward Pass (BERT)
                # In DATE mode, weighted embeddings are passed -> Transformer -> Contextual Output
                # This reconstructs the mathematical logic of Version 1.
                out_features = self.model.sbert.forward(batch_inputs)
                
                # 4. Extract Sentence Embedding
                # Note: RefinedSentenceTransformers might perform truncation, but here we call sbert.forward directly.
                # We need to extract sentence_embedding.
                # If the sbert model includes a Pooling layer, out_features['sentence_embedding'] should exist.
                
                if "sentence_embedding" in out_features:
                    batch_sent_emb = out_features["sentence_embedding"]
                else:
                    # If no Pooling layer output, token_embeddings are usually (B, L, D)
                    # Perform manual Mean Pooling (masked)
                    token_embeddings = out_features["token_embeddings"]
                    input_mask_expanded = b_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    batch_sent_emb = sum_embeddings / sum_mask
                
                # 5. Store Results
                final_embeddings[i:end_i] = batch_sent_emb.cpu()
                
            del batch_inputs, out_features
            if self.device == "cuda":
                torch.cuda.empty_cache()

        # Follow-up Penalty and Reshape logic remains unchanged
        penalities = self.calculate_penalty(batch_output, batch_size=batch_size)

        mapping_jsonkey2sentidx = batch_output["mapping_jsonkey2sentidx"]
        first_key = next(iter(mapping_jsonkey2sentidx))
        n_choices_in_one_key = mapping_jsonkey2sentidx[first_key][1] - mapping_jsonkey2sentidx[first_key][0]

        n_sents, n_embs = final_embeddings.shape
        if n_sents % n_choices_in_one_key == 0:
            final_embeddings = final_embeddings.reshape(n_sents // n_choices_in_one_key, n_choices_in_one_key, n_embs)
            penalities = penalities.reshape(n_sents // n_choices_in_one_key, n_choices_in_one_key)
        else:
             logger.warning(f"Shape mismatch: {n_sents} sents vs {n_choices_in_one_key} choices. Skipping reshape.")

        if normalize_embeddings:
            final_embeddings = torch.nn.functional.normalize(final_embeddings, p=2, dim=-1)

        if self.cpu_priority and self.compute_device == "cuda":
            final_embeddings = final_embeddings.to(self.storage_device)
            penalities = penalities.to(self.storage_device)
        else:
            final_embeddings = final_embeddings.to(self.device)
            penalities = penalities.to(self.device)
            
        return final_embeddings, penalities

    def forward(
        self,
        ref_data: dict,
        val_data: dict,
        group_name: str = "content_long",
        delta: int | float = None,
        save_path: str = None,
        dataframe: pd.DataFrame = None,
        field_type: str = None,
        batch_size: int = 32,
    ):
        """
        Main forward pass for DATE evaluation.

        This method performs the complete DATE evaluation process, including:
        1. Data preprocessing and alignment
        2. Embedding generation with optional TF-IDF weighting
        3. Similarity calculation (FP32)
        4. Discrimination calculation (Optimized Batched & Vectorized)
        5. Final score computation

        Args:
            ref_data (dict): Reference data containing ground truth
            val_data (dict): Validation data containing predictions
            group_name (str): Group name from GROUP_CONFIGS (default: 'content_long')
            delta (float): Delta parameter for discrimination calculation
            save_path (str): Path to save embeddings (optional)
            dataframe (pd.DataFrame): DataFrame to store detailed results
            field_type (str): Type of field being evaluated
            batch_size (int): Batch size for processing

        Returns:
            tuple: (evaluation_results, updated_dataframe)
                - evaluation_results: Dictionary containing scores
                - updated_dataframe: Enhanced dataframe with results
        """
        # 1. Delta Setup (Strictly match DATE0.py logic)
        group_to_subtask_mapping = {
            "content_long": "long",
            "content_short": "short",
            "pure_speech": "speech",
            "mixed_speech": "speech",
            "pure_music": "music",
            "mixed_music": "music",
            "pure_sound": "sound",
            "mixed_sound": "sound",
            "environment": "environment"
        }
        subtask_for_delta = group_to_subtask_mapping.get(group_name, "long")
        
        if delta is None:
            subtask_delta_dict = self.subset_data_delta.get(subtask_for_delta, {"all": 0.2})
            if "all" in subtask_delta_dict:
                delta = subtask_delta_dict["all"]
            else:
                delta = list(subtask_delta_dict.values())[0] if subtask_delta_dict else 0.2

        # 2. Data Cleaning
        removed_keys = []
        for tmp_key in val_data:
            if tmp_key not in ref_data:
                removed_keys.append(tmp_key)
        for tmp_key in removed_keys:
            del val_data[tmp_key]

        # 3. Logging
        logger.info(f"Processing {len(ref_data)} reference items and {len(val_data)} validation items")
        logger.info(f"start processing {group_name} (subtask: {subtask_for_delta}): {len(val_data)}")

        tf_idf_weighted = True if self.return_type != "fense" else False

        # 4. Process Reference Embeddings
        logger.info(f"Processing reference data (current memory: {fetch_memory_usage()})")
        batch_output = self.update_word_embeddings(
            ref_data, subtask_for_delta, n_sents=None, tf_idf_weighted=tf_idf_weighted, idf_type="embedding", batch_size=batch_size
        )
        embeddings_ref, penalties_ref = self.update_sentence_embeddings(batch_output, return_type=self.return_type, batch_size=batch_size)

        # 5. Process Validation Embeddings
        logger.info(f"Processing predicted data (current memory: {fetch_memory_usage()})")
        batch_output_val = self.update_word_embeddings(
            val_data, subtask_for_delta, n_sents=1, tf_idf_weighted=tf_idf_weighted, idf_type="embedding", batch_size=batch_size
        )
        embeddings_val, penalties_val = self.update_sentence_embeddings(batch_output_val, return_type=self.return_type, batch_size=batch_size)
        embeddings_val = embeddings_val.squeeze(1)

        logger.info(f"Calculating metric (current memory: {fetch_memory_usage()})")
        # 6. Prepare Centroid (Ref Mean) - Optimization from V2
        if embeddings_ref.dim() == 3:
            ref_mean = embeddings_ref.mean(dim=1)
        else:
            ref_mean = embeddings_ref
        
        # Move to device for calculation
        if self.device == "cuda":
            ref_mean = ref_mean.to(self.device)
            embeddings_val = embeddings_val.to(self.device)
            penalties_val = penalties_val.to(self.device)

        # 7. Save Embeddings
        if save_path is not None:
            os.makedirs(save_path, exist_ok=True)
            save_name = "fense" if self.return_type == "fense" else "date"
            torch.save(embeddings_ref.detach().cpu(), f"{save_path}/embedding-{save_name}-{group_name}-ref.pt")
            torch.save(embeddings_val.detach().cpu(), f"{save_path}/embedding-{save_name}-{group_name}-val.pt")

        # 8. Calculate Similarity (FP32)
        emb_val_fp32 = embeddings_val.float()
        ref_mean_fp32 = ref_mean.float()
        penalties_fp32 = penalties_val.float().squeeze()

        # Diagonal Similarity: Self-Similarity (Vectorized)
        diag_sim = (emb_val_fp32 * ref_mean_fp32).sum(dim=1) * penalties_fp32
        
        # Keep similarity as a vector for later per-sample DATE calculation
        similarity_vec = diag_sim 
        similarity_per_sample = similarity_vec.detach().cpu().numpy()

        if self.return_type == "fense":
            output = {"field_type": field_type, "similarity": round(similarity_vec.mean().item(), 4)}
            if dataframe is not None:
                sorted_keys = sorted(list(ref_data.keys()))
                for tmp_idx, tmp_key in enumerate(sorted_keys):
                    dataframe.loc[len(dataframe)] = [tmp_key, field_type, 0, similarity_per_sample[tmp_idx], None, None]
            return output, dataframe

        logger.info(f"Calculating metric (part-2) (current memory: {fetch_memory_usage()})")
        # --- DISCRIMINATION CALCULATION ---
        n_samples = len(ref_data)
        rank = torch.zeros(n_samples, device=self.device, dtype=torch.float32)
        calc_batch_size = 1024 
        
        # Pre-prepare tensors
        diag_sim_device = diag_sim.to(self.device)
        ref_mean_t = ref_mean.float().t() # (Dim, N_samples)
        
        # Batched processing over Candidates
        for i in range(0, n_samples, calc_batch_size):
            end_i = min(i + calc_batch_size, n_samples)
            
            # 1. Calculate Row of Similarity Matrix: Batch_Val vs All_Ref_Means
            batch_val = embeddings_val[i:end_i].float()
            sim_matrix_batch = torch.mm(batch_val, ref_mean_t)
            
            # 2. Apply Penalty (Candidate-wise)
            batch_penalties = penalties_val[i:end_i].float()
            sim_matrix_batch = sim_matrix_batch * batch_penalties
            
            # 3. Calculate Rank
            batch_self_scores = diag_sim_device[i:end_i].unsqueeze(1)
            
            threshold_ge = batch_self_scores + delta / 2
            threshold_lower = batch_self_scores - delta / 2
            
            count_ge = (sim_matrix_batch > threshold_ge).sum(dim=1).float()
            is_le_upper = sim_matrix_batch <= threshold_ge
            is_ge_lower = sim_matrix_batch >= threshold_lower
            count_eq = (is_le_upper & is_ge_lower).sum(dim=1).float()
            
            # Rank formula matching DATE0 logic
            batch_rank = 1 - (count_ge + count_eq) / n_samples
            rank[i:end_i] = batch_rank
            
            del sim_matrix_batch, batch_val, batch_penalties
            
        if self.device == "cuda":
            torch.cuda.empty_cache()

        # --- KEY FIX HERE: LOGIC ALIGNMENT WITH VERSION 1 ---
        # Instead of calculating DATE on the scalar means (V2 logic),
        # we calculate DATE on the vectors first (V1 logic).
        
        # Ensure discrimination rank is on the same device
        rank_vec = rank.to(similarity_vec.device)
        
        # Calculate Per-Sample DATE Score
        # Formula: 2 * Sim * Disc / (Sim + Disc)
        date_vec = 2 * similarity_vec * rank_vec / (similarity_vec + rank_vec + 1e-8)
        
        # Now take the mean of the vector (replicates V1 behavior)
        similarity_score = similarity_vec.mean().item()
        discrimination_score = rank_vec.mean().item()
        DATE_score = date_vec.mean().item()

        output = {
            "field_type": field_type,
            "delta": delta / 2,
            "similarity": round(similarity_score, 4),
            "discrimination": round(discrimination_score, 4),
            "date": round(DATE_score, 4), # Corrected logic
        }
        
        if dataframe is not None:
            sorted_keys = sorted(list(ref_data.keys()))
            rank_cpu = rank.detach().cpu().numpy()
            date_cpu = date_vec.detach().cpu().numpy() # Use the vector computed above
            
            for tmp_idx, tmp_key in enumerate(sorted_keys):
                dataframe.loc[len(dataframe)] = [
                    tmp_key,
                    field_type,
                    delta / 2,
                    similarity_per_sample[tmp_idx],
                    rank_cpu[tmp_idx],
                    date_cpu[tmp_idx],
                ]

        del ref_mean, embeddings_val, penalties_val, diag_sim, rank, date_vec, similarity_vec
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()

        return output, dataframe

class DATEEvaluator:
    """
    DATE (Discriminability based Audio Task Evaluation) evaluator with FENSE-compatible interface.

    This class provides a FENSE-compatible interface for the DATE evaluation metric,
    allowing seamless integration with existing evaluation pipelines. It supports
    both FENSE and DATE evaluation modes through the return_type parameter.

    Key Features:
    - FENSE-compatible API for easy integration
    - Support for both corpus-level and sentence-level evaluation
    - Batch processing for efficiency
    - Configurable evaluation modes (FENSE or DATE)

    Usage:
        evaluator = DATEEvaluator(return_type='date')
        score = evaluator.corpus_score(candidates, references)
    """

    def __init__(
        self,
        batch_size=32,
        device=None,
        sbert_model="paraphrase-TinyBERT-L6-v2",
        echecker_model="echecker_clotho_audiocaps_base",
        error_threshold=0.9,
        penalty=0.9,
        use_proxy=False,
        proxies=None,
        is_clamp_neg_similarity=False,
        return_type="date",
        cpu_priority=True,  # Add CPU priority parameter
    ):
        """
        Initialize DATEEvaluator with FENSE-compatible interface.

        Args:
            batch_size (int): Batch size for processing
            device (str): Device to run models on ('cuda' or 'cpu')
            sbert_model (str): Sentence transformer model name or path
            echecker_model (str): Error checker model name or path
            error_threshold (float): Threshold for error detection
            penalty (float): Penalty factor for detected errors
            use_proxy (bool): Whether to use proxy for model downloads
            proxies (str): Proxy configuration
            is_clamp_neg_similarity (bool): Whether to clamp negative similarities
            return_type (str): Evaluation mode ('fense' or 'date')
            cpu_priority (bool): Whether to prioritize CPU memory usage over GPU speed
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.batch_size = batch_size
        
        # Initialize DATE model with CPU priority option
        self.date_model = DATE(
            sbert_name_or_path=sbert_model,
            echecker_name_or_path=echecker_model,
            device=self.device,
            error_threshold=error_threshold,
            penalty=penalty,
            use_proxy=use_proxy,
            proxies=proxies,
            is_clamp_neg_similarity=is_clamp_neg_similarity,
            return_type=return_type,
            cpu_priority=cpu_priority,  # Pass CPU priority parameter
        )

    def corpus_score(self, cands, list_refs, agg_score="mean", save_path=None, save_dataframe_path=None, sample_keys=None, group_name="content_long"):
        """
        Calculate corpus-level DATE score with FENSE-compatible interface.

        This method evaluates a corpus of candidate sentences against their corresponding
        reference sentences using the DATE metric. It provides the same interface as
        FENSE's corpus_score method for easy integration.

        Args:
            cands (list): List of candidate sentences to evaluate
            list_refs (list): List of reference sentence lists (each element is a list of references)
            agg_score (str): Aggregation method for scores ('none', 'mean', 'max')
                - 'none': Return individual scores for each candidate
                - 'mean': Return mean score across all candidates
                - 'max': Return maximum score across all candidates
            save_path (str): Path to save embeddings (optional)
            save_dataframe_path (str): Path to save dataframe results (optional)
            sample_keys (list): List of sample keys to preserve in dataframe (optional)
            group_name (str): Group name from GROUP_CONFIGS (default: "content_long")

        Returns:
            float or list: DATE score(s) depending on agg_score parameter
                - If agg_score='mean' or 'max': single float score
                - If agg_score='none': list of scores for each candidate
        """
        assert len(cands) == len(list_refs), "Number of candidates must match number of reference lists"
        assert agg_score in {"none", "mean", "max"}, "agg_score must be 'none', 'mean', or 'max'"

        # Extract subtask from group_name for data processing
        group_to_subtask_mapping = {
            "content_long": "long",
            "content_short": "short",
            "pure_speech": "speech",
            "mixed_speech": "speech",
            "pure_music": "music",
            "mixed_music": "music",
            "pure_sound": "sound",
            "mixed_sound": "sound",
            "environment": "environment"
        }
        subtask_for_data = group_to_subtask_mapping.get(group_name, "long")
        
        # Convert input format to DATE model's expected format
        ref_data = {}
        val_data = {}

        for i, (cand, refs) in enumerate(zip(cands, list_refs)):
            # Use provided sample_keys if available, otherwise use default ref_{i}
            if sample_keys is not None and i < len(sample_keys):
                key = sample_keys[i]
            else:
                key = f"ref_{i}"
            
            ref_data[key] = {subtask_for_data: refs}
            val_data[key] = {subtask_for_data: [cand]}
        
        # Create dataframe for storing detailed results if save_dataframe_path is provided
        dataframe = None
        if save_dataframe_path is not None:
            dataframe = pd.DataFrame(columns=["sample_id", "field_type", "delta", "similarity", "discrimination", "date"])

        # Run DATE evaluation
        output, dataframe = self.date_model(
            ref_data=ref_data,
            val_data=val_data,
            group_name=group_name,
            save_path=save_path,
            dataframe=dataframe,
            field_type=subtask_for_data,
            # delta=0.02,  # Default delta value for discrimination calculation
        )

        # Save dataframe if path is provided
        if save_dataframe_path is not None and dataframe is not None:
            os.makedirs(os.path.dirname(save_dataframe_path), exist_ok=True)
            dataframe.to_csv(save_dataframe_path, index=False)
            logger.info(f"Dataframe results saved to: {save_dataframe_path}")

        # Select appropriate score based on evaluation mode
        if self.date_model.return_type == "fense":
            score_key = "similarity"
        else:
            score_key = "date"

        # Apply aggregation method
        if agg_score == "mean":
            return output[score_key]
        elif agg_score == "max":
            return output[score_key]  # For corpus-level score, max equals the mean score
        else:
            return [output[score_key]] * len(cands)  # Return list of same scores for each candidate

    def sentence_score(self, cand, refs, return_error_prob=False, save_path=None, save_dataframe_path=None, subtask="text"):
        """
        Calculate sentence-level DATE score with FENSE-compatible interface.

        This method evaluates a single candidate sentence against a list of reference
        sentences using the DATE metric. It provides the same interface as FENSE's
        sentence_score method for easy integration.

        Args:
            cand (str): Candidate sentence to evaluate
            refs (list): List of reference sentences
            return_error_prob (bool): Whether to return error probability (legacy parameter)
                Note: DATE doesn't provide error probability, so this returns None
            save_path (str): Path to save embeddings (optional)
            save_dataframe_path (str): Path to save dataframe results (optional)
            subtask (str): Field name for the data (default: "text")

        Returns:
            float or tuple: DATE score, or tuple if return_error_prob=True
                - If return_error_prob=False: single float score
                - If return_error_prob=True: tuple of (score, None, score)
        """
        # Convert input format to DATE model's expected format
        ref_data = {"ref_0": {subtask: refs}}
        val_data = {"ref_0": {subtask: [cand]}}

        # Create dataframe for storing detailed results if save_dataframe_path is provided
        dataframe = None
        if save_dataframe_path is not None:
            dataframe = pd.DataFrame(columns=["sample_id", "field_type", "delta", "similarity", "discrimination", "date"])

        # Run DATE evaluation
        output, dataframe = self.date_model(
            ref_data=ref_data,
            val_data=val_data,
            subtask=subtask,
            save_path=save_path,
            dataframe=dataframe,
            field_type=subtask,
            # delta=0.02,  # Default delta value for discrimination calculation
        )

        # Save dataframe if path is provided
        if save_dataframe_path is not None and dataframe is not None:
            os.makedirs(os.path.dirname(save_dataframe_path), exist_ok=True)
            dataframe.to_csv(save_dataframe_path, index=False)
            logger.info(f"Dataframe results saved to: {save_dataframe_path}")

        # Select appropriate score based on evaluation mode
        if self.date_model.return_type == "fense":
            score_key = "similarity"
        else:
            score_key = "date"

        if return_error_prob:
            # DATE doesn't provide error probability, return score with None for error_prob
            return output[score_key], None, output[score_key]
        else:
            return output[score_key]

    def evaluate(self, predictions, references, subtask="text", save_path=None, save_dataframe_path=None):
        """
        Evaluate predictions against references using the DATE metric.

        This method provides a comprehensive evaluation interface that can handle
        both single references and multiple references per prediction. It returns
        detailed scores including similarity, discrimination, and the final DATE score.

        Args:
            predictions (list): List of prediction strings to evaluate
            references (list): List of reference strings or list of reference string lists
                - If each element is a string: single reference per prediction
                - If each element is a list: multiple references per prediction
            subtask (str): Field name for the data (default: "text")
            save_path (str): Path to save embeddings (optional)
            save_dataframe_path (str): Path to save dataframe results (optional)

        Returns:
            dict: Dictionary containing evaluation scores
                - For FENSE mode: {'fense': score, 'similarity': score}
                - For DATE mode: {'date': score, 'similarity': score, 'discrimination': score}
        """
        # Ensure references is a list of lists for consistent processing
        if isinstance(references[0], str):
            references = [[ref] for ref in references]

        # Convert input format to DATE model's expected format
        ref_data = {}
        val_data = {}

        for i, (pred, refs) in enumerate(zip(predictions, references)):
            ref_data[f"ref_{i}"] = {subtask: refs}
            val_data[f"ref_{i}"] = {subtask: [pred]}

        # Create dataframe for storing detailed results if save_dataframe_path is provided
        dataframe = None
        if save_dataframe_path is not None:
            dataframe = pd.DataFrame(columns=["sample_id", "field_type", "delta", "similarity", "discrimination", "date"])

        # Run DATE evaluation
        output, dataframe = self.date_model(
            ref_data=ref_data,
            val_data=val_data,
            subtask=subtask,
            save_path=save_path,
            dataframe=dataframe,
            field_type=subtask,
            # delta=0.02,  # Default delta value for discrimination calculation
        )

        # Save dataframe if path is provided
        if save_dataframe_path is not None and dataframe is not None:
            os.makedirs(os.path.dirname(save_dataframe_path), exist_ok=True)
            dataframe.to_csv(save_dataframe_path, index=False)
            logger.info(f"Dataframe results saved to: {save_dataframe_path}")

        # Return appropriate scores based on evaluation mode
        if self.date_model.return_type == "fense":
            return {"fense": output["similarity"], "similarity": output["similarity"]}
        else:
            return {
                "date": output["date"],
                "similarity": output["similarity"],
                "discrimination": output["discrimination"],
            }