import pygame
import time
import os

class SoundEngine:
    def __init__(self, buffer_size=512):
        # Initialize pygame mixer with low latency settings
        try:
            pygame.mixer.pre_init(44100, -16, 2, buffer_size)
            pygame.mixer.init()
        except Exception as e:
            print(f"Failed to initialize pygame mixer: {e}")
            
        self.sounds = {
            'Piano': {},
            'Drums': {},
            'Guitar': {}
        }
        
        self.instruments = ['Piano', 'Drums', 'Guitar']
        self.active_instrument_idx = 0
        
        # For cooldowns
        self.last_played_time = {}
        self.cooldown = 0.150 # 150ms
        
        self.load_dummy_sounds()
        
    def get_active_instrument(self):
        return self.instruments[self.active_instrument_idx]
        
    def switch_instrument(self):
        self.active_instrument_idx = (self.active_instrument_idx + 1) % len(self.instruments)
        return self.get_active_instrument()
        
    def set_instrument(self, idx):
        if 0 <= idx < len(self.instruments):
            self.active_instrument_idx = idx
            
    def load_dummy_sounds(self):
        """Loads dummy sounds to avoid crashing if files are missing."""
        # Notes for piano mapping C3 to C5
        self.notes = ['C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        
        for note in self.notes:
            path = f'sounds/piano/{note}.wav'
            if os.path.exists(path):
                self.sounds['Piano'][note] = pygame.mixer.Sound(path)
            else:
                self.sounds['Piano'][note] = None
                
        drum_files = {'kick': 'kick.wav', 'snare': 'snare.wav', 'hihat': 'hihat.wav'}
        for name, file in drum_files.items():
            path = f'sounds/drums/{file}'
            if os.path.exists(path):
                self.sounds['Drums'][name] = pygame.mixer.Sound(path)
            else:
                self.sounds['Drums'][name] = None
                
        guitar_files = {'chord_C': 'chord_C.wav', 'chord_G': 'chord_G.wav', 'chord_D': 'chord_D.wav', 'chord_Am': 'chord_Am.wav'}
        for name, file in guitar_files.items():
            path = f'sounds/guitar/{file}'
            if os.path.exists(path):
                self.sounds['Guitar'][name] = pygame.mixer.Sound(path)
            else:
                self.sounds['Guitar'][name] = None
                
    def play_sound(self, instrument, note_or_name, volume=1.0):
        current_time = time.time()
        key = f"{instrument}_{note_or_name}"
        
        if key in self.last_played_time:
            if current_time - self.last_played_time[key] < self.cooldown:
                return False # Cooldown active
                
        sound = self.sounds.get(instrument, {}).get(note_or_name)
        if sound:
            # Map hand size / velocity to volume
            sound.set_volume(max(0.0, min(1.0, volume)))
            sound.play()
            
        self.last_played_time[key] = current_time
        return True
        
    def stop_all(self):
        pygame.mixer.stop()
        
    def map_y_to_note(self, y_pos):
        """Maps a Y coordinate [0.0, 1.0] to a note."""
        # Y=0 is top, Y=1 is bottom
        # Let's map high Y (bottom) to lower notes, low Y (top) to higher notes
        idx = int((1.0 - y_pos) * len(self.notes))
        idx = max(0, min(len(self.notes)-1, idx))
        return self.notes[idx]
        
    def process_gesture(self, gesture, hand_data):
        """Triggers sounds based on gesture and hand data."""
        instrument = self.get_active_instrument()
        triggered_note = None
        
        # Calculate volume based on hand size (larger hand = closer = louder)
        # Assuming size ranges approximately from 0.05 to 0.3
        volume = max(0.1, min(1.0, hand_data['size'] * 6.0))
        
        # Add velocity to intensity
        speed = hand_data['speed']
        intensity_mult = 1.0 + min(2.0, speed)
        final_volume = min(1.0, volume * intensity_mult)
        
        gesture_lower = gesture.lower()
        
        if "fist" in gesture_lower:
            # Drum hit on fast movement
            if speed > 0.5:
                # Map X position to different drums
                x_pos = hand_data['index_tip'][0]
                if x_pos < 0.33:
                    note = 'hihat'
                elif x_pos < 0.66:
                    note = 'snare'
                else:
                    note = 'kick'
                    
                if instrument == 'Drums':
                    if self.play_sound('Drums', note, final_volume):
                        triggered_note = note
                else:
                    # Allow fist to trigger kick drum globally
                    if self.play_sound('Drums', 'kick', final_volume):
                        triggered_note = 'kick'
                        
        elif "index" in gesture_lower:
            y_pos = hand_data['index_tip'][1]
            if instrument == 'Piano':
                note = self.map_y_to_note(y_pos)
                if self.play_sound('Piano', note, final_volume):
                    triggered_note = note
            elif instrument == 'Guitar':
                x_pos = hand_data['index_tip'][0]
                chords = list(self.sounds['Guitar'].keys())
                if chords:
                    idx = int(x_pos * len(chords))
                    idx = max(0, min(len(chords)-1, idx))
                    note = chords[idx]
                    if self.play_sound('Guitar', note, final_volume):
                        triggered_note = note
                        
        elif "pinch" in gesture_lower:
            current_time = time.time()
            self.stop_all()
            if current_time - self.last_played_time.get("MUTE", 0) > 0.5:
                triggered_note = "MUTE"
                self.last_played_time["MUTE"] = current_time
            
        elif "palm" in gesture_lower:
            # Sustain or swell (in a real implementation, might adjust ongoing volume)
            pass
            
        return triggered_note
