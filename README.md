# MudraMingle
#vE:\DT\app> .\.venv\Scripts\python.exe app.py

**MudraMingle** is a Flask-based web application that uses computer vision to detect and interpret **Bharatanatyam mudras** — the traditional hand gestures of Indian classical dance — in real time from a webcam feed.

It is designed as a learning aid: as a dancer performs a mudra in front of the camera, the application identifies the gesture, overlays the hand skeleton on the video, and displays the mudra's name, Devanagari script, and traditional meaning on screen.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Supported Mudras](#supported-mudras)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- **Real-time hand tracking** using MediaPipe's 21-landmark hand model.
- **Recognition of 16 Bharatanatyam mudras** based on finger positions and inter-fingertip distances.
- **Live webcam streaming** through a Flask web interface (MJPEG video feed).
- **On-screen mudra info card** showing the mudra's display name, Devanagari script, emoji, and a short description of its symbolism.

## How It Works

1. OpenCV captures frames from the webcam.
2. MediaPipe Hands extracts 21 landmarks per detected hand.
3. The app derives two signals from those landmarks:
   - **Finger states** — whether each of the 5 fingers is extended or folded.
   - **Inter-tip distances** — Euclidean distances between fingertip pairs (thumb–index, index–middle, etc.).
4. A rule-based classifier matches the current pose against patterns for each mudra.
5. The recognized mudra name is exposed via the `/current_mudra` JSON endpoint, which the frontend polls to update the info card.

## Supported Mudras

The app currently recognizes the following 16 single-hand (*asamyukta hasta*) mudras:

| # | Mudra | Devanagari | Meaning |
|---|-------|------------|---------|
| 1 | Patāka | पताका | Flag — clouds, forest, river, blessing |
| 2 | Tripatāka | त्रिपताक | Three parts of a flag — crown, tree, arrow |
| 3 | Śikhara | शिखर | Spire — bow, pillar, silence |
| 4 | Ardhapatāka | अर्धपताक | Half flag — leaves, riverbank, tower |
| 5 | Karthārīmukha | कर्तरीमुख | Scissors face — separation, lightning |
| 6 | Mayūra | मयूर | Peacock's beak — omens, wiping tears |
| 7 | Ardhachandra | अर्धचन्द्र | Half moon — moon, plate |
| 8 | Arāla | अराल | Bent — drinking nectar, holy water |
| 9 | Kaṭakāmukha | कटकामुख | Link in a chain — picking flowers, holding a mirror |
| 10 | Siṁhamukha | सिंहमुख | Lion face — hare, lotus, deer |
| 11 | Kapittha | कपित्थ | Wood apple — Lakshmī, Sarasvatī, cymbals |
| 12 | Muṣṭi | मुष्टि | Fist — grasping, wrestling, steadfastness |
| 13 | Sūchī | सूचि | Needle — oneness, the sun, threading |
| 14 | Chandrakalā | चन्द्रकला | Crescent moon — the moon, the face |
| 15 | Mṛgaśīrṣa | मृगशीर्ष | Deer head — deer, a graceful woman |
| 16 | Alapadma | अलपद्म | Lotus in full bloom — beauty, longing |

## Tech Stack

- **Python 3.x**
- **Flask** — web server and routing
- **OpenCV** — webcam capture and frame rendering
- **MediaPipe** — hand landmark detection
- **NumPy** — numerical operations on landmark data

## Project Structure

```
app/
├── app.py              # Flask app, video stream, mudra detection logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main UI rendered by Flask
├── web/
│   └── index.html      # Static landing page (GitHub Pages)
├── LICENSE
└── README.md
```

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/<your-username>/MudraMingle.git
cd MudraMingle/app
```

**2. Create and activate a virtual environment** (recommended)

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

The Flask server will start on `http://127.0.0.1:5000/`. Open that URL in your browser, allow camera access, and the live webcam feed will begin streaming with mudra recognition overlays.

Press `q` in the OpenCV preview window (or close the browser tab) to stop the session.

## Usage

1. Stand in front of the webcam with good, even lighting.
2. Keep one hand clearly visible within the frame.
3. Form a Bharatanatyam mudra — the app will:
   - Draw the hand skeleton overlay.
   - Identify the mudra and display its name, script, and meaning.
4. Practice multiple mudras in sequence.

## Roadmap

- Support for two-handed (*samyukta hasta*) mudras.
- Replace rule-based classification with an ML model trained on labeled mudra images.
- Dance form classification across the 8 Indian classical dance styles: Bharatanatyam, Kathak, Kathakali, Kuchipudi, Manipuri, Mohiniyattam, Odissi, and Sattriya.
- Practice mode with target mudras and accuracy scoring.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in the repository.
