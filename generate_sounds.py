import math
import wave
import struct
import os
import random

def generate_tone(filename, frequency, duration=0.5, volume=0.5, wave_type='piano'):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            
            if wave_type == 'piano':
                envelope = math.exp(-3.0 * t / duration)
                value = (math.sin(2.0 * math.pi * frequency * t) + 
                         0.5 * math.sin(2.0 * math.pi * frequency * 2 * t) + 
                         0.25 * math.sin(2.0 * math.pi * frequency * 3 * t) + 
                         0.125 * math.sin(2.0 * math.pi * frequency * 4 * t)) / 1.875
            elif wave_type == 'guitar':
                # Distorted power chord (root + fifth) for a distinct rock guitar sound
                envelope = math.exp(-1.5 * t / duration)
                # Sawtooth for root
                root = 2.0 * (t * frequency - math.floor(0.5 + t * frequency))
                # Sawtooth for fifth (freq * 1.498)
                fifth = 2.0 * (t * (frequency * 1.498) - math.floor(0.5 + t * (frequency * 1.498)))
                # Distortion clipping
                mix = (root + fifth * 0.8) * 4.0
                mix = max(-1.0, min(1.0, mix)) # Hard clip
                # Soften high-end slightly
                value = mix * 0.4
            elif wave_type == 'kick':
                freq_drop = frequency * math.exp(-25.0 * t)
                value = math.sin(2.0 * math.pi * freq_drop * t)
                envelope = math.exp(-15.0 * t / duration)
            elif wave_type == 'snare':
                sine_env = math.exp(-30.0 * t)
                noise_env = math.exp(-10.0 * t)
                sine_part = math.sin(2.0 * math.pi * 180.0 * t) * sine_env
                noise_part = random.uniform(-1.0, 1.0) * noise_env
                value = (sine_part + noise_part) / 2.0
                envelope = 1.0
            elif wave_type == 'hihat':
                envelope = math.exp(-40.0 * t)
                value = random.uniform(-1.0, 1.0) * math.sin(2.0 * math.pi * 10000.0 * t)
            else:
                value = 0
                envelope = 0
                
            # Scale to 16-bit integer
            int_value = int(value * volume * envelope * 32767.0)
            int_value = max(-32768, min(32767, int_value))
            
            data = struct.pack('<h', int_value)
            wav_file.writeframesraw(data)

# Frequencies for piano
notes = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
}

print("Generating realistic Piano notes...")
for name, freq in notes.items():
    generate_tone(f'sounds/piano/{name}.wav', freq, duration=2.0, wave_type='piano', volume=0.8)

print("Generating realistic Drum sounds...")
generate_tone('sounds/drums/kick.wav', 180.0, duration=0.4, wave_type='kick', volume=1.0)
generate_tone('sounds/drums/snare.wav', 200.0, duration=0.3, wave_type='snare', volume=0.9)
generate_tone('sounds/drums/hihat.wav', 8000.0, duration=0.1, wave_type='hihat', volume=0.6)

print("Generating distorted Guitar chords...")
chords = {
    'chord_C': 130.81, # C3
    'chord_G': 98.00,  # G2
    'chord_D': 146.83, # D3
    'chord_Am': 110.00 # A2
}
for name, freq in chords.items():
    generate_tone(f'sounds/guitar/{name}.wav', freq, duration=3.0, wave_type='guitar', volume=0.9)

print("All synthetic audio files generated successfully!")
