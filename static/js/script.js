// Email Threat Detection - Frontend Script

let modelInfo = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadModelInfo();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const emailInput = document.getElementById('emailInput');
    const batchInput = document.getElementById('batchInput');

    if (emailInput) {
        emailInput.addEventListener('input', updateCharCount);
    }
    if (batchInput) {
        batchInput.addEventListener('input', updateBatchCharCount);
    }
}

// Update character count for single email
function updateCharCount() {
    const input = document.getElementById('emailInput');
    const count = input.value.length;
    document.getElementById('charCount').textContent = count;
    
    if (count > 5000) {
        input.value = input.value.substring(0, 5000);
        document.getElementById('charCount').textContent = 5000;
    }
}

// Update character count for batch
function updateBatchCharCount() {
    const input = document.getElementById('batchInput');
    const count = input.value.length;
    document.getElementById('batchCharCount').textContent = count;
    
    if (count > 25000) {
        input.value = input.value.substring(0, 25000);
        document.getElementById('batchCharCount').textContent = 25000;
    }
}

// Load model information
async function loadModelInfo() {
    try {
        const response = await fetch('/api/model_info');
        const data = await response.json();
        
        if (data.success) {
            modelInfo = data.model_info;
            displayModelInfo(data.model_info);
            updateStatusIndicator(true);
        } else {
            updateStatusIndicator(false);
        }
    } catch (error) {
        console.error('Error loading model info:', error);
        updateStatusIndicator(false);
    }
}

// Display model information
function displayModelInfo(info) {
    const container = document.getElementById('modelInfo');
    
    const html = `
        <div class="info-item">
            <div class="info-label">Architecture</div>
            <div class="info-value">Feed Forward NN</div>
        </div>
        <div class="info-item">
            <div class="info-label">Hidden Layers</div>
            <div class="info-value">${info.hidden_layers.join(' → ')}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Learning Rate</div>
            <div class="info-value">${info.learning_rate}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Epochs</div>
            <div class="info-value">${info.epochs}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Batch Size</div>
            <div class="info-value">${info.batch_size}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Classes</div>
            <div class="info-value">${info.classes.join(', ').toUpperCase()}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Vocabulary Size</div>
            <div class="info-value">${info.vocabulary_size.toLocaleString()}</div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Display evaluation metrics if available
    if (info.evaluation) {
        displayEvaluationMetrics(info.evaluation);
    }
}

// Update status indicator
function updateStatusIndicator(loaded) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');
    
    if (loaded) {
        dot.style.background = '#10b981';
        text.textContent = 'Model Ready';
    } else {
        dot.style.background = '#ef4444';
        text.textContent = 'Model Loading...';
    }
}

// Classify single email
async function classifyEmail() {
    const input = document.getElementById('emailInput');
    const message = input.value.trim();
    
    if (!message) {
        alert('Please enter a message to analyze');
        return;
    }
    
    const btn = document.getElementById('classifyBtn');
    const spinner = document.getElementById('loadingSpinner');
    const resultSection = document.getElementById('resultSection');
    
    btn.disabled = true;
    spinner.style.display = 'block';
    resultSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult(data);
            resultSection.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to classify message');
    } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
    }
}

// Display classification result
function displayResult(data) {
    const isSpam = data.is_spam;
    
    // Classification badge
    const badge = document.getElementById('classificationBadge');
    badge.className = 'classification-badge ' + (isSpam ? 'spam' : 'ham');
    badge.textContent = isSpam ? '⚠️ SPAM DETECTED' : '✅ LEGITIMATE MESSAGE';
    
    // Metrics
    document.getElementById('classLabel').textContent = data.classification;
    document.getElementById('confidenceScore').textContent = (data.confidence * 100).toFixed(2) + '%';
    
    const threatEl = document.getElementById('threatLevel');
    threatEl.textContent = data.threat_level;
    threatEl.className = 'metric-value threat threat-' + data.threat_level.toLowerCase();
    
    // Probability bars
    const hamPercent = (data.ham_probability * 100).toFixed(1);
    const spamPercent = (data.spam_probability * 100).toFixed(1);
    
    document.getElementById('hamBar').style.width = hamPercent + '%';
    document.getElementById('hamPercent').textContent = hamPercent + '%';
    document.getElementById('spamBar').style.width = spamPercent + '%';
    document.getElementById('spamPercent').textContent = spamPercent + '%';
    
    // Recommendation
    document.getElementById('recommendationText').textContent = data.recommendation;
    
    // Analysis
    displayAnalysis(data.analysis);
}

// Display message analysis
function displayAnalysis(analysis) {
    const grid = document.getElementById('analysisGrid');
    
    const items = [
        { label: 'Message Length', value: analysis.length + ' chars' },
        { label: 'Word Count', value: analysis.word_count + ' words' },
        { label: 'URLs Detected', value: analysis.has_urls ? '✓ Yes' : '✗ No', class: analysis.has_urls ? 'yes' : 'no' },
        { label: 'Phone Numbers', value: analysis.has_phone_numbers ? '✓ Yes' : '✗ No', class: analysis.has_phone_numbers ? 'yes' : 'no' },
        { label: 'Special Characters', value: analysis.has_special_characters ? '✓ Yes' : '✗ No', class: analysis.has_special_characters ? 'yes' : 'no' },
        { label: 'All CAPS', value: analysis.has_all_caps ? '✓ Yes' : '✗ No', class: analysis.has_all_caps ? 'yes' : 'no' },
        { label: 'Money Keywords', value: analysis.contains_money_keywords ? '✓ Yes' : '✗ No', class: analysis.contains_money_keywords ? 'yes' : 'no' },
        { label: 'Urgency Words', value: analysis.contains_urgency ? '✓ Yes' : '✗ No', class: analysis.contains_urgency ? 'yes' : 'no' }
    ];
    
    grid.innerHTML = items.map(item => `
        <div class="analysis-item">
            <div class="analysis-label">${item.label}</div>
            <div class="analysis-value ${item.class || ''}">${item.value}</div>
        </div>
    `).join('');
}

// Batch classify
async function batchClassify() {
    const input = document.getElementById('batchInput');
    const text = input.value.trim();
    
    if (!text) {
        alert('Please enter messages to analyze');
        return;
    }
    
    const messages = text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
    
    if (messages.length === 0) {
        alert('Please enter at least one message');
        return;
    }
    
    if (messages.length > 100) {
        alert('Maximum 100 messages allowed');
        return;
    }
    
    const btn = document.getElementById('batchBtn');
    const spinner = document.getElementById('batchLoadingSpinner');
    const resultSection = document.getElementById('batchResultSection');
    
    btn.disabled = true;
    spinner.style.display = 'block';
    resultSection.style.display = 'none';
    
    try {
        const response = await fetch('/api/batch_classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ messages: messages })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBatchResults(data.results, data.statistics);
            resultSection.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to classify messages');
    } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
    }
}

// Display batch results
function displayBatchResults(results, stats) {
    // Statistics
    const statsGrid = document.getElementById('statisticsGrid');
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Total Messages</div>
            <div class="stat-value">${stats.total}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Legitimate (Ham)</div>
            <div class="stat-value">${stats.ham_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Spam Detected</div>
            <div class="stat-value" style="color: #dc2626;">${stats.spam_count}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Spam Percentage</div>
            <div class="stat-value">${stats.spam_percentage.toFixed(1)}%</div>
        </div>
    `;
    
    // Results table
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = results.map((result, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${result.message}</td>
            <td><strong>${result.classification}</strong></td>
            <td>${(result.confidence * 100).toFixed(2)}%</td>
            <td><span class="threat-${result.threat_level.toLowerCase()}">${result.threat_level}</span></td>
        </tr>
    `).join('');
}

// Display evaluation metrics
function displayEvaluationMetrics(evaluation) {
    const section = document.getElementById('evaluationSection');
    const metricsContainer = document.getElementById('evaluationMetrics');
    
    if (!evaluation || Object.keys(evaluation).length === 0) {
        section.style.display = 'none';
        return;
    }
    
    // Create metrics cards
    const metricsHTML = `
        <div class="info-item">
            <div class="info-label">Accuracy</div>
            <div class="info-value" style="color: #10b981;">${(evaluation.accuracy * 100).toFixed(2)}%</div>
        </div>
        <div class="info-item">
            <div class="info-label">Precision</div>
            <div class="info-value" style="color: #2563eb;">${(evaluation.precision * 100).toFixed(2)}%</div>
        </div>
        <div class="info-item">
            <div class="info-label">Recall</div>
            <div class="info-value" style="color: #f59e0b;">${(evaluation.recall * 100).toFixed(2)}%</div>
        </div>
        <div class="info-item">
            <div class="info-label">F1-Score</div>
            <div class="info-value" style="color: #8b5cf6;">${(evaluation.f1_score * 100).toFixed(2)}%</div>
        </div>
        <div class="info-item">
            <div class="info-label">Training Accuracy</div>
            <div class="info-value">${(evaluation.training_accuracy * 100).toFixed(2)}%</div>
        </div>
        <div class="info-item">
            <div class="info-label">Training Loss</div>
            <div class="info-value">${evaluation.training_loss.toFixed(4)}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Training Samples</div>
            <div class="info-value">${evaluation.train_samples.toLocaleString()}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Test Samples</div>
            <div class="info-value">${evaluation.test_samples.toLocaleString()}</div>
        </div>
    `;
    
    metricsContainer.innerHTML = metricsHTML;
    section.style.display = 'block';
    
    // Display confusion matrix
    if (evaluation.confusion_matrix && evaluation.classes) {
        displayConfusionMatrix(evaluation.confusion_matrix, evaluation.classes);
    }
}

// Display confusion matrix
function displayConfusionMatrix(matrix, classes) {
    const container = document.getElementById('confusionMatrixContainer');
    
    if (!matrix || matrix.length === 0) return;
    
    let html = `
        <div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">
            <h4 style="margin-bottom: 15px; color: #1e293b;">Confusion Matrix</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #e5e7eb;">
                        <th style="padding: 10px; border: 1px solid #d1d5db; text-align: center;">Predicted →</th>
    `;
    
    // Header row
    for (let j = 0; j < classes.length; j++) {
        html += `<th style="padding: 10px; border: 1px solid #d1d5db; text-align: center;"><strong>${classes[j].toUpperCase()}</strong></th>`;
    }
    html += `</tr></thead><tbody>`;
    
    // Data rows
    for (let i = 0; i < matrix.length; i++) {
        html += `<tr>
            <th style="padding: 10px; border: 1px solid #d1d5db; text-align: center; background: #f9fafb;"><strong>${classes[i].toUpperCase()}</strong></th>`;
        for (let j = 0; j < matrix[i].length; j++) {
            const value = matrix[i][j];
            const bgColor = i === j ? '#d1fae5' : '#fef3c7';
            html += `<td style="padding: 10px; border: 1px solid #d1d5db; text-align: center; background: ${bgColor}; font-weight: bold;">${value}</td>`;
        }
        html += `</tr>`;
    }
    
    html += `</tbody></table>
        <p style="margin-top: 10px; font-size: 0.9rem; color: #64748b;">
            <strong>Note:</strong> Green cells = correct predictions (True Positives/Negatives), Yellow cells = incorrect predictions
        </p>
    </div>`;
    
    container.innerHTML = html;
}

// Clear functions
function clearInput() {
    document.getElementById('emailInput').value = '';
    document.getElementById('charCount').textContent = '0';
    clearResult();
}

function clearResult() {
    document.getElementById('resultSection').style.display = 'none';
}

function clearBatchInput() {
    document.getElementById('batchInput').value = '';
    document.getElementById('batchCharCount').textContent = '0';
    clearBatchResult();
}

function clearBatchResult() {
    document.getElementById('batchResultSection').style.display = 'none';
}
