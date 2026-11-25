# CivicSense AI Model Evaluation Report

**Model Architecture:** Ultralytics YOLO11n (CivicSense fine-tuned)  
**Input Size:** 640x640  
**Parameters:** 2.6M (6.5 GFLOPs)  
**Evaluation Dataset:** CivicSense Unified Benchmark (RDD2022 + TACO + Synthetic Road Defects) (350 test images)  
**Evaluation Date:** 2026-11-25 11:10:34 UTC  

---

## 1. Summary Metrics

| Metric | Score |
|---|---|
| **mAP @ 0.50 (All Categories)** | **78.4%** |
| **mAP @ 0.50:0.95 (All Categories)** | **54.2%** |
| **Overall Precision** | **81.2%** |
| **Overall Recall** | **74.8%** |
| **F1 Score** | **77.8%** |

---

## 2. Per-Category Performance

| Category | Precision | Recall | mAP@50 | mAP@50:95 | Test Instances |
|---|---|---|---|---|---|
| **Pothole** | 84.5% | 81.0% | 83.2% | 58.9% | 112 |
| **Road Crack** | 78.2% | 72.0% | 74.5% | 49.2% | 94 |
| **Garbage Pile** | 82.6% | 76.5% | 80.1% | 56.4% | 68 |
| **Damaged Streetlight** | 79.5% | 71.0% | 75.8% | 52.1% | 42 |
| **Damaged Infrastructure** | 81.1% | 73.5% | 78.5% | 54.4% | 34 |

---

## 3. Inference Latency

- **CPU Average Inference:** 38.4 ms
- **GPU (NVIDIA T4) Inference:** 7.2 ms
- **End-to-End API Response Time (Upload + Stripping + Detection + DB):** ~62 ms

---

## 4. Key Findings & Error Analysis
1. **Potholes:** High recall on asphalt roads in clear daylight. Slight drop in recall during rain / reflections.
2. **Road Cracks:** Fine hairline cracks (<5px) require multi-scale augmentation to resolve reliably.
3. **Streetlights:** Night vs day lighting transitions benefit from illumination normalization.
