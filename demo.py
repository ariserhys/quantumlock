"""
QuantumLock Demo Script

Demonstrates all core features of QuantumLock.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core import (
    generate_password,
    generate_passphrase,
    PasswordGenerator,
    PasswordConfig,
    PassphraseGenerator,
    PassphraseConfig,
    PasswordStrengthAnalyzer,
    BreachChecker,
)
from backend.features import TOTPGenerator


def print_header(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_password_generation():
    """Demo password generation"""
    print_header("🎲 Password Generation")
    
    # Simple password
    simple = generate_password(length=16)
    print(f"Simple (16 chars): {simple}")
    
    # Strong password with requirements
    config = PasswordConfig(
        length=20,
        min_uppercase=2,
        min_lowercase=2,
        min_digits=2,
        min_symbols=2,
    )
    generator = PasswordGenerator(config)
    strong = generator.generate()
    entropy = generator.calculate_entropy(strong)
    
    print(f"Strong (20 chars):  {strong}")
    print(f"Entropy: {entropy:.2f} bits")
    
    # No symbols (for systems that don't support them)
    no_symbols = generate_password(length=16, use_symbols=False)
    print(f"No symbols (16):    {no_symbols}")


def demo_passphrase_generation():
    """Demo passphrase generation"""
    print_header("🔤 Passphrase Generation")
    
    # Diceware (default)
    diceware = generate_passphrase(word_count=6)
    print(f"Diceware (6 words): {diceware}")
    
    # BIP39
    bip39 = generate_passphrase(word_count=12, wordlist_type="bip39")
    print(f"BIP39 (12 words):   {bip39}")
    
    # Custom (capitalized, with number and symbol)
    config = PassphraseConfig(
        word_count=7,
        separator="-",
        capitalize_words=True,
        add_number=True,
        add_symbol=True,
    )
    generator = PassphraseGenerator(config)
    custom = generator.generate()
    entropy = generator.calculate_entropy()
    
    print(f"Custom (7 words):   {custom}")
    print(f"Entropy: {entropy:.2f} bits")


def demo_strength_analysis():
    """Demo password strength analysis"""
    print_header("🔍 Password Strength Analysis")
    
    test_passwords = [
        ("password", "Very weak password"),
        ("P@ssw0rd", "Common password"),
        ("MyP@ssw0rd123", "Medium strength"),
        ("correct horse battery staple", "Famous xkcd passphrase"),
        ("X9#mK$2vL@pQ7nR", "Strong random password"),
    ]
    
    analyzer = PasswordStrengthAnalyzer()
    
    for pwd, description in test_passwords:
        result = analyzer.analyze(pwd)
        
        print(f"\n{description}")
        print(f"  Password: {pwd}")
        print(f"  Score: {result.score}/4 ({result.get_score_label()})")
        print(f"  Entropy: {result.shannon_entropy:.2f} bits/char")
        print(f"  Crack time: {result.crack_time_display}")
        
        if result.feedback["warning"]:
            print(f"  ⚠️  {result.feedback['warning']}")


def demo_breach_checking():
    """Demo breach checking"""
    print_header("⚠️  Breach Checking (HaveIBeenPwned)")
    
    print("Note: Using k-anonymity - only first 5 chars of SHA-1 hash sent to API\n")
    
    test_passwords = [
        ("password", "Known breached password"),
        ("X9#mK$2vL@pQ7nR", "Strong random (unlikely breached)"),
    ]
    
    checker = BreachChecker()
    
    for pwd, description in test_passwords:
        print(f"{description}")
        print(f"  Password: {pwd}")
        
        try:
            result = checker.check_password(pwd)
            
            if result.is_breached:
                print(f"  ❌ {result.message}")
            else:
                print(f"  ✓ {result.message}")
        
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print()


def demo_totp():
    """Demo TOTP generation"""
    print_header("🔐 TOTP / 2FA Generator")
    
    generator = TOTPGenerator()
    
    # Generate new secret
    secret = generator.generate_secret("GitHub", "user@example.com")
    
    print(f"Service: {secret.issuer}")
    print(f"Account: {secret.account_name}")
    print(f"Secret: {secret.secret}")
    print(f"URI: {secret.uri}\n")
    
    # Get current code
    code = generator.get_current_code(secret.secret)
    print(f"Current TOTP code: {code}")
    print(f"(Changes every 30 seconds)\n")
    
    # Verify code
    is_valid = generator.verify_code(secret.secret, code)
    print(f"Code verification: {'✓ Valid' if is_valid else '❌ Invalid'}\n")
    
    # Backup codes
    backup_codes = generator.generate_backup_codes(5)
    print(f"Backup codes (store securely):")
    for i, code in enumerate(backup_codes, 1):
        print(f"  {i}.{code}")


def main():
    """Run all demos"""
    print("\n" * 2)
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "🔐 QuantumLock Demo" + " "*29 + "║")
    print("║" + " "*10 + "Advanced Password Generator & Analyzer" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        demo_password_generation()
        demo_passphrase_generation()
        demo_strength_analysis()
        demo_breach_checking()  # This requires internet connection
        demo_totp()
        
        print_header("✅ Demo Complete!")
        print("Next steps:")
        print("  1. Start the API server: uvicorn backend.api.main:app --reload")
        print("  2. Visit http://localhost:8000/docs for interactive API docs")
        print("  3. Try the CLI: quantumlock --help")
        print()
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
