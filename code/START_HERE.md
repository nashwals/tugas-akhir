# 🚀 START HERE - First Time Setup
## Lecturer Stress Prediction System

## Step 1: Install Dependencies (1 minute)

```bash
# from repository root
cd code/web_app
pip3 install -r requirements.txt
```

## Step 2: Train the Models (time depends on the grid search size)

```bash
# from repository root
cd code
python3 train_model.py
```

This will:
- Train 6 models (Mean, LR, XGBoost, RF, GB, SVR)
- Use the notebook-aligned preprocessing pipeline
- Test with repeated cross-validation and hyperparameter tuning
- Select the best model from the latest run
- Save deployment files to web_app/ and feature importance output to code/

⏰ This takes 5-10 minutes. Get some coffee! ☕

## Step 3: Start the Web App

```bash
# from repository root
cd code/web_app
python3 app.py
```

Then open your browser: **http://127.0.0.1:5000**

## ✅ You're Done!

The system is now running and ready to:
- Accept stress survey submissions
- Make predictions
- Collect data for future improvements

---

## 🔧 Troubleshooting

### Error: "No module named 'flask'"
```bash
cd web_app
pip3 install -r requirements.txt
```

### Error: "Model files not found"
```bash
# from repository root
cd code
python3 train_model.py
```

### Check if training completed successfully
```bash
ls -lh web_app/*.joblib web_app/*.json
```

You should see:
- best_model.joblib
- all_models.joblib  
- model_metadata.json
- categorical_options.json
- feature_importance_comparison.csv

---

## 📝 Quick Commands Reference

**Start the web app:**
```bash
cd "/Users/nashwalaisya/Documents/Tugas Akhir/GitHub/code/web_app"
python3 app.py
```

**Stop the web app:**
`Ctrl + C`

**Check model stats:**
Visit: http://127.0.0.1:5000/stats

**Retrain with new data:**
```bash
cd "/Users/nashwalaisya/Documents/Tugas Akhir/GitHub/code"
python3 train_model.py
```
