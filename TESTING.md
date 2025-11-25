# 🧪 Testing QuantumLock - Quick Guide

## Option 1: Run the Demo Script (✅ Already Works!)

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run demo
python demo.py
```

**What it shows:**
- Password generation examples
- Passphrase generation (Diceware & BIP39)
- Strength analysis for various passwords
- Breach checking with HaveIBeenPwned
- TOTP/2FA code generation

---

## Option 2: Test the API Server

### Step 1: Start the Server
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start API server
uvicorn backend.api.main:app --reload
```

### Step 2: Open API Docs
Visit in your browser:
- **http://localhost:8000/docs** (Interactive Swagger UI)
- **http://localhost:8000/redoc** (Alternative docs)

### Step 3: Try the Endpoints

Click "Try it out" in the Swagger UI, or use curl:

#### Generate a Password
```bash
curl -X POST http://localhost:8000/api/v1/generate/password -H "Content-Type: application/json" -d "{\"length\": 16, \"use_symbols\": true}"
```

#### Analyze Password Strength
```bash
curl -X POST http://localhost:8000/api/v1/analyze/strength -H "Content-Type: application/json" -d "{\"password\": \"MyP@ssw0rd123\"}"
```

#### Check for Breaches
```bash
curl -X POST http://localhost:8000/api/v1/analyze/breach -H "Content-Type: application/json" -d "{\"password\": \"password\"}"
```

#### Generate TOTP Secret
```bash
curl -X POST http://localhost:8000/api/v1/totp/generate -H "Content-Type: application/json" -d "{\"issuer\": \"GitHub\", \"account_name\": \"user@example.com\"}"
```

---

## Option 3: Test Individual Modules

### Test Password Generator
```bash
.\venv\Scripts\Activate.ps1
python -c "from backend.core import generate_password; print(generate_password(20))"
```

### Test Passphrase Generator
```bash
python -c "from backend.core import generate_passphrase; print(generate_passphrase(6))"
```

### Test Strength Analyzer
```bash
python -c "from backend.core import PasswordStrengthAnalyzer; a = PasswordStrengthAnalyzer(); r = a.analyze('MyP@ssw0rd'); print(f'Score: {r.score}/4, Entropy: {r.shannon_entropy:.2f}')"
```

---

## 🎯 Quick Start (Recommended)

1. **Run the demo first:**
   ```bash
   .\venv\Scripts\Activate.ps1
   python demo.py
   ```

2. **Then start the API:**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

3. **Open your browser:**
   - Go to http://localhost:8000/docs
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters and click "Execute"

---

## 🐛 Troubleshooting

### If `python demo.py` fails:
```bash
# Install missing dependencies
pip install requests pyotp qrcode pillow zxcvbn pydantic-settings
```

### If API won't start:
```bash
# Make sure you're in the virtual environment
.\venv\Scripts\Activate.ps1

# Check if FastAPI is installed
pip install fastapi uvicorn
```

### If you get import errors:
```bash
# Make sure you're in the project directory
cd "c:\Users\AVITA\Documents\Github Sync\QuantumLock"
```

---

## ✅ What You Should See

### Demo Output:
```
🔐 QuantumLock Demo
==================

🎲 Password Generation
Simple (16 chars): X9#mK$2vL@pQ7nR
Strong (20 chars): MyP@ssw0rd!2024#Secure

🔤 Passphrase Generation
Diceware (6 words): correct horse battery staple triumph puzzle

🔍 Password Strength Analysis
Score: 0/4 (Very Weak) for "password"
Score: 4/4 (Very Strong) for "X9#mK$2vL@pQ7nR"

⚠️ Breach Checking
password: ❌ Found in 3,912,816 breaches
```

### API Server:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
🚀 Starting QuantumLock API v0.1.0
📍 API Docs: http://127.0.0.1:8000/docs
```
