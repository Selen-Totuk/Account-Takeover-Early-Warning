<<<<<<< HEAD
 🎧 Spotify Security Monitoring Dashboard (PoC)

This project is a **proof-of-concept (PoC)** security monitoring dashboard designed to analyze **abnormal user behavior patterns** in a music streaming platform environment using **synthetic data**.

The goal is **not** to exploit or access real Spotify systems, but to demonstrate:
- security-oriented thinking,
- anomaly detection logic,
- and how risk signals can be surfaced in an operational dashboard.

---

## 🚩 Problem Statement

Music streaming platforms face various security risks such as:
- account takeovers,
- credential sharing,
- bot-driven listening fraud,
- abnormal device or location switching.

These behaviors are often **not obvious from a single signal** and require **multi-factor behavioral analysis**.

---

## 🧠 Core Idea

Instead of labeling users as malicious, the system evaluates **user-day activity patterns** and flags **days with abnormal behavior**.

A day is considered risky **only when multiple independent indicators deviate from the user's historical baseline**.

---

## 🧩 Features

### 🔍 Behavioral Signals
- Total listening duration
- Number of unique tracks
- Night listening ratio
- Device diversity
- Location switching
- Session frequency

### 🤖 Anomaly Detection
- **Isolation Forest** (unsupervised)
- Model trained **without labels**
- Ground truth (`is_attacker`) is used **only for simulation validation**, not training

### 📊 Dashboard
- Real-time risk score overview
- Risk trend over time
- Device and location distribution
- Recent suspicious activity feed

---

## 🏗️ Architecture


Synthetic Data Generator
↓
Feature Engineering
↓
Isolation Forest Model
↓
Risk Scoring Logic
↓
Flask API
↓
Web Dashboard (HTML/CSS/JS)


---

## ⚠️ Important Notes (Ethical & Legal)

- All data is **synthetic and randomly generated**
- No real Spotify user data is used
- No scraping, reverse engineering, or API abuse
- This project is **educational and demonstrative only**

---

## 🧪 Technology Stack

- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- HTML / CSS / Vanilla JavaScript

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
python app.py

Then open:

http://localhost:5000
📈 What This Project Demonstrates

✔ Understanding of behavioral security concepts
✔ Practical anomaly detection usage
✔ Clear separation between simulation and reality
✔ Ability to translate raw data into security insight

🔮 Possible Extensions

Real OAuth-based account login (conceptual)

Streaming data ingestion (Kafka / WebSocket)

User baseline learning over longer periods

Rule-based + ML hybrid risk engine

Incident explanation module (why flagged?)

📬 Disclaimer

This project is not affiliated with Spotify.
Spotify is referenced only as a theoretical platform context.

👤 Author

Developed by a Computer Engineering student with a focus on:

cybersecurity,

anomaly detection,

and applied machine learning.
=======
# spotify_security_project
>>>>>>> eb1f660d307f850088e66bebcf16cbb3eb5fca87
