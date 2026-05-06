# 📝 Form Customization Guide

This guide explains how to customize the web form questions and answer options.

## 🎯 Quick Reference

| What to Change | File to Edit | Restart Required? |
|----------------|--------------|-------------------|
| Question labels (text) | `web_app/app.py` | Yes |
| Dropdown options | `web_app/categorical_options.json` | Yes |
| Add/remove questions | `web_app/templates/index.html` | Yes |
| Form layout | `web_app/templates/index.html` | Yes |
| Styling | `web_app/static/style.css` | No (refresh browser) |

---

## 1️⃣ Change Question Labels (How Questions Appear)

**File:** `web_app/app.py` (Lines 58-115)

### Example: Change a question label

**Before:**
```python
'usia': 'Usia (Age)',
```

**After:**
```python
'usia': 'Umur Anda (Your Age)',
```

### Tips:
- Use bilingual format: `'Indonesian (English)'`
- Be clear and concise
- After editing, restart the web app:
  ```bash
  cd web_app
  python3 app.py
  ```

---

## 2️⃣ Change Dropdown Options (Answer Choices)

**File:** `web_app/categorical_options.json`

This file is **auto-generated** from your training data, but you can manually edit it!

### Example: Add more gender options

**Current:**
```json
"jenis_kelamin": [
  "Laki-laki",
  "Perempuan"
]
```

**Modified:**
```json
"jenis_kelamin": [
  "Laki-laki",
  "Perempuan",
  "Lainnya"
]
```

### Example: Add more work mode options

**Current:**
```json
"mode_bekerja": [
  "Hybrid",
  "On-site"
]
```

**Modified:**
```json
"mode_bekerja": [
  "On-site",
  "Hybrid",
  "Work From Home (WFH)",
  "Remote"
]
```

### Example: Clean up city names

**Current:**
```json
"kota_asal": [
  "KLATEN",
  "kediri",
  "Kediri",
  "Bandar Lampunh"
]
```

**Better:**
```json
"kota_asal": [
  "Banda Aceh",
  "Bandar Lampung",
  "Bandung",
  "Jakarta",
  "Kediri",
  "Klaten",
  "Yogyakarta"
]
```

### ⚠️ Important Notes:
1. **Keep exact spelling** for values already in your training data
2. **Alphabetize** options for easier finding
3. After editing, restart the web app
4. New options will be handled by the model (via `handle_unknown='ignore'` in preprocessing)

---

## 3️⃣ Add Custom Options Not From Training Data

If you want to add options that **don't exist in your training data** yet:

### Step 1: Edit `categorical_options.json`

Add your new options:
```json
"jabatan_struktural": [
  "Non Jabatan Struktural",
  "Setingkat Kaprodi dan Ketua KK",
  "Setingkat Dekan dan Kepala UPA / UPT",
  "Jabatan Struktural Lainnya",
  "Wakil Rektor",
  "Rektor"
]
```

### Step 2: That's it!

The model will handle unknown values gracefully because we use `OneHotEncoder(handle_unknown='ignore')` in the preprocessing.

When you retrain with new data containing these values, the model will learn from them!

---

## 4️⃣ Modify Fixed Options (1-5 Scales)

These are hardcoded in the HTML template.

**File:** `web_app/templates/index.html`

### Example: Change work-life balance scale

**Find (around line 222):**
```html
<select id="work_life_balance" name="work_life_balance" required>
    <option value="">Pilih...</option>
    <option value="1">1 - Sangat Buruk</option>
    <option value="2">2 - Buruk</option>
    <option value="3">3 - Cukup</option>
    <option value="4">4 - Baik</option>
    <option value="5">5 - Sangat Baik</option>
</select>
```

**Modify to 1-10 scale:**
```html
<select id="work_life_balance" name="work_life_balance" required>
    <option value="">Pilih...</option>
    <option value="1">1 - Sangat Buruk</option>
    <option value="2">2</option>
    <option value="3">3</option>
    <option value="4">4</option>
    <option value="5">5 - Cukup</option>
    <option value="6">6</option>
    <option value="7">7</option>
    <option value="8">8</option>
    <option value="9">9</option>
    <option value="10">10 - Sangat Baik</option>
</select>
```

---

## 5️⃣ Add a Completely New Question

### Example: Add "Years of Teaching" field

**Step 1: Add to HTML form** (`web_app/templates/index.html`)

Find a relevant section and add:
```html
<div class="form-group">
    <label for="tahun_mengajar">Tahun Mengajar (Years Teaching): *</label>
    <input type="number" id="tahun_mengajar" name="tahun_mengajar" 
           required min="0" max="50" step="1">
</div>
```

**Step 2: Add label to app.py**

In `create_feature_labels()` function:
```python
'tahun_mengajar': 'Lama Mengajar (Years of Teaching)',
```

**Step 3: Update training data**

Add the column to `data/burnout_submissions.csv` with values for all rows.

**Step 4: Retrain the model**
```bash
python3 train_model.py
```

---

## 6️⃣ Remove a Question

### Example: Remove "usia_anak" field

**Step 1: Remove from HTML** (`web_app/templates/index.html`)

Delete or comment out:
```html
<!-- REMOVED:
<div class="form-group">
    <label for="usia_anak">{{ feature_labels.usia_anak }}: *</label>
    <input type="number" id="usia_anak" name="usia_anak" ...>
</div>
-->
```

**Step 2: Update JavaScript validation** (`web_app/static/script.js`)

Remove from required fields list (around line 65):
```javascript
// Remove 'usia_anak' from this array:
const requiredFields = [
    'usia', 'jenis_kelamin', 'kota_asal', 'status_pernikahan',
    'jumlah_anak', // 'usia_anak', <- REMOVED
    'bidang', 'lama_bekerja',
    // ... rest
];
```

**Step 3: Handle in backend** (`web_app/app.py`)

Add default value in predict function (around line 140):
```python
# Add default for removed field
if 'usia_anak' not in df.columns:
    df['usia_anak'] = 0
```

---

## 7️⃣ Change Form Section Titles

**File:** `web_app/templates/index.html`

Find section headers:
```html
<h3>📋 Data Demografi (Demographics)</h3>
```

Change to whatever you want:
```html
<h3>👤 Informasi Pribadi (Personal Information)</h3>
```

---

## 8️⃣ Testing Your Changes

### Quick Test Checklist:

1. ✅ Edit the files
2. ✅ Restart web app: `python3 app.py`
3. ✅ Refresh browser (Ctrl+F5 for hard refresh)
4. ✅ Test form submission
5. ✅ Check prediction still works

### Verify Changes:
```bash
# Check if web app loads without errors
cd web_app
python3 app.py

# Should see:
# ✓ Loaded model: SVR
# Starting Stress Prediction Web Application
```

---

## 🔄 Common Customization Workflows

### Workflow 1: Quick Label Changes
```bash
1. Edit web_app/app.py (change labels)
2. Restart: python3 app.py
3. Done!
```

### Workflow 2: Add More Options
```bash
1. Edit web_app/categorical_options.json
2. Restart: python3 app.py
3. Test form
4. Collect data with new options
5. Retrain when you have 20+ new samples
```

### Workflow 3: Major Form Restructure
```bash
1. Edit web_app/templates/index.html
2. Edit web_app/app.py (labels)
3. Edit web_app/static/script.js (validation)
4. Update data/burnout_submissions.csv structure
5. Retrain: python3 train_model.py
6. Restart: python3 app.py
```

---

## 📋 File Quick Reference

```
web_app/
├── app.py                      # Question labels, backend logic
├── categorical_options.json    # Dropdown options
├── templates/
│   └── index.html             # Form structure, hardcoded options
└── static/
    ├── script.js              # Form validation, field lists
    └── style.css              # Visual styling
```

---

## ⚠️ Important Reminders

1. **Always restart the web app** after editing Python files
2. **Hard refresh browser** (Ctrl+F5) after editing HTML/CSS/JS
3. **Keep backups** before major changes
4. **Test thoroughly** after modifications
5. **Retrain model** if you change which features are collected

---

## 💡 Pro Tips

### Tip 1: Preview Options by Dataset Size
Current `categorical_options.json` shows only values from your 49 training samples. As you collect more data, more options will appear automatically when you retrain.

### Tip 2: Pre-populate Common Options
Manually add common options now to make data collection easier:
```json
"kota_asal": [
  "Banda Aceh", "Bandung", "Jakarta", "Surabaya", "Yogyakarta",
  "Semarang", "Medan", "Palembang", "Makassar", "Denpasar",
  "Lainnya"
]
```

### Tip 3: Use "Lainnya" (Other) Option
Always include an "Other" option for categorical fields to capture unexpected responses.

### Tip 4: Document Your Changes
Keep a changelog in your LOGBOOK.md:
```markdown
## 2026-03-02 - Form Customization
- Added "Lainnya" option to gender field
- Expanded city list with major Indonesian cities
- Changed work-life balance scale from 1-5 to 1-10
```

---

## 🆘 Troubleshooting

### Problem: Changes don't appear
**Solution:** Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)

### Problem: Form validation fails
**Solution:** Check `script.js` validiation matches your HTML field names

### Problem: Prediction fails with new options
**Solution:** Model handles new categories gracefully, but retrain with real data when you can

### Problem: Options not showing in dropdown
**Solution:** Check `categorical_options.json` formatting (valid JSON, proper quotes)

---

## 🎯 Example: Complete Customization

Let's say you want to add a "Institusi" (Institution) dropdown:

### 1. Add to `categorical_options.json`:
```json
"institusi": [
  "Institut Teknologi Sumatera",
  "Universitas Indonesia",
  "Institut Teknologi Bandung",
  "Universitas Gadjah Mada",
  "Lainnya"
]
```

### 2. Add label to `app.py`:
```python
'institusi': 'Nama Institusi (Institution Name)',
```

### 3. Add to HTML form (after "Demographics" section):
```html
<div class="form-group">
    <label for="institusi">{{ feature_labels.institusi }}: *</label>
    <select id="institusi" name="institusi" required>
        <option value="">Pilih...</option>
        {% for option in categorical_options.institusi %}
            <option value="{{ option }}">{{ option }}</option>
        {% endfor %}
    </select>
</div>
```

### 4. Add to validation in `script.js`:
```javascript
const requiredFields = [
    'usia', 'jenis_kelamin', 'institusi', 'kota_asal', // <- added
    // ... rest
];
```

### 5. Test and restart:
```bash
cd web_app
python3 app.py
```

Done! 🎉

---

**Need help with specific customizations? Check the relevant section above or ask!**
