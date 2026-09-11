"""
Quick test script for the email threat detection model
"""

import pandas as pd
from model import EmailThreatDetectionNN
import os

print("="*60)
print("EMAIL THREAT DETECTION - TEST SCRIPT")
print("="*60)

# Check if model exists
model_path = 'email_threat_model.pkl'
if not os.path.exists(model_path):
    print("\n❌ Model not found! Training new model...\n")
    
    # Load data
    df = pd.read_csv('email_data.csv')
    
    # Create and train
    model = EmailThreatDetectionNN(
        hidden_layers=[128, 64],
        learning_rate=0.1,
        epochs=50,
        batch_size=32
    )
    
    model.fit(df['Message'].values, df['Category'].values)
    model.save(model_path)
else:
    print(f"\n✅ Loading existing model from {model_path}...\n")
    model = EmailThreatDetectionNN()
    model.load(model_path)

print("\n" + "="*60)
print("TESTING WITH SAMPLE MESSAGES")
print("="*60)

# Test messages
test_cases = [
    {
        "text": "Hi, how are you doing today?",
        "expected": "ham"
    },
    {
        "text": "FREE MONEY! You have won a 1 week FREE membership in our £100,000 Prize Jackpot! Txt the word: CLAIM to No: 81010",
        "expected": "spam"
    },
    {
        "text": "Ok lar... Joking wif u oni...",
        "expected": "ham"
    },
    {
        "text": "WINNER!! As a valued network customer you have been selected to receive a £900 prize reward! To claim call 09061701461",
        "expected": "spam"
    },
    {
        "text": "I'm gonna be home soon and i don't want to talk about this stuff anymore tonight, k?",
        "expected": "ham"
    },
    {
        "text": "FreeMsg Why haven't you replied to my text? I'm Randy, sexy, female and live local. Netcollex Ltd",
        "expected": "spam"
    }
]

results = {
    'correct': 0,
    'wrong': 0,
    'total': len(test_cases)
}

for idx, test in enumerate(test_cases, 1):
    label, confidence, probs = model.predict_text(test['text'])
    is_correct = label.lower() == test['expected'].lower()
    
    status = "✅ CORRECT" if is_correct else "❌ WRONG"
    results['correct'] += is_correct
    results['wrong'] += not is_correct
    
    print(f"\nTest {idx}: {status}")
    print(f"  Message: {test['text'][:60]}...")
    print(f"  Expected: {test['expected'].upper()}")
    print(f"  Got: {label.upper()}")
    print(f"  Confidence: {confidence*100:.2f}%")
    print(f"  Probabilities - Ham: {probs[0]*100:.2f}%, Spam: {probs[1]*100:.2f}%")

print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Correct: {results['correct']}/{results['total']}")
print(f"Wrong: {results['wrong']}/{results['total']}")
print(f"Accuracy: {(results['correct']/results['total']*100):.1f}%")
print("="*60)

if results['correct'] == results['total']:
    print("\n🎉 ALL TESTS PASSED! Model is working correctly!")
elif results['correct'] >= results['total'] * 0.8:
    print("\n⚠️ Model is working but not perfectly. This is normal.")
else:
    print("\n❌ Model needs improvement. Check the training process.")
