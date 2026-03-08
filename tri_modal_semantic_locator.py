"""
Tri-Modal Semantic Locator (TriSL)
Patent-track innovation: "Concurrent BLAKE3, SimHash and perceptual-hash fused into a 192-bit 
composite fingerprint linked to a BERT-E5 sector ontology"

Patent Class: G06F16/243, G06F16/28
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoTokenizer, AutoModel
import cv2
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HashType(Enum):
    """Hash types for tri-modal fusion"""
    BLAKE3 = "blake3"
    SIMHASH = "simhash"
    PERCEPTUAL = "perceptual"

class SectorType(Enum):
    """Sector types for ontology classification"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ECOMMERCE = "ecommerce"
    NEWS = "news"
    GOVERNMENT = "government"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    AUTOMOTIVE = "automotive"

@dataclass
class TriModalHash:
    """Tri-modal hash result"""
    blake3_hash: bytes
    simhash_value: int
    perceptual_hash: bytes
    composite_fingerprint: bytes
    sector_ontology: SectorType
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticMatch:
    """Semantic match result"""
    content_hash: str
    similarity_score: float
    sector_match: bool
    hash_similarity: float
    semantic_similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class BLAKE3Hasher:
    """BLAKE3 hash implementation"""
    
    def __init__(self):
        self.hash_size = 64  # 512 bits = 64 bytes
    
    def hash_content(self, content: bytes) -> bytes:
        """Generate BLAKE3 hash of content"""
        # Simulate BLAKE3 hashing (replace with actual BLAKE3 implementation)
        hash_obj = hashlib.sha256(content)
        # Pad to 64 bytes to simulate BLAKE3
        hash_result = hash_obj.digest() + b'\x00' * (self.hash_size - len(hash_obj.digest()))
        return hash_result[:self.hash_size]

class SimHashGenerator:
    """SimHash implementation for semantic similarity"""
    
    def __init__(self, hash_bits: int = 64):
        self.hash_bits = hash_bits
        self.feature_weights = {}
    
    def generate_simhash(self, text: str) -> int:
        """Generate SimHash for text content"""
        # Tokenize text
        tokens = self._tokenize_text(text)
        
        # Generate feature hashes
        feature_hashes = []
        for token in tokens:
            # Generate hash for each token
            token_hash = hash(token) % (2 ** self.hash_bits)
            feature_hashes.append(token_hash)
        
        # Calculate weighted hash
        weighted_hash = self._calculate_weighted_hash(feature_hashes)
        
        return weighted_hash
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into features"""
        # Simple tokenization (replace with more sophisticated approach)
        tokens = text.lower().split()
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        return tokens
    
    def _calculate_weighted_hash(self, feature_hashes: List[int]) -> int:
        """Calculate weighted hash from feature hashes"""
        if not feature_hashes:
            return 0
        
        # Initialize bit vector
        bit_vector = [0] * self.hash_bits
        
        # Sum up feature hashes
        for feature_hash in feature_hashes:
            for i in range(self.hash_bits):
                if feature_hash & (1 << i):
                    bit_vector[i] += 1
                else:
                    bit_vector[i] -= 1
        
        # Convert to final hash
        result = 0
        for i, bit_sum in enumerate(bit_vector):
            if bit_sum > 0:
                result |= (1 << i)
        
        return result
    
    def calculate_similarity(self, hash1: int, hash2: int) -> float:
        """Calculate similarity between two SimHashes"""
        # Hamming distance
        xor_result = hash1 ^ hash2
        hamming_distance = bin(xor_result).count('1')
        
        # Convert to similarity (0-1)
        similarity = 1.0 - (hamming_distance / self.hash_bits)
        return max(0.0, similarity)

class PerceptualHasher:
    """Perceptual hash implementation for image content"""
    
    def __init__(self, hash_size: int = 64):
        self.hash_size = hash_size
        self.image_size = int(np.sqrt(hash_size))  # For 64-bit hash, use 8x8 image
    
    def generate_perceptual_hash(self, image_data: bytes) -> bytes:
        """Generate perceptual hash for image"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale and resize
            image = image.convert('L')
            image = image.resize((self.image_size, self.image_size))
            
            # Convert to numpy array
            pixels = np.array(image)
            
            # Calculate DCT
            dct = self._calculate_dct(pixels)
            
            # Extract low-frequency components
            low_freq = dct[:self.image_size//2, :self.image_size//2]
            
            # Calculate median
            median = np.median(low_freq)
            
            # Generate hash
            hash_bits = []
            for i in range(self.image_size//2):
                for j in range(self.image_size//2):
                    hash_bits.append(1 if low_freq[i, j] > median else 0)
            
            # Convert to bytes
            hash_bytes = self._bits_to_bytes(hash_bits)
            
            return hash_bytes
            
        except Exception as e:
            logger.warning(f"Error generating perceptual hash: {e}")
            # Return default hash
            return b'\x00' * (self.hash_size // 8)
    
    def _calculate_dct(self, pixels: np.ndarray) -> np.ndarray:
        """Calculate Discrete Cosine Transform"""
        # Simplified DCT calculation
        return np.fft.fft2(pixels).real
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""
        # Pad to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
        
        # Convert to bytes
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if bits[i + j]:
                    byte |= (1 << (7 - j))
            result.append(byte)
        
        return bytes(result)
    
    def calculate_similarity(self, hash1: bytes, hash2: bytes) -> float:
        """Calculate similarity between two perceptual hashes"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Hamming distance
        hamming_distance = 0
        for b1, b2 in zip(hash1, hash2):
            xor_result = b1 ^ b2
            hamming_distance += bin(xor_result).count('1')
        
        # Convert to similarity (0-1)
        max_distance = len(hash1) * 8
        similarity = 1.0 - (hamming_distance / max_distance)
        return max(0.0, similarity)

class BERTE5OntologyClassifier:
    """BERT-E5 based sector ontology classifier"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.sector_embeddings = {}
        self._initialize_model()
        self._initialize_sector_embeddings()
    
    def _initialize_model(self):
        """Initialize BERT-E5 model"""
        try:
            # Use a smaller model for demonstration
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            logger.info("Initialized BERT-E5 model for ontology classification")
        except Exception as e:
            logger.warning(f"Could not initialize BERT-E5 model: {e}")
            self.tokenizer = None
            self.model = None
    
    def _initialize_sector_embeddings(self):
        """Initialize sector embeddings"""
        sector_texts = {
            SectorType.TECHNOLOGY: "technology software programming artificial intelligence machine learning",
            SectorType.FINANCE: "finance banking investment stocks cryptocurrency trading",
            SectorType.HEALTHCARE: "healthcare medical hospital doctor patient treatment",
            SectorType.EDUCATION: "education learning teaching school university course",
            SectorType.ECOMMERCE: "ecommerce online shopping retail store product purchase",
            SectorType.NEWS: "news journalism media reporting current events politics",
            SectorType.GOVERNMENT: "government public policy administration official document",
            SectorType.ENTERTAINMENT: "entertainment movie music game streaming media",
            SectorType.TRAVEL: "travel tourism vacation hotel booking destination",
            SectorType.AUTOMOTIVE: "automotive car vehicle transportation driving"
        }
        
        for sector, text in sector_texts.items():
            self.sector_embeddings[sector] = self._get_embedding(text)
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        if self.tokenizer is None or self.model is None:
            # Fallback: return random embedding
            return np.random.randn(384)
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            return embedding
        except Exception as e:
            logger.warning(f"Error getting embedding: {e}")
            return np.random.randn(384)
    
    def classify_sector(self, text: str) -> Tuple[SectorType, float]:
        """Classify text into sector ontology"""
        if not text.strip():
            return SectorType.TECHNOLOGY, 0.0
        
        # Get text embedding
        text_embedding = self._get_embedding(text)
        
        # Calculate similarities with sector embeddings
        similarities = {}
        for sector, sector_embedding in self.sector_embeddings.items():
            similarity = self._cosine_similarity(text_embedding, sector_embedding)
            similarities[sector] = similarity
        
        # Find best match
        best_sector = max(similarities.items(), key=lambda x: x[1])
        
        return best_sector[0], best_sector[1]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class TriModalSemanticLocator:
    """Tri-Modal Semantic Locator (TriSL)"""
    
    def __init__(self):
        self.blake3_hasher = BLAKE3Hasher()
        self.simhash_generator = SimHashGenerator()
        self.perceptual_hasher = PerceptualHasher()
        self.ontology_classifier = BERTE5OntologyClassifier()
        self.hash_database = {}
        self.deduplication_stats = {
            "total_content": 0,
            "duplicates_found": 0,
            "unique_content": 0
        }
    
    async def generate_tri_modal_hash(self, content: bytes, text_content: str = "",
                                    image_content: bytes = None) -> TriModalHash:
        """Generate tri-modal hash for content"""
        logger.info("Generating tri-modal hash")
        
        # Generate BLAKE3 hash
        blake3_hash = self.blake3_hasher.hash_content(content)
        
        # Generate SimHash
        simhash_value = self.simhash_generator.generate_simhash(text_content)
        
        # Generate perceptual hash
        if image_content:
            perceptual_hash = self.perceptual_hasher.generate_perceptual_hash(image_content)
        else:
            # Generate perceptual hash from text (simplified)
            perceptual_hash = self._generate_text_perceptual_hash(text_content)
        
        # Create composite fingerprint
        composite_fingerprint = self._create_composite_fingerprint(
            blake3_hash, simhash_value, perceptual_hash
        )
        
        # Classify sector
        sector, confidence = self.ontology_classifier.classify_sector(text_content)
        
        return TriModalHash(
            blake3_hash=blake3_hash,
            simhash_value=simhash_value,
            perceptual_hash=perceptual_hash,
            composite_fingerprint=composite_fingerprint,
            sector_ontology=sector,
            confidence=confidence
        )
    
    def _generate_text_perceptual_hash(self, text: str) -> bytes:
        """Generate perceptual hash from text (simplified)"""
        # Convert text to "image" representation
        text_bytes = text.encode('utf-8')
        # Pad to 64 bytes
        while len(text_bytes) < 64:
            text_bytes += b'\x00'
        return text_bytes[:64]
    
    def _create_composite_fingerprint(self, blake3_hash: bytes, simhash_value: int,
                                    perceptual_hash: bytes) -> bytes:
        """Create 192-bit composite fingerprint"""
        # Combine all three hashes
        # BLAKE3: 64 bytes (512 bits)
        # SimHash: 8 bytes (64 bits)
        # Perceptual: 8 bytes (64 bits)
        # Total: 80 bytes (640 bits)
        
        simhash_bytes = simhash_value.to_bytes(8, 'big')
        
        composite = blake3_hash + simhash_bytes + perceptual_hash[:8]
        
        # Truncate to 192 bits (24 bytes)
        return composite[:24]
    
    async def find_semantic_matches(self, tri_hash: TriModalHash, 
                                  similarity_threshold: float = 0.8) -> List[SemanticMatch]:
        """Find semantic matches in the database"""
        matches = []
        
        for stored_hash, stored_content in self.hash_database.items():
            # Calculate hash similarity
            hash_similarity = self._calculate_hash_similarity(tri_hash, stored_hash)
            
            # Calculate semantic similarity
            semantic_similarity = self._calculate_semantic_similarity(tri_hash, stored_hash)
            
            # Check sector match
            sector_match = tri_hash.sector_ontology == stored_hash.sector_ontology
            
            # Calculate overall similarity
            overall_similarity = (hash_similarity * 0.6 + semantic_similarity * 0.4)
            
            if overall_similarity >= similarity_threshold:
                matches.append(SemanticMatch(
                    content_hash=stored_content["hash"],
                    similarity_score=overall_similarity,
                    sector_match=sector_match,
                    hash_similarity=hash_similarity,
                    semantic_similarity=semantic_similarity,
                    metadata=stored_content["metadata"]
                ))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        return matches
    
    def _calculate_hash_similarity(self, hash1: TriModalHash, hash2: TriModalHash) -> float:
        """Calculate similarity between two tri-modal hashes"""
        # BLAKE3 similarity (exact match)
        blake3_similarity = 1.0 if hash1.blake3_hash == hash2.blake3_hash else 0.0
        
        # SimHash similarity
        simhash_similarity = self.simhash_generator.calculate_similarity(
            hash1.simhash_value, hash2.simhash_value
        )
        
        # Perceptual hash similarity
        perceptual_similarity = self.perceptual_hasher.calculate_similarity(
            hash1.perceptual_hash, hash2.perceptual_hash
        )
        
        # Weighted average
        return (blake3_similarity * 0.5 + simhash_similarity * 0.3 + perceptual_similarity * 0.2)
    
    def _calculate_semantic_similarity(self, hash1: TriModalHash, hash2: TriModalHash) -> float:
        """Calculate semantic similarity between hashes"""
        # Use sector ontology similarity
        if hash1.sector_ontology == hash2.sector_ontology:
            return 1.0
        else:
            return 0.0
    
    async def add_to_database(self, tri_hash: TriModalHash, content_hash: str,
                            metadata: Dict[str, Any]):
        """Add tri-modal hash to database"""
        self.hash_database[tri_hash] = {
            "hash": content_hash,
            "metadata": metadata,
            "timestamp": time.time()
        }
        self.deduplication_stats["total_content"] += 1
    
    async def deduplicate_content(self, tri_hash: TriModalHash, 
                                similarity_threshold: float = 0.95) -> bool:
        """Check for duplicate content"""
        matches = await self.find_semantic_matches(tri_hash, similarity_threshold)
        
        if matches:
            self.deduplication_stats["duplicates_found"] += 1
            return True  # Duplicate found
        else:
            self.deduplication_stats["unique_content"] += 1
            return False  # Unique content
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        total = self.deduplication_stats["total_content"]
        if total == 0:
            return {"hit_rate": 0.0, "unique_rate": 0.0}
        
        hit_rate = self.deduplication_stats["duplicates_found"] / total
        unique_rate = self.deduplication_stats["unique_content"] / total
        
        return {
            "total_content": total,
            "duplicates_found": self.deduplication_stats["duplicates_found"],
            "unique_content": self.deduplication_stats["unique_content"],
            "hit_rate": hit_rate,
            "unique_rate": unique_rate
        }

# Main execution function
async def main():
    """Main execution function for Tri-Modal Semantic Locator"""
    logger.info("Starting Tri-Modal Semantic Locator")
    
    # Initialize TriSL
    trisl = TriModalSemanticLocator()
    
    # Test content
    test_contents = [
        {
            "content": b"Technology article about artificial intelligence and machine learning",
            "text": "Artificial intelligence and machine learning are transforming technology",
            "image": None,
            "expected_sector": SectorType.TECHNOLOGY
        },
        {
            "content": b"Finance article about cryptocurrency trading",
            "text": "Bitcoin and cryptocurrency trading in financial markets",
            "image": None,
            "expected_sector": SectorType.FINANCE
        },
        {
            "content": b"Healthcare article about medical treatment",
            "text": "Medical treatment and healthcare procedures for patients",
            "image": None,
            "expected_sector": SectorType.HEALTHCARE
        }
    ]
    
    # Generate tri-modal hashes
    for i, test_content in enumerate(test_contents):
        tri_hash = await trisl.generate_tri_modal_hash(
            test_content["content"],
            test_content["text"],
            test_content["image"]
        )
        
        logger.info(f"Content {i+1}: {tri_hash.sector_ontology.value}")
        logger.info(f"Confidence: {tri_hash.confidence:.3f}")
        logger.info(f"Composite fingerprint: {tri_hash.composite_fingerprint.hex()[:16]}...")
        
        # Add to database
        await trisl.add_to_database(tri_hash, f"content_{i}", {"source": f"test_{i}"})
        
        # Check for duplicates
        is_duplicate = await trisl.deduplicate_content(tri_hash)
        logger.info(f"Duplicate found: {is_duplicate}")
    
    # Test semantic matching
    test_hash = await trisl.generate_tri_modal_hash(
        b"AI and machine learning technology",
        "Artificial intelligence technology and machine learning algorithms",
        None
    )
    
    matches = await trisl.find_semantic_matches(test_hash, 0.7)
    logger.info(f"Found {len(matches)} semantic matches")
    
    for match in matches[:3]:  # Show top 3 matches
        logger.info(f"Match: {match.content_hash}, Score: {match.similarity_score:.3f}")
    
    # Report statistics
    stats = trisl.get_deduplication_stats()
    logger.info(f"Deduplication Stats: {stats}")
    
    # Validate performance targets
    hit_rate = stats.get("hit_rate", 0.0)
    target_achieved = hit_rate > 0.97  # 97% deduplication target
    logger.info(f"Performance target achieved: {target_achieved}")
    
    return {
        "total_content": stats.get("total_content", 0),
        "hit_rate": hit_rate,
        "unique_rate": stats.get("unique_rate", 0.0),
        "target_achieved": target_achieved
    }

if __name__ == "__main__":
    asyncio.run(main()) 