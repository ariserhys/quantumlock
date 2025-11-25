"""Core modules initialization"""
from .password_generator import PasswordGenerator, PasswordConfig, generate_password
from .passphrase_generator import PassphraseGenerator, PassphraseConfig, generate_passphrase
from .strength_analyzer import PasswordStrengthAnalyzer, StrengthResult
from .breach_checker import BreachChecker, BreachResult, check_breach

__all__ = [
    "PasswordGenerator",
    "PasswordConfig",
    "generate_password",
    "PassphraseGenerator",
    "PassphraseConfig",
    "generate_passphrase",
    "PasswordStrengthAnalyzer",
    "StrengthResult",
    "BreachChecker",
    "BreachResult",
    "check_breach",
]
