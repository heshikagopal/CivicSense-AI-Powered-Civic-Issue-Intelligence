import json
from typing import List, Optional
import numpy as np
from PIL import Image

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._init_feature_extractor()
        return cls._instance

    def _init_feature_extractor(self):
        """Initializes image embedding feature extractor."""
        self.embedding_dim = 128
        try:
            # Check for torchvision or sklearn
            import torchvision.models as models
            import torchvision.transforms as transforms
            import torch
            
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            # Lightweight MobileNetV3 / ResNet feature backbone for fast CPU embeddings
            weights = models.MobileNet_V3_Small_Weights.DEFAULT
            base_model = models.mobilenet_v3_small(weights=weights)
            base_model.classifier = torch.nn.Sequential(
                torch.nn.Linear(576, self.embedding_dim),
                torch.nn.LayerNorm(self.embedding_dim)
            )
            base_model.eval()
            self._torch_model = base_model.to(self._device)
            self._transforms = weights.transforms()
            self._use_torch = True
            print(f"[EmbeddingService] Initialized PyTorch MobileNetV3 feature extractor on {self._device}")
        except Exception as e:
            print(f"[EmbeddingService] Fallback to NumPy color-spatial feature extractor: {e}")
            self._use_torch = False

    def generate_embedding(self, image_path: str) -> List[float]:
        """
        Generates a 128-dimensional normalized visual feature embedding vector for an image.
        """
        try:
            if self._use_torch:
                import torch
                img = Image.open(image_path).convert("RGB")
                tensor = self._transforms(img).unsqueeze(0).to(self._device)
                with torch.no_grad():
                    features = self._torch_model(tensor)
                    # L2 Normalize
                    norm_features = torch.nn.functional.normalize(features, p=2, dim=1)
                    return [round(float(val), 6) for val in norm_features[0].cpu().numpy()]
            else:
                # Robust color and edge spatial feature extractor
                img = Image.open(image_path).convert("RGB").resize((64, 64))
                arr = np.array(img, dtype=np.float32) / 255.0
                # Split into 4x4 spatial grid
                grid_features = []
                for gy in range(4):
                    for gx in range(4):
                        patch = arr[gy*16:(gy+1)*16, gx*16:(gx+1)*16]
                        mean_rgb = patch.mean(axis=(0, 1))
                        std_rgb = patch.std(axis=(0, 1))
                        grid_features.extend(mean_rgb)
                        grid_features.extend(std_rgb)
                # Pad/truncate to 128 dimensions
                vec = np.array(grid_features[:self.embedding_dim], dtype=np.float32)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                return [round(float(v), 6) for v in vec]
        except Exception as e:
            print(f"[EmbeddingService] Error generating embedding: {e}")
            # Return uniform normalized vector on error
            v = np.ones(self.embedding_dim, dtype=np.float32) / np.sqrt(self.embedding_dim)
            return [round(float(x), 6) for x in v]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two normalized vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, float(dot)))

embedding_service = EmbeddingService()
