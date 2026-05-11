# 🚀 Quick Start Guide
## Lecturer Stress Prediction System

## First Time Setup (5 minutes)

### Option 1: Automatic Setup (Recommended)
```bash
# from repository root
cd code

# macOS/Linux:
./setup_and_run.sh

# Windows:
setup_and_run.bat
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
cd web_app
pip3 install -r requirements.txt

# 2. Train initial model (duration depends on the grid search)
cd ..
python3 train_model.py

# 3. Start web app
cd web_app
python3 app.py
```

## Daily Usage

### Start the Web App
```bash
# from repository root
cd code/web_app
python3 app.py
```
Then open: http://127.0.0.1:5000

### Check Model Stats
Visit: http://127.0.0.1:5000/stats

## After Collecting New Data

### Retrain the Model (Every 20-50 new submissions)
```bash
# from repository root
cd code

# 1. Merge old and new data
python3 merge_data.py

# 2. Review merged file, then replace original
cp data/submissions_merged_*.csv data/submissions.csv

# 3. Retrain all models
python3 train_model.py

# 4. Restart web app
cd web_app
python3 app.py
```

## Key Files

| File | Purpose |
|------|---------|
| `train_model.py` | Train all models, select best |
| `web_app/app.py` | Web application |
| `merge_data.py` | Combine old + new data |
| `data/submissions.csv` | Training data |
| `data/new_contributions.csv` | Collected from web app |
| `web_app/best_model.joblib` | Current best model |
| `web_app/model_metadata.json` | Model info |

## Model Flexibility

✅ **Current Model**: Depends on the latest retraining result
🔄 **Automatic Switching**: System will use whatever model scores best after retraining
📊 **No Code Changes**: Just retrain and the web app adapts automatically

## Troubleshooting

### Problem: Model not found
**Solution**: Run `python3 train_model.py` first

### Problem: Port 5000 already in use
**Solution**: Edit `web_app/app.py`, change `port=5000` to `port=8080`

### Problem: Import errors
**Solution**: 
```bash
cd web_app
pip install -r requirements.txt
```

## Getting Help

- 📖 Full documentation: `README_WEB_APP.md`
- 📓 Analysis details: `regression.ipynb`
- 📝 Project log: `../LOGBOOK.md`

---

**🎯 Goal**: Grow from the current training set → 100+ → 500+ and watch the model improve!
