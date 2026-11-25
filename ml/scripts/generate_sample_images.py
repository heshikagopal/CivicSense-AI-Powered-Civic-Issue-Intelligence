"""
Generates synthetic civic test images for local end-to-end testing
and UI demonstration in backend/samples/ and backend/uploads/
"""
import os
from PIL import Image, ImageDraw

def create_samples():
    out_dir = os.path.abspath("./backend/samples")
    uploads_dir = os.path.abspath("./backend/uploads")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)

    samples = [
        ("pothole_sample.jpg", "POTHOLE ON ARTERIAL ROAD", (60, 60, 65), (25, 25, 28), "pothole"),
        ("road_crack_sample.jpg", "TRANSVERSE ASPHALT CRACK", (75, 75, 80), (35, 35, 40), "crack"),
        ("garbage_pile_sample.jpg", "MUNICIPAL GARBAGE DUMP", (85, 90, 80), (60, 110, 60), "garbage"),
        ("damaged_streetlight_sample.jpg", "DAMAGED STREETLIGHT POLE", (40, 50, 65), (200, 180, 50), "streetlight"),
        ("damaged_infrastructure_sample.jpg", "BROKEN PEDESTRIAN GUARDRAIL", (70, 70, 75), (140, 60, 60), "infrastructure")
    ]

    for filename, title, bg_col, feature_col, feature_type in samples:
        img = Image.new("RGB", (640, 480), color=bg_col)
        draw = ImageDraw.Draw(img)

        # Draw road texture / surface grid
        for y in range(0, 480, 40):
            draw.line([(0, y), (640, y)], fill=(bg_col[0] - 8, bg_col[1] - 8, bg_col[2] - 8), width=2)

        # Draw specific civic defect shape
        if feature_type == "pothole":
            # Dark oval cavity with jagged border
            draw.ellipse([180, 150, 460, 330], fill=feature_col, outline=(15, 15, 15), width=4)
            draw.ellipse([220, 180, 420, 300], fill=(15, 15, 18))
        elif feature_type == "crack":
            # Jagged crack line
            points = [(100, 240), (220, 230), (310, 260), (430, 220), (550, 250)]
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=feature_col, width=8)
        elif feature_type == "garbage":
            # Cluster of colored debris
            for offset in [(200, 200), (250, 240), (300, 190), (360, 220), (400, 250)]:
                draw.rectangle([offset[0], offset[1], offset[0] + 50, offset[1] + 40], fill=feature_col)
        elif feature_type == "streetlight":
            # Vertical pole with bent angle
            draw.rectangle([300, 80, 320, 400], fill=(120, 130, 140))
            draw.ellipse([270, 60, 350, 110], fill=feature_col)
        elif feature_type == "infrastructure":
            # Broken barrier
            draw.rectangle([120, 200, 280, 220], fill=feature_col)
            draw.line([(280, 220), (350, 320)], fill=feature_col, width=12)

        # Draw label banner
        draw.rectangle([0, 0, 640, 45], fill=(20, 25, 30))
        draw.text((20, 14), f"CivicSense Sample: {title}", fill=(255, 255, 255))

        target_sample_path = os.path.join(out_dir, filename)
        target_upload_path = os.path.join(uploads_dir, filename)
        img.save(target_sample_path, quality=90)
        img.save(target_upload_path, quality=90)

    print(f"[Samples] Generated 5 realistic sample images in {out_dir} and {uploads_dir}")

if __name__ == "__main__":
    create_samples()
