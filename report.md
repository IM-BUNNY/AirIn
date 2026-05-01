# Air Instrument Development Report

## Overview
The "Air Instrument" project has been successfully built and implemented. It is a complete real-time computer vision system that translates hand gestures into musical instrument controls, leveraging the power of MediaPipe, OpenCV, pygame, and scikit-learn.

## Architecture & Components
The system is cleanly divided into several modular files, following software engineering best practices:

1. **`main.py`**: The entry point that ties all the components together. It manages the webcam feed, passes frames to the hand tracker, triggers predictions, controls sound, renders UI via the visualizer, and handles keyboard inputs.
2. **`hand_tracker.py`**: Wraps the Google MediaPipe Hands framework to extract 21 landmarks (42 keypoints) per hand. It tracks velocity between frames and computes a proxy for hand size (z-axis depth).
3. **`gesture_classifier.py`**: Contains the logic to save normalized keypoints into a CSV file (`data/gesture_data.csv`), train an MLP (Multi-Layer Perceptron) Neural Network model on the fly using `scikit-learn`, and make real-time predictions. The trained model is cached via `joblib` in `models/gesture_model.pkl`.
4. **`sound_engine.py`**: Utilizes `pygame.mixer` to play audio with low latency (buffer size 512). It translates vertical hand position (Y-axis) to specific notes, sets volume based on hand size (Z-axis), and determines intensity based on hand velocity. Includes an internal cooldown mechanism to prevent "note spamming".
5. **`midi_bridge.py`**: An optional bridge using `python-rtmidi` that can transmit standard MIDI signals (Note On/Note Off) to external Digital Audio Workstations (DAWs) like GarageBand.
6. **`visualizer.py`**: Uses OpenCV's drawing primitives to overlay the tracked hand skeleton (with distinct colors for left/right hands), draw ripple effects for triggered notes, project floating text annotations, and render a dynamic volume equalizer.

## Features Built
- **Real-time Tracking**: Simultaneously tracks up to two hands smoothly.
- **Expressiveness**: Note volume adapts depending on your hand size/distance and movement speed.
- **Gesture Control**: 
    - **Open Palm**: Idle state / sustain.
    - **Fist**: Swiftly striking down triggers drums.
    - **Index**: Moving your finger up and down plays the piano/guitar scale.
    - **Peace (✌️)**: Swaps between Piano, Drums, and Guitar.
    - **Pinch**: Acts as a mute or panic button.
- **ML Training Loop**: Integrated data collection (press 'C') and training pipeline (press 'T').
- **Visual Feedback**: Real-time HUD showing the current gesture, active instrument, and visual triggers (ripples).

## Environment and Dependencies
A `requirements.txt` file is provided to set up the environment, requiring `opencv-python`, `mediapipe`, `pygame`, `scikit-learn`, `numpy`, and `joblib`. The code is written defensively so that if `python-rtmidi` cannot be installed on a specific setup or Apple Silicon Mac, the system will gracefully degrade instead of crashing.

## Next Steps for the User
1. Ensure your `.wav` files are placed inside their respective directories under `sounds/`.
2. Run `python main.py`.
3. Start by collecting data for the gestures: perform a gesture, press `C`, enter its label, and repeat to build a dataset.
4. Press `T` to train the neural network.
5. Wave your hands and play music!
