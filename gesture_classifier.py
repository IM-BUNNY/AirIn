import os
import csv
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import joblib

class GestureClassifier:
    def __init__(self, data_path='data/gesture_data.csv', model_path='models/gesture_model.pkl'):
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Loads the trained model if it exists."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print("No trained model found. Please collect data and train.")
            
    def save_sample(self, keypoints, label):
        """Saves a 42-dimensional keypoint vector and its label to the CSV."""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        file_exists = os.path.isfile(self.data_path)
        
        with open(self.data_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                # write header: x0, y0, ... x20, y20, label
                header = []
                for i in range(21):
                    header.extend([f'x{i}', f'y{i}'])
                header.append('label')
                writer.writerow(header)
            
            row = list(keypoints) + [label]
            writer.writerow(row)
            print(f"Saved sample for gesture: {label}")
            
    def train(self):
        """Trains the MLP Classifier on the collected data."""
        if not os.path.exists(self.data_path):
            print("No data found for training.")
            return False
            
        X = []
        y = []
        with open(self.data_path, mode='r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) == 43:
                    features = [float(val) for val in row[:42]]
                    label = row[42]
                    X.append(features)
                    y.append(label)
                    
        if len(X) < 10:
            print("Not enough data to train. Please collect more samples.")
            return False
            
        print(f"Training model on {len(X)} samples...")
        # Using MLPClassifier for real-time classification speed
        self.model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
        
        self.model.fit(X, y)
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model trained and saved to {self.model_path}")
        return True
        
    def predict(self, keypoints):
        """Predicts the gesture from keypoints."""
        if self.model is None:
            return "Unknown"
        
        # Reshape to 2D array for prediction
        X = np.array(keypoints).reshape(1, -1)
        pred = self.model.predict(X)
        return pred[0]
