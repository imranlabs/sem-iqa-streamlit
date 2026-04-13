# SEM Image Quality Metrics Tool

[![Live App](https://img.shields.io/badge/Live%20App-sem--iqm--tool.streamlit.app-ff4b4b?logo=streamlit)](https://sem-iqm-tool.streamlit.app)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render)](https://sem-iqa-backend.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.14.3%20%28frontend%29%20%7C%203.13%20%28backend%29-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A full-stack web application for quantitative image quality assessment and tool-to-tool matching. Originally designed for **CD-SEM metrology workflows** in semiconductor manufacturing, the metrics are general-purpose and work on any grayscale or RGB image pair.

---

## Live Demo

🔬 **[https://sem-iqm-tool.streamlit.app](https://sem-iqm-tool.streamlit.app)**

> **Note:** The backend is hosted on Render's free tier and may take 30–60 seconds to wake up on the first request after a period of inactivity.

---

## Features

- **Full-reference metrics** — SSIM, PSNR, Normalized Variance focus score (Normvar)
- **Sharpness analysis** — Laplacian variance ratio and FFT high-frequency energy ratio
- **Contrast-to-Noise Ratio (CNR)** — signal-to-background contrast assessment
- **Tool-to-tool histogram matching** — correlation, Hellinger distance, brightness and contrast comparison
- **FFT spectrum visualization** — reference, test, and difference magnitude spectra with colorbars
- **BRISQUE score** — no-reference perceptual quality metric (experimental, included for completeness)
- **CSV report export** — timestamped, named report downloadable from the Metrics tab
- **Robust image handling** — automatic grayscale conversion, shape mismatch detection with auto-resize to smaller dimensions, 50MB file size limit

---

## Metrics Overview

| Metric | Type | What it detects |
|--------|------|----------------|
| SSIM | Full-reference | Structural degradation, charging, drift |
| PSNR | Full-reference | Electronic noise, pixel-level distortion |
| Normvar | No-reference | Focus / Z-height mismatch |
| Laplacian ratio | Full-reference | Edge blurring, resolution loss |
| FFT ratio | Full-reference | Vibration, EMI, astigmatism |
| CNR | No-reference | Contrast loss, secondary electron yield |
| Hellinger distance | Full-reference | Brightness/contrast (gain) mismatch |
| BRISQUE | No-reference | Perceptual quality (unreliable for SEM) |

---

## Architecture

```
Browser
   │
   ▼
Streamlit Frontend          (Streamlit Community Cloud — Python 3.14.3)
app/main.py                 Entry point
app/components/             UI tabs: Metrics, Histogram, FFT
app/utils/api_client.py     All HTTP calls to the backend
   │
   │  HTTP (JSON)
   ▼
FastAPI Backend             (Render — Python 3.13 / Docker)
app/api/routes/analysis.py  POST /api/v1/analyze
app/api/routes/analysis.py  POST /api/v1/fft
app/services/iqa_service.py Bridge: FastAPI ↔ sem_iqa package
   │
   ▼
sem_iqa package
sem_iqa/metrics.py          All IQA computation functions
sem_iqa/degradations.py     Synthetic SEM degradation simulations
sem_iqa/visualization.py    Matplotlib figure helpers (notebook use)
sem_iqa/opencv_models/      BRISQUE model files
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Pydantic, Gunicorn + Uvicorn |
| Image processing | OpenCV, scikit-image, NumPy, SciPy |
| Containerisation | Docker, Docker Compose |
| Backend deployment | Render (free tier) |
| Frontend deployment | Streamlit Community Cloud |

---

## Local Development

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

Clone both repos into a shared root directory:

```bash
mkdir sem-iqa && cd sem-iqa
git clone https://github.com/imranlabs/sem-iqa-streamlit
git clone https://github.com/imranlabs/sem-iqa-backend   # private
```

Create environment files:

**`sem-iqa-backend/.env`**
```
ENVIRONMENT=dev
TESTING=0
ALLOWED_ORIGINS=["http://localhost:8501"]
```

**`sem-iqa-frontend/.env`**
```
BACKEND_URL=http://backend:8000
```

Create a root-level `docker-compose.yml`:

```yaml
services:
  backend:
    build:
      context: ./sem-iqa-backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./sem-iqa-backend/.env

  frontend:
    build:
      context: ./sem-iqa-streamlit
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    env_file:
      - ./sem-iqa-streamlit/.env
    depends_on:
      - backend
```

Start both services:

```bash
docker-compose up --build
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
sem-iqa-streamlit/
├── app/
│   ├── main.py                  # Streamlit entry point
│   ├── core/
│   │   └── config.py            # Pydantic settings (BACKEND_URL)
│   ├── components/
│   │   ├── upload.py            # Sidebar image upload
│   │   ├── metrics.py           # Metrics tab
│   │   └── charts.py            # Histogram and FFT tabs
│   └── utils/
│       ├── api_client.py        # All backend HTTP calls
│       └── report.py            # CSV report generation
├── .streamlit/
│   └── config.toml              # maxUploadSize = 50MB
├── Dockerfile
├── Dockerfile.prod
└── requirements.txt
```

---

## Accepted Image Formats

`JPG` · `PNG` · `BMP` · `TIFF` — maximum 50MB per image.

All images are converted to grayscale internally regardless of input format.

---

## Acknowledgements

- Normalized Variance Focus Score adapted from [Yu Sun et al.](https://doi.org/10.1002/jemt.20118)
- BRISQUE model files from OpenCV contrib
- Distortion methodology inspired by [TID2013](https://doi.org/10.1016/j.image.2014.10.009)

---

## Citation

If you use this tool or reference this work, please cite:

> Khan, I. (2026). *SEM Image Quality Metrics Tool*. GitHub.  
> https://github.com/imranlabs/sem-iqa-streamlit

---

## Author

**Imran Khan**  
[khanimran.com](https://khanimran.com) · imransmailbox@gmail.com  
© 2026 Imran Khan — MIT License
