import os
import hashlib
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont

def strip_exif_and_save(input_path: str, output_path: str, max_dimension: int = 1920) -> Tuple[int, int, int]:
    """
    Removes EXIF metadata for citizen privacy, resizes large images if needed,
    and saves clean JPEG/PNG.
    Returns (width, height, file_size_bytes).
    """
    with Image.open(input_path) as img:
        # Auto-convert RGBA or other modes to RGB if saving as JPEG
        if img.mode in ("RGBA", "P") and output_path.lower().endswith((".jpg", ".jpeg")):
            img = img.convert("RGB")
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
            
        # Strip EXIF by copying image data without info/exif dict
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(list(img.getdata()))
        
        # Resize if exceeding max dimension
        w, h = clean_img.size
        if max(w, h) > max_dimension:
            scale = max_dimension / float(max(w, h))
            clean_img = clean_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            w, h = clean_img.size
            
        clean_img.save(output_path, quality=88, optimize=True)
        file_size = os.path.getsize(output_path)
        return w, h, file_size

def calculate_file_hash(file_path: str) -> str:
    """Computes SHA-256 hash of file for duplicate checks and integrity."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def draw_detection_boxes(
    image_path: str,
    output_preview_path: str,
    detections: List[dict]
) -> str:
    """
    Draws clear bounding boxes with category label and confidence % on preview image.
    detections: list of dicts with keys: 'bbox' [x1, y1, x2, y2], 'category_name', 'confidence', 'status'
    """
    with Image.open(image_path) as img:
        img_rgb = img.convert("RGB")
        draw = ImageDraw.Draw(img_rgb)
        w, h = img_rgb.size
        
        # Color mapping for civic categories
        color_map = {
            "pothole": "#EF4444",              # Red
            "road_crack": "#F59E0B",           # Amber
            "garbage_pile": "#10B981",         # Emerald Green
            "damaged_streetlight": "#3B82F6",  # Blue
            "damaged_infrastructure": "#8B5CF6"# Purple
        }
        
        for det in detections:
            bbox = det.get("bbox", [0, 0, 0, 0])
            cat_code = det.get("category_code", "pothole")
            label = f"{det.get('category_name', cat_code)}: {int(det.get('confidence', 0.0) * 100)}%"
            color = color_map.get(cat_code, "#EF4444")
            
            x1, y1, x2, y2 = bbox
            # If coordinates are normalized 0-1, convert to pixel space
            if max(x1, y1, x2, y2) <= 1.0:
                x1, x2 = x1 * w, x2 * w
                y1, y2 = y1 * h, y2 * h
                
            # Draw rectangle with thickness
            for offset in range(3):
                draw.rectangle([x1 - offset, y1 - offset, x2 + offset, y2 + offset], outline=color)
                
            # Draw label banner
            banner_height = 24
            banner_width = min(len(label) * 9 + 12, w - x1)
            draw.rectangle([x1, max(0, y1 - banner_height), x1 + banner_width, max(0, y1)], fill=color)
            draw.text((x1 + 6, max(2, y1 - banner_height + 4)), label, fill="#FFFFFF")
            
        img_rgb.save(output_preview_path, quality=85)
        return output_preview_path
