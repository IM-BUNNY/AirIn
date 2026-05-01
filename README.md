# Air Instrument

A real-time system where hand gestures detected through a webcam trigger and control musical instrument sounds, creating an "antigravity" instrument experience where the user plays music without touching anything.

## Setup Instructions

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Make sure you have your audio samples in the `sounds/` directory. Create these folders and add the respective `.wav` files:
   - `sounds/piano/`: `C3.wav`, `D3.wav`, `E3.wav`, `F3.wav`, `G3.wav`, `A3.wav`, `B3.wav`, `C4.wav`, `D4.wav`, `E4.wav`, `F4.wav`, `G4.wav`, `A4.wav`, `B4.wav`, `C5.wav`
   - `sounds/drums/`: `kick.wav`, `snare.wav`, `hihat.wav`
   - `sounds/guitar/`: `chord_C.wav`, `chord_G.wav`, `chord_D.wav`, `chord_Am.wav`
   
3. Run the application:
   ```bash
   python main.py
   ```

## Keyboard Controls

- **C** — Collect gesture sample (prompts for label in terminal)
- **T** — Train model from collected CSV data
- **M** — Toggle MIDI mode on/off
- **1, 2, 3** — Manually switch instruments (1: Piano, 2: Drums, 3: Guitar)
- **Q** — Quit

## Collecting Gesture Data

1. Run the application using `python main.py`.
2. Make a hand gesture in front of the camera.
3. Press **C**. The terminal will prompt you to enter a label for the gesture.
4. Enter one of the following labels: `Open Palm`, `Fist`, `Index`, `Peace`, `Pinch`.
5. Repeat this for multiple samples of each gesture to build a robust dataset.

## Training the Model

1. After collecting sufficient data (e.g., 20+ samples per gesture), press **T** while the application is running.
2. The system will train an MLP Classifier and save it as `models/gesture_model.pkl`.
3. The trained model will automatically be loaded and used for gesture recognition.

## Gestures and Actions

- **Open Palm**: Volume swell / sustain.
- **Fist**: Drum hit (triggered on fast movement).
- **Index finger pointing**: Play piano note based on Y position.
- **Peace sign (✌️)**: Switch active instrument.
- **Pinch (thumb + index close)**: Mute / stop sound.

## Features

- **Expressiveness**: Hand velocity maps to note intensity (volume).
- **Pitch Control**: Vertical position (Y) maps to musical notes.
- **Volume Control**: Hand size (Z-axis proxy) maps to overall volume.
- **Visual Feedback**: Real-time OpenCV rendering of hand tracking, current note, active instrument, and visual equalizer.
- **MIDI Bridge**: Optional MIDI output via `python-rtmidi` (press M to enable). Sends signals to DAWs like GarageBand on Mac.
