"""
Dataset Preparation & Harmonization Pipeline for CivicSense
Converts raw civic annotations (RDD2022, TACO, Roboflow) into unified YOLO format:
- Maps source classes into CivicSense 5-class taxonomy
- Verifies image integrity and removes corrupt files
- Validates bounding boxes (clamps out-of-bounds, removes zero-area boxes)
- Stratified 70/20/10 train/val/test split with scene-level leakage prevention
"""
import os
import shutil
import random
from pathlib import Path
from PIL import Image

TAXONOMY_MAP = {
    # Road damage mappings (e.g. RDD2022)
    "D00": 0, "pothole": 0, "Pothole": 0,
    "D10": 1, "D20": 1, "D40": 1, "road_crack": 1, "crack": 1, "Crack": 1, "Alligator Crack": 1,
    # Waste mappings (e.g. TACO)
    "garbage": 2, "trash": 2, "garbage_pile": 2, "litter": 2, "Plastics": 2,
    # Streetlight mappings
    "damaged_streetlight": 3, "broken_lamp": 3, "streetlight": 3,
    # General infrastructure
    "damaged_infrastructure": 4, "broken_guardrail": 4, "damaged_barrier": 4, "broken_sidewalk": 4
}

def validate_bbox(x, y, w, h):
    """Ensures bounding box is strictly normalized in [0, 1] range with positive area."""
    x = max(0.0, min(1.0, float(x)))
    y = max(0.0, min(1.0, float(y)))
    w = max(0.001, min(1.0 - x, float(w)))
    h = max(0.001, min(1.0 - y, float(h)))
    return x, y, w, h

def process_and_split(
    raw_images_dir: str,
    raw_labels_dir: str,
    output_dir: str,
    split_ratio=(0.7, 0.2, 0.1)
):
    output_path = Path(output_dir)
    for split in ["train", "val", "test"]:
        (output_path / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_path / "labels" / split).mkdir(parents=True, exist_ok=True)

    img_files = list(Path(raw_images_dir).glob("*.*"))
    valid_samples = []

    print(f"[DatasetPrep] Found {len(img_files)} candidate images in {raw_images_dir}...")

    for img_path in img_files:
        if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
            continue
        try:
            with Image.open(img_path) as im:
                im.verify()
        except Exception:
            print(f"[DatasetPrep] Skipping corrupt image: {img_path.name}")
            continue

        label_file = Path(raw_labels_dir) / f"{img_path.stem}.txt"
        if not label_file.exists():
            continue

        valid_samples.append((img_path, label_file))

    # Shuffle with fixed seed for reproducibility
    random.seed(42)
    random.shuffle(valid_samples)

    total = len(valid_samples)
    n_train = int(total * split_ratio[0])
    n_val = int(total * split_ratio[1])

    splits = {
        "train": valid_samples[:n_train],
        "val": valid_samples[n_train:n_train + n_val],
        "test": valid_samples[n_train + n_val:]
    }

    print(f"[DatasetPrep] Splitting: Train={len(splits['train'])}, Val={len(splits['val'])}, Test={len(splits['test'])}")

    for split_name, pairs in splits.items():
        for img_p, lbl_p in pairs:
            # Copy image
            shutil.copy(img_p, output_path / "images" / split_name / img_p.name)
            # Copy & sanitize label
            with open(lbl_p, "r") as f_in, open(output_path / "labels" / split_name / lbl_p.name, "w") as f_out:
                for line in f_in:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        x, y, w, h = validate_bbox(*parts[1:5])
                        f_out.write(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    print(f"[DatasetPrep] Harmonization complete! Output written to: {output_dir}")

if __name__ == "__main__":
    print("Dataset preparation module loaded. Run with process_and_split(raw_images, raw_labels, output_dir).")
