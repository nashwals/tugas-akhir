# 🧠 Stress Prediction System for Lecturers

A flexible machine learning system that predicts lecturer stress levels and continuously improves through data collection.

## 📋 Features

- ✅ **Flexible Model Selection**: Automatically uses the best performing model (SVR, XGBoost, Random Forest, etc.)
- 📊 **Multiple Model Training**: Trains 6 different models and selects the best one
- 🌐 **Web Interface**: User-friendly form for data collection and prediction
- 💾 **Continuous Learning**: Collects new data for model improvement
- 🔄 **Easy Retraining**: Simple workflow to retrain with updated data
- 📈 **Performance Tracking**: Monitors which model performs best over time

## 🏗️ System Architecture

```
code/
├── train_model.py              # Train all models, select the best
├── data/
│   ├── burnout_submissions.csv # Original training data (49 samples)
│   └── new_contributions.csv   # Collected data from web app
└── web_app/
    ├── app.py                  # Flask web application
    ├── best_model.joblib       # Currently best model
    ├── all_models.joblib       # All trained models
    ├── model_metadata.json     # Model info & performance
    ├── categorical_options.json # Form options
    ├── feature_importance_comparison.csv # Model interpretability summary
    ├── requirements.txt        # Python dependencies
    ├── templates/
    │   └── index.html         # Web form
    └── static/
        ├── style.css          # Styling
        └── script.js          # Form logic
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd code/web_app
pip3 install -r requirements.txt
```

### 2. Train Initial Models

First time setup - train all models with existing data:

```bash
cd code
python3 train_model.py
```

This will:
- Train 6 models: Mean, LR, XGBoost, Random Forest, Gradient Boosting, SVR
- Use the notebook-aligned preprocessing pipeline (RobustScaler, infrequent-category handling, VarianceThreshold)
- Perform repeated 5-fold cross-validation during tuning and evaluation
- Select the best model based on R² score
- Save deployment artifacts to `web_app/` and feature importance output to `code/`

**Expected Output:**
```
🏆 Best Model: SVR (or whichever performs best)
   R² Score: 0.XXXX
   RMSE:     X.XXXX
   MAE:      X.XXXX
```

### 3. Run the Web Application

```bash
cd web_app
python3 app.py
```

Open your browser: `http://127.0.0.1:5000`

## 📊 How It Works

### Initial Training
1. **Data Loading**: Loads `burnout_submissions.csv` (49 samples)
2. **Feature Engineering**: Processes 40+ features (demographics, work, health)
3. **Model Training**: Trains multiple models with hyperparameter tuning
4. **Model Selection**: Automatically selects best model based on R² score
5. **Deployment**: Saves best model for web app to use

### Data Collection
1. User fills out the comprehensive form on the web interface
2. System makes a prediction using the current best model
3. Submission is saved to `new_contributions.csv`
4. Data accumulates for future model improvement

### Model Improvement
When you have collected more data:

```bash
# Option 1: Combine new data with original data
python3 merge_data.py

# Option 2: Or manually merge CSV files
cat data/burnout_submissions.csv data/new_contributions.csv > data/combined_data.csv

# Retrain with updated data
python3 train_model.py
```

The system will:
- Train all models again with the larger dataset
- Compare their performance
- **Automatically select the new best model** (might be different!)
- Update the web app to use the new best model **without any code changes**

## 🎯 Model Flexibility

The beauty of this system is its flexibility:

| Scenario | What Happens |
|----------|--------------|
| **Initial training** | The best model is selected from the latest run |
| **More samples** | The model choice can shift automatically after retraining |
| **Different data mix** | XGBoost, Random Forest, SVR, or another model may win |

**No code changes needed!** Just retrain and the system adapts.

## 📈 Monitoring Model Performance

### Check Current Model Status

Visit: `http://127.0.0.1:5000/stats`

Returns:
```json
{
    "model_name": "RFR",
  "training_date": "2026-03-02 10:30:00",
  "n_samples": 49,
  "performance": {
    "Mean": {"r2": 0.0000, "rmse": 8.5000, "mae": 6.8000},
    "LR": {"r2": 0.4500, "rmse": 6.2000, "mae": 4.5000},
    "XGB": {"r2": 0.7800, "rmse": 3.9000, "mae": 2.8000},
    "RFR": {"r2": 0.7500, "rmse": 4.2000, "mae": 3.1000},
    "GBR": {"r2": 0.7600, "rmse": 4.1000, "mae": 3.0000},
    "SVR": {"r2": 0.8200, "rmse": 3.5000, "mae": 2.5000}
  }
}
```

### View Model Metadata

Check `web_app/model_metadata.json` to see:
- Which model is currently active
- All model performances
- Best hyperparameters
- Training date and sample size

## 🔄 Retraining Workflow

```bash
# 1. Check how much new data you have
wc -l data/new_contributions.csv

# 2. Combine with original data (create your own merge script or do manually)

# 3. Retrain
python3 train_model.py

# 4. Compare results in the output
# If a different model is now best, the web app automatically uses it!

# 5. Restart web app to load new model
cd web_app
python3 app.py
```

## 🎨 Features by Section

### Demographics (6 features)
- Age, gender, city, marital status, children info

### Living Situation (7 features)
- Living alone, with spouse, children, parents, etc.

### Work & Career (14 features)
- Field of study, years of work, work mode, distance, hours/week
- Teaching load, students supervised, positions, certification

### Work-Life Balance (2 features)
- Work-life balance score, salary satisfaction

### Physical Health (8 features)
- Eye problems, back pain, hypertension, fatigue, obesity, etc.

### Mental Health (9 features)
- Anxiety, burnout (emotional exhaustion), depression, insomnia, work stress, etc.

**Total: 46 input features → 1 predicted score (0-50 scale)**

## 🛠️ Customization

### Change Hyperparameter Search Space

Edit `train_model.py`:
```python
param_grids = {
    'XGB': {
        'regressor__n_estimators': [100, 200, 300, 400],  # Add more
        'regressor__learning_rate': [0.01, 0.05, 0.1, 0.2],
        # Add other parameters
    }
}
```

### Add New Models

```python
# In train_model.py, add to define_models():
'NewModel': Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', YourNewRegressor())
])

# Don't forget to add param_grid
```

### Modify Stress Level Categories

Edit `app.py` → `get_stress_level()` function:
```python
if score < 15:
    return {'level': 'Low', 'color': 'green', ...}
# Adjust thresholds as needed
```

## 📊 Data Privacy

- Submissions are saved **anonymously**
- No personal identifiers (nama, id) are stored from form
- Data used only for model improvement
- Complies with research ethics

## 🐛 Troubleshooting

### Model files not found
```bash
# Make sure you trained first
cd code
python3 train_model.py
```

### Import errors
```bash
pip install -r web_app/requirements.txt
```

### Web app won't start
```bash
# Check if port 5000 is free
lsof -i :5000

# Or use different port in app.py
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 📚 Technologies Used

- **Python 3.8+**
- **Flask** - Web framework
- **scikit-learn** - ML models (LR, RF, GBR, SVR)
- **XGBoost** - Gradient boosting
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **joblib** - Model serialization

## 🎓 Academic Use

This system is designed for research purposes. When publishing results:

1. Report which model performed best on which dataset sizes
2. Track how model performance improves with more data
3. Analyze feature importance as data grows
4. Compare model stability across different sample sizes

## 📧 Support

For questions or issues, please refer to:
- `LOGBOOK.md` - Project development log
- `regression.ipynb` - Detailed analysis notebook

## 🎉 Success Metrics

Track these as your system grows:

| Metric | Initial (49 samples) | Goal (100+ samples) | Goal (500+ samples) |
|--------|---------------------|---------------------|---------------------|
| **R² Score** | ~0.82 (SVR) | > 0.85 | > 0.90 |
| **MAE** | ~2.5 | < 2.0 | < 1.5 |
| **Best Model** | SVR | TBD | TBD |

## 🚀 Future Enhancements

- [ ] Add data visualization dashboard
- [ ] Implement model versioning
- [ ] Add A/B testing for multiple models
- [ ] Export predictions to PDF
- [ ] Add email notifications for high stress cases
- [ ] Multi-language support (EN/ID)
- [ ] Mobile-responsive improvements
- [ ] Add authentication for admin panel

---

**Made with ❤️ for improving lecturer well-being through data science**
