import time

try:
    import rtmidi
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False

class MidiBridge:
    def __init__(self):
        self.enabled = False
        self.midiout = None
        self.is_setup = False
        
        if MIDI_AVAILABLE:
            try:
                self.midiout = rtmidi.MidiOut()
                available_ports = self.midiout.get_ports()
                
                if available_ports:
                    self.midiout.open_port(0)
                else:
                    self.midiout.open_virtual_port("AirInstrument MIDI")
                self.is_setup = True
                print("MIDI Bridge initialized.")
            except Exception as e:
                print(f"Failed to initialize MIDI: {e}")
                
    def toggle(self):
        if not self.is_setup:
            print("MIDI not available or failed to initialize.")
            return False
            
        self.enabled = not self.enabled
        return self.enabled
        
    def send_note_on(self, channel=0, note=60, velocity=112):
        """Send a Note On message."""
        if not self.enabled or not self.is_setup:
            return
        # [0x90 + channel, note, velocity]
        msg = [0x90 + channel, note, velocity]
        self.midiout.send_message(msg)
        
    def send_note_off(self, channel=0, note=60):
        """Send a Note Off message."""
        if not self.enabled or not self.is_setup:
            return
        # [0x80 + channel, note, 0]
        msg = [0x80 + channel, note, 0]
        self.midiout.send_message(msg)
        
    def map_y_to_midi(self, y_pos):
        """Maps Y position to MIDI note numbers (e.g., 48 to 72)"""
        # C3 (48) to C5 (72)
        min_note = 48
        max_note = 72
        note_range = max_note - min_note
        
        # y=0 is top, y=1 is bottom. High y -> low note
        idx = int((1.0 - y_pos) * note_range)
        note = min_note + max(0, min(note_range, idx))
        return note

    def process_gesture_midi(self, gesture, hand_data):
        if not self.enabled:
            return
            
        gesture_lower = gesture.lower()
        if "index" in gesture_lower:
            y_pos = hand_data['index_tip'][1]
            note = self.map_y_to_midi(y_pos)
            
            volume = max(0.1, min(1.0, hand_data['size'] * 6.0))
            speed = hand_data['speed']
            velocity = int(min(127, volume * 127 + speed * 10))
            
            # Simple implementation: send note on
            # A more robust system would track active notes
            self.send_note_on(note=note, velocity=velocity)
            
        elif "pinch" in gesture_lower:
            # Send All Notes Off (CC 123)
            msg = [0xB0, 123, 0]
            self.midiout.send_message(msg)
