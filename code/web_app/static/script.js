// Stress Prediction System JavaScript

// Global variable to track current mode
let currentMode = 'predict'; // 'predict' or 'contribute'

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('result-content');
    
    // Mode selector buttons
    const predictModeBtn = document.getElementById('predictModeBtn');
    const contributeModeBtn = document.getElementById('contributeModeBtn');
    const sosSection = document.getElementById('sos-section');
    const predictModeInfo = document.getElementById('predictModeInfo');
    const contributeModeInfo = document.getElementById('contributeModeInfo');
    const submitBtnText = document.getElementById('submitBtnText');
    const footerText = document.getElementById('footerText');
    
    // Mode switching handlers
    predictModeBtn.addEventListener('click', function() {
        switchMode('predict');
    });
    
    contributeModeBtn.addEventListener('click', function() {
        switchMode('contribute');
    });
    
    // Initialize the form to predict mode on page load
    switchMode('predict');
    
    function switchMode(mode) {
        currentMode = mode;
        
        if (mode === 'predict') {
            // Switch to prediction mode
            predictModeBtn.classList.add('active');
            contributeModeBtn.classList.remove('active');
            sosSection.style.display = 'none';
            predictModeInfo.style.display = 'block';
            contributeModeInfo.style.display = 'none';
            submitBtnText.innerHTML = '🔮 Estimasi Skor Stres';
            footerText.innerHTML = '<em>Mode estimasi: Data tidak disimpan (privacy-preserving).<br>Estimation mode: Data is not saved (privacy-preserving).</em><p style="margin-top: 10px; font-size: 0.85rem; color: #999;"><strong>Disclaimer:</strong> Hasil estimasi adalah perhitungan statistik berbasis model machine learning, bukan diagnosis klinis. Untuk penilaian lebih lanjut, konsultasikan dengan profesional kesehatan mental.</p>';
            
            // Remove required from SOS-S questions
            document.querySelectorAll('.sos-section input[type="radio"]').forEach(input => {
                input.removeAttribute('required');
            });
        } else {
            // Switch to contribution mode
            contributeModeBtn.classList.add('active');
            predictModeBtn.classList.remove('active');
            sosSection.style.display = 'block';
            predictModeInfo.style.display = 'none';
            contributeModeInfo.style.display = 'block';
            submitBtnText.innerHTML = '🤝 Estimasi & Kontribusi Data';
            footerText.innerHTML = 'Data anonim akan disimpan untuk keperluan penelitian dan dapat digunakan untuk pembaruan model melalui proses retraining terkontrol.<br><em>Anonymous data will be saved for research purposes and can be used for model updates through controlled retraining processes.</em><p style="margin-top: 10px; font-size: 0.85rem; color: #999;"><strong>Disclaimer:</strong> Hasil estimasi adalah perhitungan statistik berbasis model machine learning, bukan diagnosis klinis. Untuk penilaian lebih lanjut, konsultasikan dengan profesional kesehatan mental.</p>';
            
            // Add required to SOS-S questions (first of each group)
            const sosQuestions = ['1_tidak_mampu', '2_kewalahan_tanggung_jawab', '3_keadaan_tidak_berpihak',
                                 '4_waktu_tidak_cukup', '5_tidak_berjalan_baik', '6_terburu_buru',
                                 '7_tidak_ada_jalan_keluar', '8_masalah_menumpuk', '9_ingin_menyerah',
                                 '10_memikul_beban_berat'];
            sosQuestions.forEach(q => {
                const firstInput = document.querySelector(`input[name="${q}"][value="1"]`);
                if (firstInput) firstInput.setAttribute('required', 'required');
            });
        }
        
        // Hide result when switching modes
        resultDiv.style.display = 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = collectFormData();
        
        // Validate required fields
        if (!validateForm(formData)) {
            alert('Mohon lengkapi semua field yang wajib diisi (Please fill in all required fields)');
            return;
        }
        
        // Validate SOS-S questions in contribute mode
        if (currentMode === 'contribute') {
            const sosQuestions = ['1_tidak_mampu', '2_kewalahan_tanggung_jawab', '3_keadaan_tidak_berpihak',
                                 '4_waktu_tidak_cukup', '5_tidak_berjalan_baik', '6_terburu_buru',
                                 '7_tidak_ada_jalan_keluar', '8_masalah_menumpuk', '9_ingin_menyerah',
                                 '10_memikul_beban_berat'];
            
            let missingSos = false;
            for (const q of sosQuestions) {
                if (!formData[q] || formData[q] === 0) {
                    missingSos = true;
                    break;
                }
            }
            
            if (missingSos) {
                alert('Mohon jawab semua 10 pertanyaan SOS-S (Please answer all 10 SOS-S questions)');
                // Scroll to SOS-S section
                sosSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                return;
            }
        }
        
        // Disable submit button and show loading
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⏳ Memproses...';
        
        try {
            // Determine endpoint based on mode
            const endpoint = currentMode === 'predict' ? '/predict' : '/contribute';
            
            // Send request
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayResult(data, currentMode);
                // Scroll to result
                resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                displayError(data.error || 'Terjadi kesalahan saat memproses data');
            }
            
        } catch (error) {
            console.error('Error:', error);
            displayError('Tidak dapat terhubung ke server. Mohon coba lagi.');
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
    
    // Collect all form data
    function collectFormData() {
        const formData = {};
        
        // Get all input elements (excluding radio buttons temporarily)
        const inputs = form.querySelectorAll('input:not([type="radio"]), select');
        
        inputs.forEach(input => {
            const name = input.name;
            
            if (!name) return;
            
            if (input.type === 'checkbox') {
                // For checkboxes, set TRUE if checked, FALSE otherwise
                formData[name] = input.checked ? 'TRUE' : 'FALSE';
            } else if (input.type === 'number') {
                // For numbers, parse as float
                formData[name] = input.value ? parseFloat(input.value) : 0;
            } else {
                // For text and select, use value as is
                formData[name] = input.value;
            }
        });
        
        // Handle radio buttons (PSS questions)
        const radioGroups = {};
        form.querySelectorAll('input[type="radio"]').forEach(radio => {
            if (radio.name && radio.checked) {
                formData[radio.name] = parseInt(radio.value);
            }
        });
        
        return formData;
    }
    
    // Validate form data
    function validateForm(formData) {
        // Check required fields (basic validation)
        const requiredFields = [
            'usia', 'jenis_kelamin', 'kota_asal', 'status_pernikahan',
            'jumlah_anak', 'usia_anak', 'bidang', 'lama_bekerja',
            'mode_bekerja', 'jarak', 'waktu_bekerja_seminggu', 'beban_sks',
            'mhs_bimbingan', 'jabatan_struktural', 'jabatan_fungsional',
            'sertifikasi', 'status_keaktifan', 'work_life_balance', 'gaji_sesuai'
        ];
        
        for (const field of requiredFields) {
            // Check if field is missing or empty string (but allow 0 as valid value)
            if (formData[field] === undefined || formData[field] === null || formData[field] === '') {
                console.log('Missing required field:', field);
                return false;
            }
        }
        
        return true;
    }
    
    // Display prediction result
    function displayResult(data, mode) {
        if (mode === 'predict') {
            // Estimation mode - show only predicted score
            const score = data.predicted_score;
            const level = data.stress_level;
            const modelInfo = data.model_info;
            
            resultContent.innerHTML = `
                <div class="result-box ${level.color}">
                    <div class="score-display" style="color: ${getColorCode(level.color)}">
                        ${score}
                    </div>
                    <div style="text-align: center; color: #666; margin-bottom: 10px;">
                        Estimasi Skor Stres / Estimated Stress Score
                    </div>
                    <div class="level-display" style="color: ${getColorCode(level.color)}">
                        ${level.level}
                    </div>
                    <div class="description">
                        ${level.description}
                    </div>
                </div>
                
                <div class="model-metadata">
                    <h4>📊 Informasi Model / Model Information</h4>
                    <p><strong>Model:</strong> ${modelInfo.model_name}</p>
                    <p><strong>Model Version:</strong> ${modelInfo.model_version}</p>
                    <p><strong>Training Samples:</strong> ${modelInfo.training_samples}</p>
                    <p><strong>Cross-Validated R²:</strong> ${modelInfo.r2_score}</p>
                </div>
                
                <div class="disclaimer-box">
                    <strong>⚠️ Disclaimer:</strong><br>
                    ${data.disclaimer}
                </div>
                
                <div class="thank-you">
                    <strong>✅ ${data.message}</strong>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="location.reload()" class="btn-submit">
                        🔄 Isi Form Lagi / Fill Again
                    </button>
                </div>
            `;
        } else {
            // Contribution mode - show both predicted and actual scores
            const predictedScore = data.predicted_score;
            const actualScore = data.actual_score;
            const predictedLevel = data.predicted_stress_level;
            const actualLevel = data.actual_stress_level;
            const modelInfo = data.model_info;
            
            resultContent.innerHTML = `
                <div class="comparison-container">
                    <div class="result-column">
                        <h4>🔮 Estimasi Model</h4>
                        <div class="result-box ${predictedLevel.color}">
                            <div class="score-display" style="color: ${getColorCode(predictedLevel.color)}">
                                ${predictedScore}
                            </div>
                            <div style="text-align: center; color: #666; margin-bottom: 10px;">
                                Estimated Score
                            </div>
                            <div class="level-display" style="color: ${getColorCode(predictedLevel.color)}">
                                ${predictedLevel.level}
                            </div>
                        </div>
                    </div>
                    
                    <div class="result-column">
                        <h4>📊 Skor Aktual (SOS-S)</h4>
                        <div class="result-box ${actualLevel.color}">
                            <div class="score-display" style="color: ${getColorCode(actualLevel.color)}">
                                ${actualScore}
                            </div>
                            <div style="text-align: center; color: #666; margin-bottom: 10px;">
                                Actual Score
                            </div>
                            <div class="level-display" style="color: ${getColorCode(actualLevel.color)}">
                                ${actualLevel.level}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="description" style="margin-top: 20px;">
                    <strong>Interpretasi Skor Aktual:</strong><br>
                    ${actualLevel.description}
                </div>
                
                <div class="model-metadata">
                    <h4>📊 Informasi Model / Model Information</h4>
                    <p><strong>Model:</strong> ${modelInfo.model_name}</p>
                    <p><strong>Model Version:</strong> ${modelInfo.model_version}</p>
                    <p><strong>Training Samples:</strong> ${modelInfo.training_samples}</p>
                    <p><strong>Cross-Validated R²:</strong> ${modelInfo.r2_score}</p>
                </div>
                
                <div class="disclaimer-box">
                    <strong>⚠️ Disclaimer:</strong><br>
                    ${data.disclaimer}
                </div>
                
                <div class="thank-you">
                    <strong>✅ ${data.message}</strong>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button onclick="location.reload()" class="btn-submit">
                        🔄 Isi Form Lagi / Fill Again
                    </button>
                </div>
            `;
        }
        
        resultDiv.style.display = 'block';
    }
    
    // Display error message
    function displayError(errorMessage) {
        resultContent.innerHTML = `
            <div class="error-message">
                <strong>❌ Error:</strong> ${errorMessage}
            </div>
        `;
        resultDiv.style.display = 'block';
    }
    
    // Get color code for level
    function getColorCode(colorName) {
        const colors = {
            'green': '#27ae60',
            'lightgreen': '#52c41a',
            'yellow': '#f39c12',
            'orange': '#e67e22',
            'red': '#e74c3c'
        };
        return colors[colorName] || '#2c3e50';
    }
    
    // Auto-calculate based on living situation
    const livingCheckboxes = document.querySelectorAll('[name^="tinggal_"]');
    livingCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // If "tinggal_sendiri" is checked, uncheck others
            if (this.name === 'tinggal_sendiri' && this.checked) {
                livingCheckboxes.forEach(cb => {
                    if (cb.name !== 'tinggal_sendiri') {
                        cb.checked = false;
                    }
                });
            }
            // If any other is checked, uncheck "tinggal_sendiri"
            else if (this.name !== 'tinggal_sendiri' && this.checked) {
                const tinggalSendiri = document.getElementById('tinggal_sendiri');
                if (tinggalSendiri) {
                    tinggalSendiri.checked = false;
                }
            }
        });
    });
    
    // Smart validation for children fields
    const jumlahAnakInput = document.getElementById('jumlah_anak');
    const usiaAnakInput = document.getElementById('usia_anak');
    
    if (jumlahAnakInput && usiaAnakInput) {
        jumlahAnakInput.addEventListener('change', function() {
            if (parseInt(this.value) === 0) {
                usiaAnakInput.value = 0;
            }
        });
    }
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Form progress indicator
    let totalFields = form.querySelectorAll('input[required], select[required]').length;
    let filledFields = 0;
    
    form.querySelectorAll('input, select').forEach(field => {
        field.addEventListener('change', function() {
            updateProgress();
        });
    });
    
    function updateProgress() {
        filledFields = 0;
        form.querySelectorAll('input[required], select[required]').forEach(field => {
            if (field.value !== '') {
                filledFields++;
            }
        });
        
        const progress = Math.round((filledFields / totalFields) * 100);
        console.log(`Form completion: ${progress}%`);
    }
    
    // Auto-capitalize text inputs: capitalize first letter and letters after spaces
    function titleCaseTransform(s) {
        return s.replace(/\b\w/g, function(ch) { return ch.toUpperCase(); });
    }

    document.querySelectorAll('input[type="text"]').forEach(input => {
        input.addEventListener('input', function(e) {
            const start = this.selectionStart;
            const end = this.selectionEnd;
            const orig = this.value;
            const transformed = titleCaseTransform(orig);
            if (transformed !== orig) {
                this.value = transformed;
                try { this.setSelectionRange(start, end); } catch (err) { /* ignore */ }
            }
        });
    });

    console.log('Stress Prediction System loaded successfully!');
});
