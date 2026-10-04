# MOTIONSTRIKE 🎯

**A webcam-based, hand-tracking arcade game built with Python, Pygame, OpenCV, and MediaPipe.**

MotionStrike turns your index fingertip into an in-game cursor. Move your hand in front of a webcam and catch the falling targets before they reach the bottom of the screen.

> **Made for Inspira 2026** — MotionStrike was showcased at the exhibition, where nearly 600 visitors attended over two days and got to experience the game.

## ✨ Features

- **Real-time hand tracking** using MediaPipe Hand Landmarker.
- **Gesture-based gameplay:** use your index fingertip to catch targets—no mouse needed during play.
- **Multiple target types** with different score values.
- **Progressive difficulty:** target speed increases as you level up.
- **Scoreboard and leaderboard:** the game stores the top 10 scores locally.
- **Audio:** background music and sound effects.
- **Resizable window and fullscreen support.**

## 🎮 How to Play

1. Start the game and enter a player name.
2. Press **Enter** to begin.
3. Move your hand in front of the webcam. Your index fingertip controls the on-screen cursor.
4. Catch each falling target before it leaves the screen.
5. Missing a target ends the round. Try to beat the leaderboard!

### Targets

| Target | Points |
|---|---:|
| Blue target | +2 |
| Red virus target | +10 |
| Green power-up | +5 |
| Orange danger target | -30 |

*The values above reflect the current game code.*

### Keyboard Controls

| Key | Action |
|---|---|
| Enter | Start / play again |
| Backspace | Delete the last character while entering your name |
| F10 | Maximize / restore the window |
| F11 | Toggle fullscreen / windowed mode |
| Esc | Quit from the start or game-over screen |

## 🧰 Requirements

- Windows PC
- Python
- A working webcam
- The packages listed in [requirements.txt](requirements.txt)

The repository includes the MediaPipe model file, hand_landmarker.task, required for hand tracking.

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/abh1nvx/motionstrike.git
cd motionstrike
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly using .\.venv\Scripts\python.exe.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Python compatibility note:** MediaPipe wheels are not available for every Python version. If installation fails, use a Python version supported by the MediaPipe release you're installing, then recreate the virtual environment with that version.

### 4. Run MotionStrike

Launch the main exhibition game:

```bash
python pygame_tracking_test.py
```

The game currently selects camera index 1 in pygame_tracking_test.py. If your webcam is assigned a different index, change CAMERA_INDEX near the top of that file.

## 📁 Project Structure

```text
motionstrike/
├── game.py                    # Game rules, screens, targets, scoring, leaderboard
├── hand_tracker.py             # MediaPipe hand-tracking interface
├── pygame_tracking_test.py    # Main Pygame + webcam game
├── main.py                     # Basic OpenCV game runner
├── hand_landmarker.task        # MediaPipe hand-landmarker model
├── requirements.txt            # Python dependencies
├── motionstrike_leaderboard.json
├── sounds/
│   ├── background_music.mp3
│   ├── quit.mp3
│   └── touch.mp3
└── ...                         # Camera and tracking test scripts
```

## 🧠 Built With

- [Python](https://www.python.org/)
- [Pygame-ce](https://pyga.me/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)

## 🙌 Acknowledgements

Created as a hands-on exploration of computer vision, real-time hand tracking, and interactive game development—and brought to life at **Inspira 2026**.

If you try MotionStrike, feel free to ⭐ the repository!
