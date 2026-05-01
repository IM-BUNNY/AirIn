import cv2
import sys
import time

from hand_tracker import HandTracker
from gesture_classifier import GestureClassifier
from sound_engine import SoundEngine
from midi_bridge import MidiBridge
from visualizer import Visualizer

def main():
    print("Initializing Air Instrument...")
    
    # Initialize components
    tracker = HandTracker()
    classifier = GestureClassifier()
    sound_engine = SoundEngine()
    midi_bridge = MidiBridge()
    visualizer = Visualizer()
    
    # Initialize WebCam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)
        
    frame_count = 0
    recording_mode = False
    
    print("Air Instrument Ready!")
    print("Controls: C=Collect, T=Train, M=MIDI, 1/2/3=Instrument, Q=Quit")

    last_gesture = "Unknown"
    peace_cooldown = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Mirror the frame horizontally for selfie view
        frame = cv2.flip(frame, 1)
        frame_count += 1
        
        # Track hands
        hands_data, results = tracker.process_frame(frame)
        
        current_gesture = "Unknown"
        
        if hands_data:
            # Display the gesture of the first hand
            for idx, hand in enumerate(hands_data):
                # Predict gesture
                gesture = classifier.predict(hand['keypoints'])
                if idx == 0:
                    current_gesture = gesture
                    
                # Handle Instrument Switching via Peace Sign
                if "peace" in gesture.lower() and time.time() - peace_cooldown > 1.0:
                    sound_engine.switch_instrument()
                    peace_cooldown = time.time()
                    print(f"Switched to: {sound_engine.get_active_instrument()}")
                    
                # Trigger sound based on gesture
                triggered_note = sound_engine.process_gesture(gesture, hand)
                midi_bridge.process_gesture_midi(gesture, hand)
                
                if triggered_note:
                    visualizer.add_note_trigger(hand['index_tip'][0], hand['index_tip'][1], triggered_note, frame_count)
                    
            # Draw tracking
            visualizer.draw_tracking(frame, hands_data, tracker.mp_hands, tracker.mp_draw)
        
        # Draw Visuals
        # Calculate overall volume proxy for equalizer
        vol_proxy = sum(h['size'] for h in hands_data) if hands_data else 0.0
        visualizer.draw_effects(frame, frame_count)
        visualizer.draw_equalizer(frame, min(1.0, vol_proxy * 2.0))
        visualizer.draw_ui(frame, sound_engine.get_active_instrument(), current_gesture, midi_bridge.enabled, recording_mode)
        
        cv2.imshow('Air Instrument', frame)
        
        # Handle Keyboard Input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            # Collect data
            if hands_data:
                # Pause and ask for label in terminal
                cv2.putText(frame, "LOOK AT TERMINAL", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.imshow('Air Instrument', frame)
                cv2.waitKey(1)
                
                print("\n--- DATA COLLECTION ---")
                print("Available labels: Open Palm, Fist, Index, Peace, Pinch")
                label = input("Enter label for current gesture (or press Enter to skip): ").strip()
                if label:
                    # Save the first hand's keypoints
                    classifier.save_sample(hands_data[0]['keypoints'], label)
        elif key == ord('t'):
            print("\n--- TRAINING MODEL ---")
            classifier.train()
        elif key == ord('m'):
            midi_bridge.toggle()
        elif key == ord('1'):
            sound_engine.set_instrument(0)
        elif key == ord('2'):
            sound_engine.set_instrument(1)
        elif key == ord('3'):
            sound_engine.set_instrument(2)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
