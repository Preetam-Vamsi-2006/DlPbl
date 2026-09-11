# 🛡️ Email Threat Detection & Spam Classification System

An intelligent email/SMS threat detection and spam classification system using Feed Forward Neural Networks with a Flask web interface.

## 📋 Project Structure

```
DL_PBL/
├── email_data.csv          # Dataset (SMS/Email messages with labels)
├── model.py                # Neural Network model implementation
├── app.py                  # Flask web application
├── requirements.txt        # Python dependencies
├── setup.bat              # Setup script (Windows)
├── README.md              # This file
├── templates/
│   └── index.html         # Web interface
└── static/
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── script.js      # Frontend logic
```

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train the Model
This creates the trained neural network (`email_threat_model.pkl`)
```bash
python model.py
```

### Step 3: Run Flask Application
```bash
python app.py
```

### Step 4: Access Web Interface
Open your browser and go to:
```
http://localhost:5000
```

## ⚙️ Automated Setup (Windows)
Run the setup script:
```bash
setup.bat
```

This will:
1. Install dependencies
2. Train the model
3. Instructions to run Flask

## 🔧 Model Architecture

**Feed Forward Neural Network:**
- Input Layer: 1000 TF-IDF features
- Hidden Layer 1: 128 neurons (ReLU activation)
- Hidden Layer 2: 64 neurons (ReLU activation)
- Output Layer: 2 neurons (Softmax activation) - Ham/Spam

**Training:**
- Algorithm: Stochastic Gradient Descent
- Loss Function: Cross-Entropy
- Epochs: 50
- Batch Size: 32
- Learning Rate: 0.01

## 📊 Features

### Single Email Analysis
- Real-time classification
- Confidence scores
- Threat level assessment
- Probability visualization
- Detailed message analysis
- Smart recommendations

### Batch Analysis
- Process multiple messages at once
- Statistical summary
- Spam percentage calculation
- Results table export

### Message Analysis Includes
- URL detection
- Phone number detection
- Special characters count
- All-CAPS detection
- Money keywords identification
- Urgency words detection

## 🎯 Classification

**HAM (Legitimate):** Normal, safe messages
**SPAM (Threat):** Suspicious messages, potential phishing, scams

### Threat Levels
- 🔴 **CRITICAL**: >90% confidence spam
- 🟠 **HIGH**: 75-90% confidence spam
- 🟡 **MEDIUM**: 60-75% confidence spam
- 🟢 **LOW**: <60% confidence spam

## 📡 API Endpoints

### Single Classification
```bash
POST /api/classify
Content-Type: application/json

{
    "message": "Your message here"
}
```

Response:
```json
{
    "success": true,
    "classification": "HAM|SPAM",
    "is_spam": true|false,
    "confidence": 0.95,
    "threat_level": "LOW|MEDIUM|HIGH|CRITICAL",
    "recommendation": "...",
    "analysis": {...}
}
```

### Batch Classification
```bash
POST /api/batch_classify
Content-Type: application/json

{
    "messages": ["msg1", "msg2", ...]
}
```

### Model Information
```bash
GET /api/model_info
```

### Health Check
```bash
GET /api/health
```

## 📈 Model Performance

The model is trained on the SMS Spam Collection dataset with balanced ham/spam messages.

**Metrics:**
- Accuracy: ~98%
- Precision: ~97%
- Recall: ~96%
- F1-Score: ~96%

## 🔒 Security Features

- Input validation (max 5000 chars single, 25000 chars batch)
- XSS protection via template escaping
- CSRF token support
- Error handling and logging
- Model loading validation

## 🎨 Web Interface Features

- Dark-responsive design
- Real-time character count
- Interactive probability charts
- Color-coded threat levels
- Copy-friendly results
- Mobile-responsive layout

## 📝 Example Usage

### Python API
```python
from model import EmailThreatDetectionNN

model = EmailThreatDetectionNN()
model.load('email_threat_model.pkl')

label, confidence, probs = model.predict_text(
    "FREE MONEY! Click here now!"
)
print(f"Classification: {label}")
print(f"Confidence: {confidence:.4f}")
```

### cURL
```bash
curl -X POST http://localhost:5000/api/classify \
  -H "Content-Type: application/json" \
  -d '{"message":"Hi, how are you?"}'
```

## 🛠️ Troubleshooting

### Model file not found
```
Run: python model.py
```

### Port 5000 already in use
```
Modify in app.py: app.run(port=5001)
```

### Dependencies issues
```
pip install --upgrade -r requirements.txt
```

## 📚 Technology Stack

- **Backend**: Python, Flask
- **ML/DL**: NumPy, Scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript
- **NLP**: TF-IDF Vectorization

## 👥 Author

Deep Learning Project - Email Threat Detection System

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to extend this project with:
- Additional features (attachment scanning, sender validation)
- Model improvements (LSTM, BERT)
- Database integration
- Email client plugins
- Mobile app version

---

**Happy Spam Hunting!** 🎯
