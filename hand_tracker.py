import cv2
import mediapipe as mp
import numpy as np
import time

class HandTracker:
    def __init__(self, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = None
        self.mp_draw = None
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='models/hand_landmarker.task'),
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            running_mode=VisionRunningMode.VIDEO
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self.prev_positions = {} # To calculate velocity
        self.prev_time = time.time()
        
    def process_frame(self, frame):
        """Processes the frame and returns tracked hand data."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        current_time_ms = int(time.time() * 1000)
        
        # In VIDEO mode, we pass timestamps
        results = self.landmarker.detect_for_video(mp_image, current_time_ms)
        
        hands_data = []
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt == 0: dt = 0.001
        
        if results.hand_landmarks:
            for i, hand_landmarks in enumerate(results.hand_landmarks):
                # results.handedness contains ClassificationList per hand
                label = results.handedness[i][0].category_name if results.handedness else "Unknown"
                
                keypoints = []
                # landmark here is a list of NormalizedLandmark objects with x, y, z
                for lm in hand_landmarks:
                    keypoints.extend([lm.x, lm.y])
                
                wrist = hand_landmarks[0]
                middle_tip = hand_landmarks[12]
                hand_size = np.sqrt((wrist.x - middle_tip.x)**2 + (wrist.y - middle_tip.y)**2)
                
                index_tip = hand_landmarks[8]
                pos = (index_tip.x, index_tip.y)
                
                velocity = (0.0, 0.0)
                hand_id = f"{label}_{i}"
                if hand_id in self.prev_positions:
                    prev_pos = self.prev_positions[hand_id]
                    vx = (pos[0] - prev_pos[0]) / dt
                    vy = (pos[1] - prev_pos[1]) / dt
                    velocity = (vx, vy)
                
                self.prev_positions[hand_id] = pos
                
                hands_data.append({
                    "id": hand_id,
                    "label": label,
                    "landmarks": hand_landmarks,
                    "keypoints": keypoints,
                    "index_tip": pos,
                    "size": hand_size,
                    "velocity": velocity,
                    "speed": np.sqrt(velocity[0]**2 + velocity[1]**2)
                })
                
        self.prev_time = current_time
        return hands_data, results
