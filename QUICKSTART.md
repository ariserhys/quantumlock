# QuantumLock - Quick Start Guide

## 🚀 Getting Started

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/QuantumLock.git
cd QuantumLock

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo.py
```

This will demonstrate:
- Password generation
- Passphrase generation  
- Strength analysis
- Breach checking
- TOTP/2FA generation

### 3. Start the API Server

```bash
# Option 1: Using uvicorn directly
uvicorn backend.api.main:app --reload

# Option 2: Using Python
python -m backend.api.main
```

Visit **http://localhost:8000/docs** for interactive API documentation!

### 4. Try the API

#### Generate a password:
```bash
curl -X POST http://localhost:8000/api/v1/generate/password \
  -H "Content-Type: application/json" \
  -d '{"length": 20, "use_symbols": true}'
```

#### Analyze password strength:
```bash
curl -X POST http://localhost:8000/api/v1/analyze/strength \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd123"}'
```

#### Check for breaches:
```bash
curl -X POST http://localhost:8000/api/v1/analyze/breach \
  -H "Content-Type: application/json" \
  -d '{"password": "password123"}'
```

#### Generate TOTP secret:
```bash
curl -X POST http://localhost:8000/api/v1/totp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "issuer": "GitHub",
    "account_name": "user@example.com"
  }'
```

## 📁 Project Structure

```
QuantumLock/
├── backend/
│   ├── api/              # FastAPI endpoints
│   │   ├── main.py      # Application entry point
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── generator.py    # Password/passphrase generation
│   │           ├── analyzer.py     # Strength/breach analysis
│   │           └── totp.py        # 2FA/TOTP codes
│   ├── core/            # Core functionality
│   │   ├── password_generator.py  # CSPRNG password generation
│   │   ├── passphrase_generator.py # Diceware/BIP39 passphrases
│   │   ├── strength_analyzer.py   # zxcvbn integration
│   │   └── breach_checker.py     # HaveIBeenPwned API
│   ├── features/        # Additional features
│   │   └── totp_generator.py     # TOTP/2FA with QR codes
│   ├── config/          # Configuration
│   │   └── settings.py           # Pydantic settings
│   └── utils/          # Utilities
│       └── wordlists/             # Diceware & BIP39 word lists
├── tests/               # Test suite
├── docs/                # Documentation
├── demo.py              # Feature demonstration
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Package configuration
└── README.md           # Project overview
```

## ⚡ Key Features

### 🎲 Password Generation
- **CSPRNG-based**: Uses Python's `secrets` module for true randomness
- **Highly customizable**: Length, character sets, minimum requirements
- **Policy enforcement**: No repeating chars, exclude specific characters

### 🔤 Passphrase Generation
- **Diceware**: 7776-word EFF list (~12.9 bits/word entropy)
- **BIP39**: 2048-word Bitcoin list (~11 bits/word)
- **Dice simulation**: Simulates physical dice rolls for true randomness

### 🔍 Strength Analysis
- **zxcvbn scoring**: Industry-standard password strength estimation
- **Shannon entropy**: Information theory-based analysis
- **Crack time estimates**: Multiple attack scenarios
- **Pattern detection**: Sequential/repeating chars, keyboard patterns

### ⚠️ Breach Checking
- **K-anonymity protocol**: Only first 5 chars of SHA-1 hash sent to API
- **HaveIBeenPwned**: 800M+ breached passwords
- **Privacy-preserving**: Your password never leaves your system

### 🔐 TOTP/2FA
- **Google Authenticator compatible**: Standard TOTP implementation
- **QR code generation**: Easy mobile setup
- **Backup codes**: Account recovery
- **Customizable**: 6/8 digits, 30/60 second intervals

## 🔒 Security

- **CSPRNG**: All randomness uses `secrets` module (cryptographically secure)
- **Argon2id**: State-of-the-art password hashing
- **AES-256**: Fernet encryption for vault
- **No logging**: Passwords are never logged
- **K-anonymity**: Breach checks preserve privacy

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛠️ Development

### Run tests:
```bash
pytest tests/ -v --cov
```

### Code quality:
```bash
# Format code
ruff backend/ cli/ --fix

# Type checking
mypy backend/ cli/

# Security scan
bandit -r backend/
```

## 🤝 Next Steps

1. **CLI Development**: Implement Typer-based command-line interface
2. **Web Frontend**: Build React app with dark/light themes
3. **Vault**: Encrypted password storage with SQLCipher
4. **Docker**: Containerization for easy deployment
5. **Tests**: Comprehensive unit and integration tests

## 📝 License

MIT License - see LICENSE file for details.

---

**Made with 🔐 by the QuantumLock Team**
