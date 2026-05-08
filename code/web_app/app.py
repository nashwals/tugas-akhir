"""
Stress Prediction Web Application
===================================
A research-oriented web application that:
1. Collects respondent data through a comprehensive form
2. Makes stress score estimations using trained statistical models
3. Allows anonymous data contribution for model improvement

Note: Predictions are statistical estimations, not clinical diagnoses.
Models can be updated through controlled retraining processes.
"""

from flask import Flask, request, jsonify, render_template
import joblib
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

# Global variables to store loaded model and metadata
model = None
metadata = None
categorical_options = None
feature_labels = None
data_stats = None

def load_data_statistics():
    """Load and calculate statistics from training data"""
    try:
        # Load training data
        data_path = '../data/burnout_submissions.csv'
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            
            if 'skor_total' in df.columns:
                scores = df['skor_total'].dropna()
                
                stats = {
                    'mean': float(scores.mean()),
                    'std': float(scores.std()),
                    'min': float(scores.min()),
                    'max': float(scores.max()),
                    'q1': float(scores.quantile(0.25)),
                    'q2': float(scores.quantile(0.50)),  # median
                    'q3': float(scores.quantile(0.75)),
                    'n_samples': len(scores)
                }
                
                print(f"✓ Data statistics loaded:")
                print(f"  Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}")
                print(f"  Range: {stats['min']:.0f}-{stats['max']:.0f}")
                print(f"  Q1={stats['q1']:.2f}, Median={stats['q2']:.2f}, Q3={stats['q3']:.2f}")
                
                return stats
        
        # Fallback if data not available
        print("⚠ Data file not found, using default statistics")
        return {
            'mean': 25.0,
            'std': 10.0,
            'min': 0,
            'max': 50,
            'q1': 18.0,
            'q2': 25.0,
            'q3': 32.0,
            'n_samples': 0
        }
    except Exception as e:
        print(f"⚠ Error loading data statistics: {e}")
        return {
            'mean': 25.0,
            'std': 10.0,
            'min': 0,
            'max': 50,
            'q1': 18.0,
            'q2': 25.0,
            'q3': 32.0,
            'n_samples': 0
        }


def load_model_and_metadata():
    """Load the best model and its metadata with error handling"""
    global model, metadata, categorical_options, feature_labels, data_stats
    
    try:
        # Load the trained model
        model = joblib.load('best_model.joblib')
        print("✓ Model loaded successfully")
        
        # Load metadata
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        print("✓ Metadata loaded successfully")
        
        # Load categorical options
        with open('categorical_options.json', 'r') as f:
            categorical_options = json.load(f)
        print("✓ Categorical options loaded successfully")
        
        # Create human-readable labels for features
        feature_labels = create_feature_labels()
        
        # Load data statistics
        data_stats = load_data_statistics()
        
        print(f"✓ Model: {metadata['model_name']}")
        print(f"✓ Trained: {metadata['training_date']}")
        print(f"✓ Training samples: {metadata['n_samples']}")
        print(f"✓ Cross-Validated R²: {metadata['performance'][metadata['model_name']]['r2']:.4f}")
        
    except FileNotFoundError as e:
        print("ERROR: Required files not found!")
        print("Please ensure best_model.joblib, model_metadata.json, and categorical_options.json exist.")
        print("Run 'python train_model.py' to generate these files.")
        raise e
    except Exception as e:
        print(f"ERROR: Failed to load model or metadata: {e}")
        raise e


def validate_numerical_input(data):
    """
    Validate numerical inputs with realistic bounds to prevent garbage input.
    Returns (is_valid, error_message)
    """
    validations = {
        'usia': (20, 70, 'Usia harus antara 20-70 tahun'),
        'jumlah_anak': (0, 15, 'Jumlah anak harus antara 0-15'),
        'usia_anak': (0, 50, 'Rata-rata usia anak harus antara 0-50 tahun'),
        'lama_bekerja': (0, 50, 'Lama bekerja harus antara 0-50 tahun'),
        'waktu_bekerja_seminggu': (0, 168, 'Jam kerja per minggu harus antara 0-168'),
        'beban_sks': (0, 100, 'Beban SKS harus antara 0-100'),
        'mhs_bimbingan': (0, 200, 'Jumlah mahasiswa bimbingan harus antara 0-200'),
        'work_life_balance': (1, 5, 'Work-life balance harus antara 1-5'),
        'gaji_sesuai': (1, 5, 'Kesesuaian gaji harus antara 1-5')
    }
    
    for field, (min_val, max_val, error_msg) in validations.items():
        if field in data:
            try:
                value = float(data[field])
                if not (min_val <= value <= max_val):
                    return False, f"{error_msg} (nilai: {value})"
            except (ValueError, TypeError):
                return False, f"{field} harus berupa angka"
    
    return True, None


def handle_missing_values(df, metadata):
    """
    Handle missing values explicitly before prediction.
    Fills with 0 for numerical and 'Unknown' for categorical.
    """
    for feature in metadata['numerical_features']:
        if feature in df.columns:
            df[feature] = df[feature].fillna(0)
    
    for feature in metadata['categorical_features']:
        if feature in df.columns:
            df[feature] = df[feature].fillna('Unknown')
    
    return df


def create_feature_labels():
    """Create human-readable labels for all features"""
    labels = {
        # Demographics
        'usia': 'Usia (Age)',
        'jenis_kelamin': 'Jenis Kelamin (Gender)',
        'kota_asal': 'Kota Asal (City of Origin)',
        'status_pernikahan': 'Status Pernikahan (Marital Status)',
        'jumlah_anak': 'Jumlah Anak (Number of Children)',
        'usia_anak': 'Rata-rata Usia Anak (Average Children\'s Age)',
        
        # Living situation
        'tinggal_sendiri': 'Tinggal Sendiri (Living Alone)',
        'tinggal_pasangan': 'Tinggal dengan Pasangan (Living with Spouse)',
        'tinggal_anak': 'Tinggal dengan Anak (Living with Children)',
        'tinggal_ortu': 'Tinggal dengan Orang Tua (Living with Parents)',
        'tinggal_mertua': 'Tinggal dengan Mertua (Living with In-laws)',
        'tinggal_saudara': 'Tinggal dengan Saudara/Kerabat (Living with Siblings/Relatives)',
        'tinggal_teman': 'Tinggal dengan Teman/Kolega (Living with Friends/Colleagues)',
        
        # Work & Career
        'bidang': 'Bidang/Program Studi (Field of Study)',
        'lama_bekerja': 'Lama Bekerja (Years of Work)',
        'mode_bekerja': 'Mode Bekerja (Work Mode)',
        'jarak': 'Jarak ke Kampus (Distance to Campus)',
        'waktu_bekerja_seminggu': 'Jam Kerja per Minggu (Work Hours per Week)',
        'beban_sks': 'Beban SKS (Credit Load)',
        'mhs_bimbingan': 'Jumlah Mahasiswa Bimbingan (Number of Students)',
        'jabatan_struktural': 'Jabatan Struktural (Structural Position)',
        'jabatan_fungsional': 'Jabatan Fungsional (Functional Position)',
        'sertifikasi': 'Status Sertifikasi (Certification Status)',
        'status_keaktifan': 'Status Keaktifan (Activity Status)',
        
        # Physical Health
        'fisik_mata': 'Gangguan Mata (Eye Problems)',
        'fisik_punggung': 'Gangguan Punggung (Back Problems)',
        'fisik_tensi': 'Hipertensi (Hypertension)',
        'fisik_lemah': 'Kelelahan Fisik (Physical Fatigue)',
        'fisik_kepala': 'Sakit Kepala (Headache)',
        'fisik_obesitas': 'Obesitas (Obesity)',
        'fisik_imun': 'Penurunan Imunitas (Low Immunity)',
        'fisik_carpal': 'Carpal Tunnel',
        
        # Mental Health
        'mental_anxiety': 'Anxiety (Kecemasan)',
        'mental_burnout': 'Burnout (Kelelahan Emosional)',
        'mental_depresi': 'Depresi (Depression)',
        'mental_distress': 'Distress Psikologis',
        'mental_konsentrasi': 'Gangguan Konsentrasi',
        'mental_insomnia': 'Insomnia',
        'mental_iritate': 'Iritabilitas (Irritability)',
        'mental_lelah': 'Kelelahan Mental',
        'mental_stres': 'Stres Kerja (Work Stress)',
        
        # Work-Life Balance
        'work_life_balance': 'Work-Life Balance (1-5 scale)',
        'gaji_sesuai': 'Gaji Sesuai? (Salary Satisfaction, 1-5)'
    }
    
    return labels


@app.route('/')
def home():
    """Main page with the data collection form"""
    return render_template('index.html',
                          categorical_options=categorical_options,
                          feature_labels=feature_labels,
                          numerical_features=metadata['numerical_features'],
                          categorical_features=metadata['categorical_features'],
                          model_name=metadata['model_name'],
                          n_samples=metadata['n_samples'],
                          model_performance=metadata['performance'][metadata['model_name']])


@app.route('/predict', methods=['POST'])
def predict():
    """
    Make a prediction WITHOUT saving any data (privacy-preserving mode).
    Predictions are statistical estimations, not clinical diagnoses.
    """
    try:
        data = request.json
        
        # Validate numerical inputs
        is_valid, error_msg = validate_numerical_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'Input tidak valid: {error_msg}'
            }), 400
        
        # Create DataFrame with the same structure as training data
        df = pd.DataFrame([data])
        
        # Convert numeric features to appropriate types
        for feature in metadata['numerical_features']:
            if feature in df.columns:
                df[feature] = pd.to_numeric(df[feature], errors='coerce')
        
        # Handle missing values explicitly
        df = handle_missing_values(df, metadata)
        
        # Ensure the order matches training
        features = metadata['categorical_features'] + metadata['numerical_features']
        df = df[features]
        
        # Make prediction
        prediction = model.predict(df)
        predicted_score = float(prediction[0])
        
        # Clip prediction to valid SOS-S range (10-50)
        predicted_score = float(np.clip(predicted_score, 10, 50))
        
        # Determine stress level
        stress_level = get_stress_level(predicted_score)
        
        # NO DATA SAVING in prediction mode - privacy preserved
        
        return jsonify({
            'success': True,
            'predicted_score': round(predicted_score, 2),
            'stress_level': stress_level,
            'model_info': {
                'model_name': metadata['model_name'],
                'model_version': metadata['training_date'],
                'training_samples': metadata['n_samples'],
                'r2_score': round(metadata['performance'][metadata['model_name']]['r2'], 4)
            },
            'message': 'Estimasi selesai. Data tidak disimpan (privacy mode).',
            'disclaimer': 'Hasil ini adalah estimasi statistik berbasis model machine learning, bukan diagnosis klinis. Konsultasikan dengan profesional kesehatan mental untuk penilaian lebih lanjut.'
        })
        
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Data tidak lengkap: {str(e)}'
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Format data tidak valid: {str(e)}'
        }), 400
    except Exception as e:
        # Don't expose stack trace to user
        print(f"Prediction error: {e}")
        return jsonify({
            'success': False,
            'error': 'Terjadi kesalahan saat memproses prediksi. Mohon periksa input Anda.'
        }), 500


@app.route('/contribute', methods=['POST'])
def contribute():
    """
    Make a prediction AND save anonymous contribution with actual stress score.
    Data is saved without personal identifiers for research purposes.
    """
    try:
        data = request.json
        
        # Validate numerical inputs
        is_valid, error_msg = validate_numerical_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'Input tidak valid: {error_msg}'
            }), 400
        
        # Extract SOS-S questions and calculate skor_total
        sos_questions = [
            '1_tidak_mampu', '2_kewalahan_tanggung_jawab', '3_keadaan_tidak_berpihak',
            '4_waktu_tidak_cukup', '5_tidak_berjalan_baik', '6_terburu_buru',
            '7_tidak_ada_jalan_keluar', '8_masalah_menumpuk', '9_ingin_menyerah',
            '10_memikul_beban_berat'
        ]
        
        # Calculate actual stress score from SOS-S questions
        skor_total = sum(int(data.get(q, 0)) for q in sos_questions)
        
        # Validate SOS-S score is in valid range
        if not (10 <= skor_total <= 50):
            return jsonify({
                'success': False,
                'error': f'Skor SOS-S tidak valid: {skor_total}. Harus antara 10-50.'
            }), 400
        
        data['skor_total'] = skor_total
        
        # Create DataFrame for prediction (without SOS-S questions and skor_total)
        prediction_data = data.copy()
        for q in sos_questions + ['skor_total']:
            prediction_data.pop(q, None)
        
        df = pd.DataFrame([prediction_data])
        
        # Convert numeric features to appropriate types
        for feature in metadata['numerical_features']:
            if feature in df.columns:
                df[feature] = pd.to_numeric(df[feature], errors='coerce')
        
        # Handle missing values explicitly
        df = handle_missing_values(df, metadata)
        
        # Ensure the order matches training
        features = metadata['categorical_features'] + metadata['numerical_features']
        df = df[features]
        
        # Make prediction
        prediction = model.predict(df)
        predicted_score = float(prediction[0])
        
        # Clip prediction to valid SOS-S range (10-50)
        predicted_score = float(np.clip(predicted_score, 10, 50))
        
        # Save the full anonymous contribution (no personal identifiers)
        save_contribution(data, predicted_score, skor_total)
        
        # Determine stress level based on PREDICTED score
        predicted_stress_level = get_stress_level(predicted_score)
        
        # Determine stress level based on ACTUAL score
        actual_stress_level = get_stress_level(skor_total)
        
        return jsonify({
            'success': True,
            'predicted_score': round(predicted_score, 2),
            'actual_score': skor_total,
            'predicted_stress_level': predicted_stress_level,
            'actual_stress_level': actual_stress_level,
            'model_info': {
                'model_name': metadata['model_name'],
                'model_version': metadata['training_date'],
                'training_samples': metadata['n_samples'],
                'r2_score': round(metadata['performance'][metadata['model_name']]['r2'], 4)
            },
            'message': 'Terima kasih atas kontribusi anonim Anda! Data telah tersimpan dan dapat digunakan untuk pembaruan model melalui proses retraining terkontrol.',
            'disclaimer': 'Hasil ini adalah estimasi statistik berbasis model machine learning, bukan diagnosis klinis. Konsultasikan dengan profesional kesehatan mental untuk penilaian lebih lanjut.'
        })
        
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Data tidak lengkap: {str(e)}'
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Format data tidak valid: {str(e)}'
        }), 400
    except Exception as e:
        # Don't expose stack trace to user
        print(f"Contribution error: {e}")
        return jsonify({
            'success': False,
            'error': 'Terjadi kesalahan saat memproses kontribusi. Mohon periksa input Anda.'
        }), 500


def save_contribution(data, predicted_score, actual_score):
    """
    Save anonymous contribution data with timestamp and model version.
    Data is stored without personal identifiers for research purposes.
    Auto-creates CSV files if they don't exist for robustness.
    """
    main_dataset_file = '../data/burnout_submissions.csv'
    contributions_file = '../data/new_contributions.csv'
    
    # Ensure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    # Remove any potential personal identifiers
    # (nama, institusi, id should not be in data from web form, but ensure they're not saved)
    safe_data = data.copy()
    personal_fields = ['nama', 'institusi', 'id', 'email', 'phone', 'nama_lengkap']
    for field in personal_fields:
        safe_data.pop(field, None)
    
    # Add metadata for controlled retraining
    safe_data['predicted_score'] = predicted_score
    safe_data['submission_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    safe_data['model_used'] = metadata['model_name']
    safe_data['model_version'] = metadata['training_date']
    safe_data['model_r2'] = metadata['performance'][metadata['model_name']]['r2']
    
    # Create DataFrame
    df = pd.DataFrame([safe_data])
    
    # Append to main dataset (for future retraining)
    try:
        if os.path.exists(main_dataset_file):
            # Read existing data to maintain column order
            existing_df = pd.read_csv(main_dataset_file, nrows=0)
            # Add any new columns from contribution
            for col in df.columns:
                if col not in existing_df.columns:
                    existing_df[col] = None
            # Append
            df.to_csv(main_dataset_file, mode='a', header=False, index=False)
        else:
            # Create new file with headers
            df.to_csv(main_dataset_file, mode='w', header=True, index=False)
        print(f"✓ Contribution saved to main dataset")
    except Exception as e:
        print(f"⚠ Warning: Could not save to main dataset: {e}")
    
    # Also keep a backup in separate contributions file
    try:
        if os.path.exists(contributions_file):
            df.to_csv(contributions_file, mode='a', header=False, index=False)
        else:
            df.to_csv(contributions_file, mode='w', header=True, index=False)
        print(f"✓ Contribution backed up")
    except Exception as e:
        print(f"⚠ Warning: Could not save backup: {e}")


def get_stress_level(score):
    """Categorize stress level based on score compared to dataset statistics"""
    mean = data_stats['mean']
    q1 = data_stats['q1']
    q3 = data_stats['q3']
    
    # Calculate how far from mean
    diff_from_mean = score - mean
    percent_diff = (diff_from_mean / mean) * 100 if mean > 0 else 0
    
    # Classify based on quartiles
    if score < q1:
        # Below 25th percentile - Very Low
        return {
            'level': 'Sangat Rendah (Very Low)',
            'color': 'green',
            'description': f'Skor stres Anda ({score:.1f}) jauh di bawah rata-rata ({mean:.1f}). '
                          f'Tingkat stres Anda sangat rendah dibanding responden lain.'
        }
    elif score < mean:
        # Between Q1 and mean - Below Average
        return {
            'level': 'Rendah (Below Average)',
            'color': 'lightgreen',
            'description': f'Skor stres Anda ({score:.1f}) lebih rendah {abs(percent_diff):.1f}% dari rata-rata ({mean:.1f}). '
                          f'Tingkat stres Anda di bawah rata-rata populasi.'
        }
    elif score < q3:
        # Between mean and Q3 - Above Average
        return {
            'level': 'Sedang (Above Average)',
            'color': 'yellow',
            'description': f'Skor stres Anda ({score:.1f}) lebih tinggi {abs(percent_diff):.1f}% dari rata-rata ({mean:.1f}). '
                          f'Tingkat stres Anda di atas rata-rata. Pertimbangkan untuk istirahat lebih banyak.'
        }
    else:
        # Above 75th percentile - High
        return {
            'level': 'Tinggi (High)',
            'color': 'red',
            'description': f'Skor stres Anda ({score:.1f}) jauh di atas rata-rata ({mean:.1f}). '
                          f'Tingkat stres Anda sangat tinggi dibanding responden lain. '
                          f'Sangat disarankan untuk konsultasi dengan profesional kesehatan mental.'
        }



@app.route('/stats')
def stats():
    """Display current model statistics"""
    return jsonify({
        'model_name': metadata['model_name'],
        'training_date': metadata['training_date'],
        'n_samples': metadata['n_samples'],
        'performance': metadata['performance'],
        'all_models': list(metadata['performance'].keys()),
        'data_statistics': data_stats
    })


if __name__ == '__main__':
    # Load model at startup
    load_model_and_metadata()
    
    # Run the app
    print("\n" + "="*80)
    print("Starting Stress Prediction Web Application")
    print("="*80)
    print(f"Open your browser and go to: http://127.0.0.1:5000")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
