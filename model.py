"""
Feed Forward Neural Network for Email Threat Detection and Spam Classification
"""

import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')

class EmailThreatDetectionNN:
    """Feed Forward Neural Network for Email Threat Detection"""
    
    def __init__(self, hidden_layers=[128, 64], learning_rate=0.01, epochs=50, batch_size=32):
        """
        Initialize the neural network
        
        Args:
            hidden_layers: List of hidden layer sizes
            learning_rate: Learning rate for gradient descent
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.label_encoder = LabelEncoder()
        
        self.weights = []
        self.biases = []
        self.history = {'loss': [], 'accuracy': []}
        
    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """ReLU derivative"""
        return (x > 0).astype(float)
    
    def sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, x):
        """Sigmoid derivative"""
        return x * (1 - x)
    
    def softmax(self, x):
        """Softmax activation for output layer"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def initialize_weights(self, input_size, output_size):
        """Initialize weights and biases"""
        layer_sizes = [input_size] + self.hidden_layers + [output_size]
        
        for i in range(len(layer_sizes) - 1):
            # He initialization for better convergence
            std = np.sqrt(2.0 / layer_sizes[i])
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * std
            b = np.zeros((1, layer_sizes[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def forward_propagation(self, X):
        """Forward propagation"""
        self.activations = [X]
        self.z_values = []
        
        current = X
        
        # Hidden layers with ReLU
        for i in range(len(self.weights) - 1):
            z = np.dot(current, self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            current = self.relu(z)
            self.activations.append(current)
        
        # Output layer with Softmax
        z = np.dot(current, self.weights[-1]) + self.biases[-1]
        self.z_values.append(z)
        output = self.softmax(z)
        self.activations.append(output)
        
        return output
    
    def backward_propagation(self, y, output, batch_size):
        """Backward propagation"""
        m = batch_size
        
        # Output layer error
        delta = output - y
        
        # Backpropagate through layers
        for i in range(len(self.weights) - 1, -1, -1):
            # Gradient calculations
            dw = np.dot(self.activations[i].T, delta) / m
            db = np.sum(delta, axis=0, keepdims=True) / m
            
            # Update weights and biases
            self.weights[i] -= self.learning_rate * dw
            self.biases[i] -= self.learning_rate * db
            
            # Propagate error to previous layer
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self.relu_derivative(self.z_values[i-1])
    
    def compute_loss(self, y, output):
        """Compute cross-entropy loss"""
        m = y.shape[0]
        log_likelihood = -np.log(output[range(m), np.argmax(y, axis=1)] + 1e-8)
        loss = np.sum(log_likelihood) / m
        return loss
    
    def train(self, X_train, y_train, X_val=None, y_val=None, verbose=True):
        """Train the neural network"""
        m = X_train.shape[0]
        
        for epoch in range(self.epochs):
            # Shuffle data
            indices = np.random.permutation(m)
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            # Mini-batch training
            for start_idx in range(0, m, self.batch_size):
                end_idx = min(start_idx + self.batch_size, m)
                X_batch = X_shuffled[start_idx:end_idx]
                y_batch = y_shuffled[start_idx:end_idx]
                
                # Forward and backward propagation
                output = self.forward_propagation(X_batch)
                self.backward_propagation(y_batch, output, end_idx - start_idx)
            
            # Compute metrics
            train_output = self.forward_propagation(X_train)
            train_loss = self.compute_loss(y_train, train_output)
            train_pred = np.argmax(train_output, axis=1)
            train_true = np.argmax(y_train, axis=1)
            train_acc = accuracy_score(train_true, train_pred)
            
            self.history['loss'].append(train_loss)
            self.history['accuracy'].append(train_acc)
            
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{self.epochs} - Loss: {train_loss:.4f} - Accuracy: {train_acc:.4f}")
    
    def predict(self, X):
        """Make predictions"""
        output = self.forward_propagation(X)
        predictions = np.argmax(output, axis=1)
        probabilities = np.max(output, axis=1)
        return predictions, probabilities, output
    
    def fit(self, X_texts, y_labels):
        """Complete training pipeline"""
        # Vectorize texts
        X_vectorized = self.vectorizer.fit_transform(X_texts).toarray()
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y_labels)
        y_one_hot = np.eye(len(self.label_encoder.classes_))[y_encoded]
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_vectorized, y_one_hot, test_size=0.2, random_state=42
        )
        
        # Initialize network
        self.initialize_weights(X_train.shape[1], y_one_hot.shape[1])
        
        # Train
        self.train(X_train, y_train, X_val, y_val)
        
        # Evaluate
        y_pred, y_probs, _ = self.predict(X_val)
        y_val_true = np.argmax(y_val, axis=1)
        
        # Calculate comprehensive metrics
        accuracy = accuracy_score(y_val_true, y_pred)
        precision = precision_score(y_val_true, y_pred, average='weighted')
        recall = recall_score(y_val_true, y_pred, average='weighted')
        f1 = f1_score(y_val_true, y_pred, average='weighted')
        cm = confusion_matrix(y_val_true, y_pred)
        
        # Store evaluation metrics
        self.evaluation_metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': cm.tolist(),
            'classes': list(self.label_encoder.classes_),
            'total_samples': len(y_val_true),
            'train_samples': len(y_train),
            'test_samples': len(y_val),
            'training_loss': float(self.history['loss'][-1]) if self.history['loss'] else 0,
            'training_accuracy': float(self.history['accuracy'][-1]) if self.history['accuracy'] else 0
        }
        
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(
            y_val_true, y_pred, 
            target_names=self.label_encoder.classes_
        ))
        print("="*50)
        
        return self
    
    def predict_text(self, text):
        """Predict for a single text"""
        X = self.vectorizer.transform([text]).toarray()
        pred, prob, output = self.predict(X)
        label = self.label_encoder.inverse_transform(pred)[0]
        return label, float(prob[0]), output[0]
    
    def save(self, filepath):
        """Save model and vectorizer"""
        model_data = {
            'weights': self.weights,
            'biases': self.biases,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder,
            'hidden_layers': self.hidden_layers,
            'learning_rate': self.learning_rate,
            'evaluation_metrics': getattr(self, 'evaluation_metrics', {})
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model and vectorizer"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.weights = model_data['weights']
        self.biases = model_data['biases']
        self.vectorizer = model_data['vectorizer']
        self.label_encoder = model_data['label_encoder']
        self.hidden_layers = model_data['hidden_layers']
        self.learning_rate = model_data['learning_rate']
        self.evaluation_metrics = model_data.get('evaluation_metrics', {})
        
        print(f"Model loaded from {filepath}")
        return self


def train_model():
    """Train the email threat detection model"""
    # Load data
    df = pd.read_csv('email_data.csv')
    
    print("="*50)
    print("EMAIL THREAT DETECTION MODEL TRAINING")
    print("="*50)
    print(f"Total samples: {len(df)}")
    print(f"Ham messages: {sum(df['Category'] == 'ham')}")
    print(f"Spam messages: {sum(df['Category'] == 'spam')}")
    print("="*50)
    
    # Create and train model
    model = EmailThreatDetectionNN(
        hidden_layers=[128, 64],
        learning_rate=0.1,
        epochs=50,
        batch_size=32
    )
    
    model.fit(df['Message'].values, df['Category'].values)
    
    # Save model
    model.save('email_threat_model.pkl')
    
    return model


if __name__ == '__main__':
    model = train_model()
    
    # Test predictions
    test_messages = [
        "Hi there, how are you doing today?",
        "FREE MONEY! Win £1000 today! Click here now!",
        "Let me know when you're available for a meeting"
    ]
    
    print("\n" + "="*50)
    print("SAMPLE PREDICTIONS")
    print("="*50)
    
    for msg in test_messages:
        label, confidence, probs = model.predict_text(msg)
        print(f"Message: {msg[:50]}...")
        print(f"Classification: {label.upper()}")
        print(f"Confidence: {confidence:.4f}")
        print(f"Spam Probability: {probs[1]:.4f}")
        print("-" * 50)
