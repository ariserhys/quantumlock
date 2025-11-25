# 🔐 QuantumLock

> **Advanced Password Generator & Security Toolkit**  
> Generate cryptographically secure passwords, check breaches, and manage 2FA codes — all in one place.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start

### 1️⃣ Install
```bash
# Clone and setup
git clone https://github.com/ariserhys/QuantumLock.git
cd QuantumLock
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

### 2️⃣ Test It
```bash
# Generate a password
python -c "from backend.core import generate_password; print(generate_password(16))"

# Run the demo
python demo.py

# Start API server
python -m uvicorn backend.api.main:app --reload
```

### 3️⃣ Use the API
Open **http://localhost:8000/docs** in your browser - you'll see interactive documentation where you can test all features!

---

## ✨ What Can It Do?

### 🎲 **Generate Secure Passwords**
```python
from backend.core import generate_password
password = generate_password(20, use_symbols=True)
# Output: "X9#mK$2vL@pQ7nR4cD!s"
```

### 🔤 **Create Memorable Passphrases**
```python
from backend.core import generate_passphrase
passphrase = generate_passphrase(6)
# Output: "correct horse battery staple triumph puzzle"
```

### 🔍 **Analyze Password Strength**
```python
from backend.core import PasswordStrengthAnalyzer
analyzer = PasswordStrengthAnalyzer()
result = analyzer.analyze("MyP@ssw0rd")
print(f"Score: {result.score}/4")  # Score: 2/4 (Fair)
```

### ⚠️ **Check for Data Breaches**
```python
from backend.core import BreachChecker
checker = BreachChecker()
result = checker.check_password("password")
# "Found in 3,912,816 breaches" ❌
```

### 🔐 **Generate 2FA Codes**
```python
from backend.features import TOTPGenerator
generator = TOTPGenerator()
secret = generator.generate_secret("GitHub", "user@example.com")
code = generator.get_current_code(secret.secret)
# QR code ready for Google Authenticator!
```

---

## 🌐 API Endpoints

Once the server is running, visit **http://localhost:8000/docs** for the full interactive API.

### Password Generation
- `POST /api/v1/generate/password` - Generate strong password
- `POST /api/v1/generate/passphrase` - Generate passphrase

### Security Analysis
- `POST /api/v1/analyze/strength` - Check password strength
- `POST /api/v1/analyze/breach` - Check if password is breached
- `POST /api/v1/analyze/full` - Combined strength + breach check

### TOTP/2FA
- `POST /api/v1/totp/generate` - Create new TOTP secret
- `GET /api/v1/totp/current/{secret}` - Get current code
- `POST /api/v1/totp/verify` - Verify a code

**Quick API Test:**
```bash
curl -X POST http://localhost:8000/api/v1/generate/password \
  -H "Content-Type: application/json" \
  -d '{"length": 16, "use_symbols": true}'
```

---

## 🛡️ Security Features

| Feature | Description |
|---------|-------------|
| **CSPRNG** | Uses Python's `secrets` module for cryptographically secure randomness |
| **K-Anonymity** | Breach checks only send first 5 chars of hash - your password never leaves your device |
| **zxcvbn** | Industry-standard password strength estimation by Dropbox |
| **Argon2id** | State-of-the-art password hashing (memory=64MB, iterations=3) |
| **No Logging** | Passwords are never logged or stored in plaintext |

### Breach Checking Privacy
When you check if a password is breached:
1. Your password is hashed locally with SHA-1
2. Only the **first 5 characters** of the hash are sent to HaveIBeenPwned
3. Your actual password **never leaves your computer**
4. The API returns all matches, and we check locally

---

## 📁 Project Structure

```
QuantumLock/
├── backend/
│   ├── core/                  # Password generation & analysis
│   │   ├── password_generator.py
│   │   ├── passphrase_generator.py
│   │   ├── strength_analyzer.py
│   │   └── breach_checker.py
│   ├── features/              # TOTP, QR codes
│   ├── api/                   # FastAPI endpoints
│   └── config/                # Settings & configuration
├── demo.py                    # Run this to see everything in action
├── TESTING.md                 # How to test the project
└── QUICKSTART.md              # Detailed getting started guide
```

---

## 🧪 Testing

### Run the Demo
```bash
python demo.py
```
See password generation, strength analysis, breach checking, and TOTP in action!

### Test the API
```bash
# Start server
python -m uvicorn backend.api.main:app --reload

# Visit in browser
http://localhost:8000/docs
```

### Run Tests
```bash
pytest tests/ -v --cov=backend
```

---

## 🎯 Key Technologies

- **FastAPI** - Modern Python web framework with auto-generated docs
- **zxcvbn** - Password strength estimation
- **pyotp** - TOTP/2FA code generation  
- **qrcode** - QR code generation for mobile apps
- **HaveIBeenPwned API** - 800M+ breached password database

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed installation and usage guide
- **[TESTING.md](TESTING.md)** - How to test all features
- **API Docs** - http://localhost:8000/docs (when server is running)

---

## 🗺️ Roadmap

- [x] Password & passphrase generation
- [x] Strength analysis with zxcvbn
- [x] Breach checking with HaveIBeenPwned
- [x] TOTP/2FA generation
- [x] REST API with Swagger docs
- [ ] Encrypted password vault
- [ ] CLI interface with Typer
- [ ] React web frontend
- [ ] Docker deployment

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- [Dropbox zxcvbn](https://github.com/dropbox/zxcvbn) - Password strength estimation
- [HaveIBeenPwned](https://haveibeenpwned.com/) - Breach database by Troy Hunt
- [EFF Diceware](https://www.eff.org/dice) - Wordlist for passphrases
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

---

<div align="center">

**Made with 🔐 by the QuantumLock Team**

[Report Bug](https://github.com/ariserhys/QuantumLock/issues) · [Request Feature](https://github.com/ariserhys/QuantumLock/issues)

</div>
