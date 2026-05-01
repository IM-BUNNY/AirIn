import cv2
import numpy as np

class Visualizer:
    def __init__(self):
        self.color_left = (255, 100, 100) # Blueish
        self.color_right = (50, 150, 255) # Orangeish
        
        # Visualizer state
        self.active_notes = [] # tuples of [x, y, note_str, frame_born, age]
        
    def draw_tracking(self, frame, hand_data, mp_hands, mp_draw):
        """Draws landmarks and connections on the frame."""
        HAND_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
        
        for hand in hand_data:
            color = self.color_left if hand['label'] == 'Left' else self.color_right
            
            landmarks = hand['landmarks']
            h, w, c = frame.shape
            
            overlay = frame.copy()
            # Draw connections with glow
            for connection in HAND_CONNECTIONS:
                p1 = landmarks[connection[0]]
                p2 = landmarks[connection[1]]
                
                x1, y1 = int(p1.x * w), int(p1.y * h)
                x2, y2 = int(p2.x * w), int(p2.y * h)
                cv2.line(overlay, (x1, y1), (x2, y2), color, 8)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
                
            # Draw points
            for lm in landmarks:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 6, color, cv2.FILLED)
                cv2.circle(frame, (x, y), 3, (255, 255, 255), cv2.FILLED)
                
            # Draw Velocity Vector
            index_x, index_y = int(hand['index_tip'][0] * w), int(hand['index_tip'][1] * h)
            vx, vy = hand['velocity']
            end_x = int(index_x + vx * w * 0.1)
            end_y = int(index_y + vy * h * 0.1)
            cv2.arrowedLine(frame, (index_x, index_y), (end_x, end_y), (0, 255, 150), 3, tipLength=0.3)

    def draw_ui(self, frame, instrument_name, gesture, midi_enabled, recording_mode=False):
        """Draws the HUD/UI."""
        h, w, _ = frame.shape
        
        # Sleek Top banner
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 70), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.line(frame, (0, 70), (w, 70), (100, 100, 150), 2)
        
        # Title
        cv2.putText(frame, "AIR INSTRUMENT", (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 200, 50), 2)
        
        # Instrument Info
        inst_text = f"MODE: {instrument_name.upper()}"
        cv2.putText(frame, inst_text, (320, 45), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 200), 2)
        
        # Gesture Info
        gest_text = f"DETECTION: {gesture.upper()}"
        cv2.putText(frame, gest_text, (w - 400, 45), cv2.FONT_HERSHEY_DUPLEX, 0.8, (150, 255, 100), 2)
        
        # MIDI Status
        midi_color = (0, 255, 0) if midi_enabled else (0, 0, 255)
        cv2.putText(frame, f"MIDI: {'ON' if midi_enabled else 'OFF'}", (20, h - 30), cv2.FONT_HERSHEY_DUPLEX, 0.6, midi_color, 2)
        
        # Mode indicator
        if recording_mode:
            cv2.circle(frame, (w - 40, 35), 12, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (w - 110, 45), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

    def add_note_trigger(self, x, y, note_str, frame_idx):
        self.active_notes.append([x, y, note_str, frame_idx, 0])

    def draw_effects(self, frame, current_frame_idx):
        """Draws dynamic ripples and floating notes for triggered sounds."""
        h, w, _ = frame.shape
        
        new_notes = []
        for note_data in self.active_notes:
            x_norm, y_norm, text, start_frame, age = note_data
            age += 1
            
            x, y = int(x_norm * w), int(y_norm * h)
            
            # Draw ripple
            radius = age * 8
            alpha = max(0, 255 - age * 12)
            if alpha > 0:
                overlay = frame.copy()
                cv2.circle(overlay, (x, y), radius, (50, 200, 255), max(1, 10 - age//2))
                if text == "MUTE":
                    cv2.circle(overlay, (x, y), radius//2, (0, 0, 255), -1)
                cv2.addWeighted(overlay, alpha/255.0, frame, 1 - alpha/255.0, 0, frame)
                
                # Floating text
                text_y = y - age * 3
                cv2.putText(frame, text, (x - 20, text_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
                
                note_data[4] = age
                new_notes.append(note_data)
                
        self.active_notes = new_notes

    def draw_equalizer(self, frame, volume_proxy):
        """Draws a cool visual equalizer bar at the bottom."""
        h, w, _ = frame.shape
        bar_height = int(volume_proxy * 150)
        bar_width = 40
        
        x = w - 70
        y_bottom = h - 40
        y_top = y_bottom - bar_height
        
        # Background outline
        cv2.rectangle(frame, (x, y_bottom), (x + bar_width, y_bottom - 150), (50, 50, 50), 2)
        
        # Colored bar
        if bar_height > 0:
            overlay = frame.copy()
            # Color gradient simulation: red on top, green on bottom
            color = (0, int(255 - min(1.0, volume_proxy)*100), int(min(1.0, volume_proxy)*255))
            cv2.rectangle(overlay, (x, y_bottom), (x + bar_width, y_top), color, -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
