# CivicSense Model Card: YOLO11-Civic-v1.0

## Model Details
- **Developer:** CivicSense Engineering Team
- **Model Architecture:** Ultralytics YOLO11n (2.6M parameters, 6.5 GFLOPs)
- **Input Resolution:** $640 \times 640 \times 3$
- **Model Task:** Multi-Class Object Detection for Urban Defect Intelligence
- **License:** MIT / Academic Evaluation

---

## Target Categories
1. `pothole` (Potholes, asphalt depressions)
2. `road_crack` (Transverse, longitudinal, and fatigue cracks)
3. `garbage_pile` (Solid waste accumulations, overflowing dumpsters)
4. `damaged_streetlight` (Damaged light poles, non-functional fixtures, exposed wiring)
5. `damaged_infrastructure` (Damaged pedestrian guardrails, broken footpaths, compromised barriers)

---

## Training Data & Methodology
- **Source Datasets Investigated:** RDD2022 (Road Damage Dataset), TACO (Trash Annotations in Context), and synthetic defect distributions.
- **Harmonization Pipeline:**
  - Converted annotations into unified YOLO format (`classes.yaml`).
  - Filtered corrupt images and checked bounding box sanity ($0.0 \le x, y, w, h \le 1.0$).
  - Stratified 70/20/10 train/validation/test split grouped by camera sequence/location to eliminate scene leakage across splits.
- **Optimization:** AdamW optimizer, lr0=0.002, weight decay=0.0005, mosaic & mixup augmentations.

---

## Benchmark Metrics (Test Set Evaluation)

| Metric | Score |
|---|---|
| **mAP @ 0.50 (All Classes)** | **78.4%** |
| **mAP @ 0.50:0.95 (All Classes)** | **54.2%** |
| **Precision** | **81.2%** |
| **Recall** | **74.8%** |
| **F1 Score** | **77.8%** |

### Latency
- **CPU Inference (Intel Xeon):** 38.4 ms
- **GPU Inference (NVIDIA T4):** 7.2 ms
- **Full API Round-Trip:** ~62 ms

---

## Ethical Considerations & Limitations
1. **Never Represented as Absolute Certainty:** AI detections provide confidence tiers (High/Medium/Low) and encourage citizen confirmation.
2. **Citizen Privacy:** EXIF metadata is systematically stripped prior to model inference and storage.
3. **Environmental Factors:** Model recall decreases in heavy rain, standing water reflections, and low-light nocturnal conditions.
