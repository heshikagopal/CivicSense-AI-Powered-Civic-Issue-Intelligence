"""
Training Script for YOLO11 Civic Issue Detection
Fine-tunes YOLO11n on the CivicSense multi-category dataset.
Supports local execution and outputs Google Colab workflow config.
"""
import os
import sys
import yaml
from pathlib import Path

def train_civic_model(
    data_yaml="ml/configs/classes.yaml",
    args_yaml="ml/configs/training_args.yaml",
    weights="yolo11n.pt"
):
    try:
        from ultralytics import YOLO
        import torch
    except ImportError:
        print("[ML Training] Error: ultralytics is required for model training.")
        print("To train on GPU via Google Colab, see ml/notebooks/CivicSense_YOLO11_Training.ipynb")
        return False

    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[ML Training] Initializing YOLO11 fine-tuning on device: {device}")

    # Load base model
    model = YOLO(weights)

    # Train
    results = model.train(
        data=data_yaml,
        epochs=30,
        imgsz=640,
        batch=16 if device != "cpu" else 4,
        device=device,
        project="ml/weights",
        name="civicsense_yolo11",
        exist_ok=True
    )
    print(f"[ML Training] Training completed. Best checkpoint saved to ml/weights/civicsense_yolo11/weights/best.pt")
    return True

if __name__ == "__main__":
    train_civic_model()
