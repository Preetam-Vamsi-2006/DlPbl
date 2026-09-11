"""
Flask Application for Email Threat Detection and Spam Classification
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from model import EmailThreatDetectionNN
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'email_threat_detection_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Global model variable
model = None

def load_model():
    """Load the trained model"""
    global model
    model_path = 'email_threat_model.pkl'
    
    if os.path.exists(model_path):
        model = EmailThreatDetectionNN()
        model.load(model_path)
        print("Model loaded successfully!")
        return True
    else:
        print(f"Model file not found: {model_path}")
        return False

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/classify', methods=['POST'])
def classify_email():
    """
    API endpoint for email classification
    
    Expected JSON:
    {
        "message": "email text here"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        message = data['message'].strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        if len(message) > 5000:
            return jsonify({
                'success': False,
                'error': 'Message is too long (max 5000 characters)'
            }), 400
        
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please train the model first.'
            }), 500
        
        # Make prediction
        label, confidence, probs = model.predict_text(message)
        
        # Determine threat level
        is_spam = label.lower() == 'spam'
        threat_level = calculate_threat_level(confidence, is_spam)
        
        response = {
            'success': True,
            'classification': label.upper(),
            'is_spam': is_spam,
            'confidence': float(confidence),
            'spam_probability': float(probs[1]) if len(probs) > 1 else 0,
            'ham_probability': float(probs[0]) if len(probs) > 0 else 0,
            'threat_level': threat_level,
            'recommendation': get_recommendation(is_spam, confidence),
            'analysis': analyze_message(message, label)
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Classification error: {str(e)}'
        }), 500

@app.route('/api/batch_classify', methods=['POST'])
def batch_classify():
    """
    API endpoint for batch classification
    
    Expected JSON:
    {
        "messages": ["message1", "message2", ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({
                'success': False,
                'error': 'No messages provided'
            }), 400
        
        messages = data['messages']
        
        if not isinstance(messages, list):
            return jsonify({
                'success': False,
                'error': 'Messages should be a list'
            }), 400
        
        if len(messages) > 100:
            return jsonify({
                'success': False,
                'error': 'Too many messages (max 100)'
            }), 400
        
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded'
            }), 500
        
        results = []
        for msg in messages:
            msg = str(msg).strip()
            if msg:
                label, confidence, probs = model.predict_text(msg)
                is_spam = label.lower() == 'spam'
                
                results.append({
                    'message': msg[:100] + '...' if len(msg) > 100 else msg,
                    'classification': label.upper(),
                    'is_spam': is_spam,
                    'confidence': float(confidence),
                    'threat_level': calculate_threat_level(confidence, is_spam)
                })
        
        stats = {
            'total': len(results),
            'spam_count': sum(1 for r in results if r['is_spam']),
            'ham_count': sum(1 for r in results if not r['is_spam']),
            'spam_percentage': (sum(1 for r in results if r['is_spam']) / len(results) * 100) if results else 0
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'statistics': stats
        }), 200
    
    except Exception as e:
        print(f"Error in batch classification: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Batch classification error: {str(e)}'
        }), 500

@app.route('/api/model_info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 500
    
    # Basic model info
    info = {
        'hidden_layers': model.hidden_layers,
        'learning_rate': model.learning_rate,
        'epochs': model.epochs,
        'batch_size': model.batch_size,
        'classes': list(model.label_encoder.classes_),
        'vocabulary_size': len(model.vectorizer.vocabulary_)
    }
    
    # Add evaluation metrics if available
    if hasattr(model, 'evaluation_metrics') and model.evaluation_metrics:
        metrics = model.evaluation_metrics
        info['evaluation'] = {
            'accuracy': round(metrics.get('accuracy', 0), 4),
            'precision': round(metrics.get('precision', 0), 4),
            'recall': round(metrics.get('recall', 0), 4),
            'f1_score': round(metrics.get('f1_score', 0), 4),
            'training_accuracy': round(metrics.get('training_accuracy', 0), 4),
            'training_loss': round(metrics.get('training_loss', 0), 4),
            'train_samples': metrics.get('train_samples', 0),
            'test_samples': metrics.get('test_samples', 0),
            'total_samples': metrics.get('total_samples', 0),
            'confusion_matrix': metrics.get('confusion_matrix', []),
            'classes': metrics.get('classes', [])
        }
    
    return jsonify({
        'success': True,
        'model_info': info
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    }), 200

def calculate_threat_level(confidence, is_spam):
    """Calculate threat level based on classification and confidence"""
    if not is_spam:
        return 'LOW'
    
    if confidence >= 0.9:
        return 'CRITICAL'
    elif confidence >= 0.75:
        return 'HIGH'
    elif confidence >= 0.6:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_recommendation(is_spam, confidence):
    """Get recommendation based on classification"""
    if not is_spam:
        return 'Message appears legitimate. Safe to read.'
    
    if confidence >= 0.9:
        return 'CRITICAL: Delete immediately. Highly likely to be spam/threat.'
    elif confidence >= 0.75:
        return 'WARNING: Likely spam. Review before taking any action.'
    elif confidence >= 0.6:
        return 'CAUTION: Possibly spam. Verify sender before engaging.'
    else:
        return 'REVIEW: Message characteristics suggest spam. Check carefully.'

def analyze_message(message, classification):
    """Provide detailed analysis of the message"""
    analysis = {
        'length': len(message),
        'word_count': len(message.split()),
        'has_urls': 'http://' in message.lower() or 'https://' in message.lower() or 'www.' in message.lower(),
        'has_phone_numbers': any(char.isdigit() for char in message) and len([c for c in message if c.isdigit()]) >= 5,
        'has_special_characters': sum(1 for c in message if c in '!@#$%^&*()') > 0,
        'has_all_caps': sum(1 for c in message if c.isupper()) > len(message) * 0.3,
        'contains_money_keywords': any(keyword in message.lower() for keyword in ['win', 'prize', 'free', 'cash', 'pound', '£', '$', 'money']),
        'contains_urgency': any(keyword in message.lower() for keyword in ['urgent', 'immediately', 'now', 'asap', 'limited', 'only'])
    }
    
    return analysis

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.before_request
def before_request():
    """Check model before each request"""
    global model
    if model is None and request.endpoint and 'api' in request.endpoint:
        if request.endpoint != 'health_check':
            pass  # Will be handled in individual routes

# Load model on startup
print("Loading Email Threat Detection Model...")
load_model()

if __name__ == '__main__':
    if model is None:
        print("Failed to load model. Please train the model first using: python model.py")
        sys.exit(1)
    
    print("Starting Flask application...")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )
