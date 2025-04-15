# 📡 RF-Based Human Presence Detection using Wi-Fi RSSI and Machine Learning

This repository contains all the essential code, models, datasets, and results for a Wi-Fi RSSI-based human presence detection project. It combines 2.4 GHz RSSI data from ESP modules and visual supervision using camera frames to classify the presence zone of a person in an indoor environment.

## 🧠 Overview

The system uses:
- RSSI heatmaps generated from 4 ESP Wi-Fi nodes placed at fixed corners.
- Live or saved webcam frames for cross-modal supervision.
- Kalman filters for signal smoothing.
- A Random Forest classifier trained on both RSSI (heatmap) and camera features.

It achieves **~94% classification accuracy** using a 10×10 heatmap grid with 2232 training samples.
---
<p align = "left">
<img src="images/IMG_20250406_182836_300 (1).jpg" alt="Material RSSI" width="400">
</p>

## ⚡Materials Required:
- ESP32/ESP8266
> I used 2 ESP32 and 2 ESP8266 but recommended to use ESP32
- A Modem/Router (2.4 GHz)
- Powering system (battery)
- Camera (Use phone as IP cam)(If you are training)
> The codes of all the Embedded codes will be given in the MAY 2025

---
## 🗃️ Repository Structure

| File/Folder                  | Description |
|-----------------------------|-------------|
| `test_report.py`            | Predicts presence zone using **Folder containing multiple heatmaps** |
| `test_heatmap_model.py`     | Predicts using **single heatmap only**  |
| `model_g.pkl`               | Final trained model (10×10 heatmap + 64×64 webcam input) |
| `classification_report.txt` | Consists of the all the report from intial phase|
| `model_g_scaler.pkl`        | Optional feature scaler used during training (if applied) |
| `Kalman_image_trained/`     | Heatmap images (10×10) used for training |
| `rssi_log.txt`              | Contains all the log values from raw to filtered RSSI values used in sessions|
| `images/`                   | Contains diagrams and figures used in paper |

---

## 📊 Model Performance

### 🧪 Classification Report (From Final Training Run)

```
              precision    recall  f1-score   support

        ESP1       0.91      0.96      0.93       121
        ESP2       0.92      0.94      0.93        98
        ESP3       0.99      0.95      0.97       104
        ESP4       0.97      0.93      0.95       124

    accuracy                           0.94       447
   macro avg       0.95      0.94      0.94       447
weighted avg       0.95      0.94      0.94       447
```

---

## 🧪 How to Test

### 🔍 Heatmap Only (No Webcam)
```bash
python test_heatmap_model.py Kalman_image_trained/heatmap_16-53-42_ESP3.png
```

Expected output:
```
✅ Model loaded.
📌 Prediction for Kalman_image_trained/heatmap_16-53-42_ESP3.png
→ Zone: ESP3
→ Confidence: 0.92
```

---

## 📷 Figures

Visuals included (used in publication):
- Node architecture and heatmap overlays
- Flowchart of model supervision
- RSSI line plots (ESP nodes)

See `images/` folder for reference.

---

## 💡 Notes

- Trained using Random Forest for ease of deployment on low-cost hardware.
- Uses 10×10 heatmaps from 4 static ESP nodes.
- 3G modem provides 2.4 GHz signal field for RF propagation.
- Cross-modal learning improves generalization using webcam frames.
- Includes Kalman filter smoothing of RSSI values.

---

## 🔬 Citation

If you use this work, please cite or acknowledge:

> "RF-Based Indoor Human Presence Estimation using Wi-Fi RSSI and Cross-Modal Learning", Antarip Kar, 2024.

---

## 📚 License

MIT License

---

Feel free to open an issue for questions, bugs, or suggestions.
