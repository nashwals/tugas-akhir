"""
Stress Prediction Model Training Script
=========================================
This script trains multiple regression models and automatically selects the best one
based on cross-validation performance. Designed for controlled retraining with updated data.

RETRAINING PROCESS (For Reproducibility):
------------------------------------------
1. Ensure burnout_submissions.csv has sufficient data (recommended: 50+ samples)
2. Run: python train_model.py
3. Script will:
   - Train 6 different models with cross-validation
   - Select best model based on R² score
   - Save best_model.joblib (model file)
   - Save model_metadata.json (version, performance metrics, feature lists)
   - Save categorical_options.json (for web form dropdowns)
4. Web application will automatically use the updated model on next restart

Models trained:
- Mean Regressor (baseline)
- Linear Regression (LR)
- XGBoost (XGB)
- Random Forest (RFR)
- Gradient Boosting (GBR)
- Support Vector Regression (SVR)

IMPORTANT NOTES:
- All preprocessing steps must be included in the pipeline for consistency
- Feature order and encoding must match between training and prediction
- Model version is tracked by timestamp for reproducibility
- Anonymous data only - no personal identifiers should be in training data
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RepeatedKFold, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor


def load_and_prepare_data(csv_path):
    """Load data and prepare features and target"""
    print(f"\n{'='*80}")
    print("LOADING DATA")
    print(f"{'='*80}")
    
    data = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(data)} samples from {csv_path}")
    
    # Define features to drop (not used for prediction)
    features_to_drop = [
        'id', 'nama', 'institusi', 'tinggal_dengan_siapa', 'profesi', 
        'kesehatan_fisik', 'kondisi_mental',
        '1_tidak_mampu', '2_kewalahan_tanggung_jawab', '3_keadaan_tidak_berpihak',
        '4_waktu_tidak_cukup', '5_tidak_berjalan_baik', '6_terburu_buru',
        '7_tidak_ada_jalan_keluar', '8_masalah_menumpuk', '9_ingin_menyerah',
        '10_memikul_beban_berat', 'skor_total'
    ]
    
    X = data.drop(columns=features_to_drop)
    y = data['skor_total']
    
    print(f"✓ Features: {len(X.columns)} columns")
    print(f"✓ Target: skor_total (stress score)")
    
    return X, y, data


def create_preprocessor(X):
    """Create preprocessing pipeline for numerical and categorical features"""
    numerical_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'str', 'bool']).columns.tolist()
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(
            handle_unknown='infrequent_if_exist',
            min_frequency=0.05,
            sparse_output=False
        ))
    ])
    
    preprocessor_base = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )

    preprocessor = Pipeline(steps=[
        ('prep_base', preprocessor_base),
        ('variance_filter', VarianceThreshold(threshold=0.01))
    ])
    
    print(f"✓ Numerical features: {len(numerical_features)}")
    print(f"✓ Categorical features: {len(categorical_features)}")
    
    return preprocessor, numerical_features, categorical_features


def define_models(preprocessor):
    """Define all models to be trained"""
    models = {
        'Mean': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', DummyRegressor(strategy='mean'))
        ]),
        'LR': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', LinearRegression())
        ]),
        'XGB': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=2024))
        ]),
        'RFR': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=2024))
        ]),
        'GBR': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', GradientBoostingRegressor(n_estimators=100, random_state=2024))
        ]),
        'SVR': Pipeline(steps=[
            ('preprocessor', preprocessor), 
            ('regressor', SVR(kernel='rbf', C=1.0, epsilon=0.1))
        ])
    }
    
    return models


def define_param_grids():
    """Define hyperparameter grids for tuning"""
    param_grids = {
        'Mean': {
            'regressor__strategy': ['mean']
        },
        'LR': {
            'regressor__fit_intercept': [True, False],
            'regressor__positive': [False, True]
        },
        'XGB': {
            'regressor__n_estimators': [50, 100, 150],
            'regressor__learning_rate': [0.01, 0.05, 0.1],
            'regressor__max_depth': [2, 3, 4],
            'regressor__min_child_weight': [2, 4, 6],
            'regressor__subsample': [0.8, 1.0],
            'regressor__colsample_bytree': [0.8, 1.0]
        },
        'RFR': {
            'regressor__n_estimators': [50, 100, 150],
            'regressor__max_depth': [3, 5, 7],
            'regressor__min_samples_split': [4, 6, 8],
            'regressor__min_samples_leaf': [2, 4, 6],
            'regressor__max_features': ['sqrt', 'log2']
        },
        'GBR': {
            'regressor__n_estimators': [50, 100, 150],
            'regressor__learning_rate': [0.01, 0.05, 0.1],
            'regressor__max_depth': [2, 3, 4],
            'regressor__min_samples_split': [4, 6, 8],
            'regressor__min_samples_leaf': [2, 4, 6],
            'regressor__subsample': [0.8, 1.0]
        },
        'SVR': {
            'regressor__kernel': ['rbf', 'linear'],
            'regressor__C': [0.1, 1.0, 5.0, 10.0],
            'regressor__epsilon': [0.05, 0.1, 0.2],
            'regressor__gamma': ['scale', 'auto']
        }
    }
    
    return param_grids


def tune_and_train_models(models, param_grids, X, y, n_splits=5):
    """Perform hyperparameter tuning and train all models"""
    print(f"\n{'='*80}")
    print("HYPERPARAMETER TUNING & TRAINING")
    print(f"{'='*80}")
    
    kf = RepeatedKFold(n_splits=n_splits, n_repeats=3, random_state=2024)
    
    best_models = {}
    best_params = {}
    cv_scores = {}
    
    for name, model in models.items():
        print(f"\n[{name}] Starting hyperparameter tuning...")
        n_combinations = np.prod([len(v) for v in param_grids[name].values()])
        print(f"  Testing {n_combinations} parameter combinations...")
        
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grids[name],
            cv=kf,
            scoring='r2',
            n_jobs=-1,
            verbose=0,
            return_train_score=True
        )
        
        grid_search.fit(X, y)
        
        best_models[name] = grid_search.best_estimator_
        best_params[name] = grid_search.best_params_
        cv_scores[name] = grid_search.best_score_
        
        print(f"  ✓ Best CV R² Score: {grid_search.best_score_:.4f}")
    
    return best_models, best_params, cv_scores


def evaluate_models(best_models, X, y, n_splits=5):
    """Evaluate all models using cross-validation"""
    print(f"\n{'='*80}")
    print("MODEL EVALUATION")
    print(f"{'='*80}")
    
    kf = RepeatedKFold(n_splits=n_splits, n_repeats=3, random_state=2024)
    results = {model: {'r2': [], 'rmse': [], 'mae': []} for model in best_models}
    
    for train_index, test_index in kf.split(X, y):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        for name, model in best_models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            results[name]['r2'].append(r2_score(y_test, y_pred))
            results[name]['rmse'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
            results[name]['mae'].append(np.mean(np.abs(y_test - y_pred)))
    
    # Print results
    model_performance = []
    for name, metrics in results.items():
        avg_r2 = np.mean(metrics['r2'])
        avg_rmse = np.mean(metrics['rmse'])
        avg_mae = np.mean(metrics['mae'])
        
        print(f"\n{name} Results:")
        print(f"  R² Score: {avg_r2:.4f} (+/- {np.std(metrics['r2']):.4f})")
        print(f"  RMSE:     {avg_rmse:.4f} (+/- {np.std(metrics['rmse']):.4f})")
        print(f"  MAE:      {avg_mae:.4f} (+/- {np.std(metrics['mae']):.4f})")
        
        model_performance.append({
            'model': name,
            'r2': avg_r2,
            'rmse': avg_rmse,
            'mae': avg_mae,
            'r2_std': np.std(metrics['r2']),
            'rmse_std': np.std(metrics['rmse']),
            'mae_std': np.std(metrics['mae'])
        })
    
    return model_performance, results


def get_feature_importance(model, model_name, X, y):
    """Extract signed feature importance from a fitted model."""
    feature_names = model.named_steps['preprocessor'].named_steps['prep_base'].get_feature_names_out()
    mask = model.named_steps['preprocessor'].named_steps['variance_filter'].get_support()
    feature_names = feature_names[mask]

    if model_name == 'Mean':
        return None
    if model_name == 'LR':
        importances = model.named_steps['regressor'].coef_
    elif model_name in ['XGB', 'RFR', 'GBR']:
        importances = model.named_steps['regressor'].feature_importances_
    elif model_name == 'SVR':
        perm_importance = permutation_importance(model, X, y, n_repeats=10, random_state=2024)
        importances = perm_importance.importances_mean
    else:
        return None

    feature_importance = dict(zip(feature_names, importances))
    return dict(sorted(feature_importance.items(), key=lambda item: abs(item[1]), reverse=True))


def retrain_models_on_full_data(models, X, y):
    """Retrain the tuned models on the full dataset before deployment."""
    print(f"\n{'='*80}")
    print("RETRAINING ON FULL DATA")
    print(f"{'='*80}")
    for name, model in models.items():
        model.fit(X, y)
        print(f"✓ {name} retrained on full dataset")


def save_feature_importance_comparison(models, X, y, output_path):
    """Save a comparison table of feature importances for all fitted models."""
    feature_importances = {}

    for name, model in models.items():
        importance = get_feature_importance(model, name, X, y)
        if importance:
            feature_importances[name] = importance

    if not feature_importances:
        print("⚠ No feature importances available to save")
        return

    df_importance = pd.DataFrame(feature_importances)
    df_importance['avg_importance'] = df_importance.abs().mean(axis=1)
    df_importance = df_importance.sort_values('avg_importance', ascending=False)
    df_importance = df_importance.drop('avg_importance', axis=1)

    new_index = []
    for feature in df_importance.index:
        if feature.startswith('cat__'):
            parts = feature.split('__')
            if len(parts) == 3:
                new_index.append(f"{parts[1]}_{parts[2]}")
            else:
                new_index.append(feature)
        elif feature.startswith('num__'):
            new_index.append(feature.replace('num__', ''))
        else:
            new_index.append(feature)
    df_importance.index = new_index

    df_importance.to_csv(output_path)
    print(f"✓ Feature importance saved: {output_path}")


def select_best_model(model_performance):
    """Select the best model based on R² score"""
    best = max(model_performance, key=lambda x: x['r2'])
    
    print(f"\n{'='*80}")
    print("BEST MODEL SELECTION")
    print(f"{'='*80}")
    print(f"\n🏆 Best Model: {best['model']}")
    print(f"   R² Score: {best['r2']:.4f}")
    print(f"   RMSE:     {best['rmse']:.4f}")
    print(f"   MAE:      {best['mae']:.4f}")
    
    return best['model']


def save_model_and_metadata(best_model_name, best_models, model_performance, 
                            best_params, numerical_features, categorical_features,
                            data, output_dir):
    """Save the best model and metadata"""
    print(f"\n{'='*80}")
    print("SAVING MODEL AND METADATA")
    print(f"{'='*80}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the best model
    model_path = os.path.join(output_dir, 'best_model.joblib')
    joblib.dump(best_models[best_model_name], model_path)
    print(f"✓ Model saved: {model_path}")
    
    # Save metadata
    metadata = {
        'model_name': best_model_name,
        'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'n_samples': len(data),
        'performance': {m['model']: {
            'r2': m['r2'],
            'rmse': m['rmse'],
            'mae': m['mae']
        } for m in model_performance},
        'best_params': best_params[best_model_name],
        'numerical_features': numerical_features,
        'categorical_features': categorical_features
    }
    
    metadata_path = os.path.join(output_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")
    
    # Save categorical options for the web form
    # Some dropdowns are intentionally static (hardcoded in the template)
    STATIC_DROPDOWNS = {
        'jenis_kelamin': ["Laki-laki", "Perempuan"],
        'status_pernikahan': ["Belum Menikah", "Sudah Menikah", "Cerai Hidup", "Cerai Mati"],
        'mode_bekerja': ["On-site", "Online", "Hybrid"],
        'jarak': ["< 1 km", "1 - 5 km", "6 - 10 km", "11 - 15 km", "> 15 km"],
        'jabatan_struktural': [
            "Rektor / Wakil Rektor",
            "Setingkat Dekan dan Kepala UPA / UPT",
            "Setingkat Kaprodi dan Ketua KK",
            "Setingkat Unit Lembaga dan Biro",
            "Jabatan Struktural Lainnya",
            "Non Jabatan Struktural"
        ],
        'jabatan_fungsional': ["Non Jabatan Fungsional", "Asisten Ahli", "Lektor", "Lektor Kepala", "Guru Besar"],
        'sertifikasi': ["Belum Tersertifikasi", "Sudah Tersertifikasi"],
        'status_keaktifan': ["Aktif", "Tugas Belajar (di PDDikti)", "Aktif (PDDikti) namun masih melakukan Tugas Belajar"]
    }

    categorical_options = {}
    for col in categorical_features:
        if col in STATIC_DROPDOWNS:
            categorical_options[col] = STATIC_DROPDOWNS[col]
        else:
            # fallback to values present in training data
            categorical_options[col] = sorted(data[col].dropna().unique().tolist())

    options_path = os.path.join(output_dir, 'categorical_options.json')
    with open(options_path, 'w') as f:
        json.dump(categorical_options, f, indent=2)
    print(f"✓ Categorical options saved: {options_path}")
    
    # Save all models for comparison
    all_models_path = os.path.join(output_dir, 'all_models.joblib')
    joblib.dump(best_models, all_models_path)
    print(f"✓ All models saved: {all_models_path}")


def main():
    """Main training pipeline"""
    print("\n" + "="*80)
    print("STRESS PREDICTION MODEL TRAINING")
    print("="*80)
    
    # Configuration
    csv_path = 'data/burnout_submissions.csv'
    output_dir = 'web_app'
    
    # Load data
    X, y, data = load_and_prepare_data(csv_path)
    
    # Create preprocessor
    preprocessor, numerical_features, categorical_features = create_preprocessor(X)
    
    # Define models
    models = define_models(preprocessor)
    print(f"\n✓ Defined {len(models)} models: {', '.join(models.keys())}")
    
    # Define parameter grids
    param_grids = define_param_grids()
    
    # Tune and train
    best_models, best_params, cv_scores = tune_and_train_models(models, param_grids, X, y)
    
    # Evaluate
    model_performance, results = evaluate_models(best_models, X, y)

    # Retrain on the full dataset before export and interpretability analysis
    retrain_models_on_full_data(best_models, X, y)

    # Save feature importances from the full-data fitted models
    feature_importance_path = os.path.join(os.path.dirname(__file__), 'feature_importance_comparison.csv')
    save_feature_importance_comparison(best_models, X, y, feature_importance_path)
    
    # Select best model
    best_model_name = select_best_model(model_performance)
    
    # Save everything
    save_model_and_metadata(
        best_model_name, 
        best_models, 
        model_performance, 
        best_params,
        numerical_features, 
        categorical_features,
        data,
        output_dir
    )
    
    print(f"\n{'='*80}")
    print("TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"\n✓ Best model ({best_model_name}) is ready to use")
    print(f"✓ All files saved to '{output_dir}/' directory")
    print(f"\nNext steps:")
    print(f"  1. Run the web app: python web_app/app.py")
    print(f"  2. Collect new data through the web interface")
    print(f"  3. When you have more data, re-run this script")
    print(f"  4. The system will automatically use the new best model!")
    print()


if __name__ == '__main__':
    main()
