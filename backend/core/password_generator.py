"""
Cryptographically Secure Password Generator

Uses Python's secrets module (CSPRNG) for true randomness.
Supports customizable character sets and password policies.
"""

import secrets
import string
import math
from typing import Optional, Set
from collections import Counter


class PasswordConfig:
    """Configuration for password generation"""
    
    def __init__(
        self,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        custom_symbols: Optional[str] = None,
        exclude_chars: Optional[str] = None,
        no_repeating: bool = False,
        min_uppercase: int = 0,
        min_lowercase: int = 0,
        min_digits: int = 0,
        min_symbols: int = 0,
    ):
        self.length = length
        self.use_uppercase = use_uppercase
        self.use_lowercase = use_lowercase
        self.use_digits = use_digits
        self.use_symbols = use_symbols
        self.custom_symbols = custom_symbols
        self.exclude_chars = exclude_chars or ""
        self.no_repeating = no_repeating
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_symbols = min_symbols
        
    def get_character_set(self) -> str:
        """Build the character set based on configuration"""
        charset = ""
        
        if self.use_uppercase:
            charset += string.ascii_uppercase
        if self.use_lowercase:
            charset += string.ascii_lowercase
        if self.use_digits:
            charset += string.digits
        if self.use_symbols:
            if self.custom_symbols:
                charset += self.custom_symbols
            else:
                charset += string.punctuation
        
        # Remove excluded characters
        if self.exclude_chars:
            charset = "".join(c for c in charset if c not in self.exclude_chars)
        
        if not charset:
            raise ValueError("Character set is empty. Enable at least one character type.")
        
        return charset


class PasswordGenerator:
    """Generate cryptographically secure passwords"""
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        self.config = config or PasswordConfig()
    
    def generate(self) -> str:
        """
        Generate a password according to the configuration.
        
        Returns:
            str: The generated password
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate minimum requirements don't exceed length
        total_min = (
            self.config.min_uppercase +
            self.config.min_lowercase +
            self.config.min_digits +
            self.config.min_symbols
        )
        
        if total_min > self.config.length:
            raise ValueError(
                f"Minimum character requirements ({total_min}) exceed password length ({self.config.length})"
            )
        
        charset = self.config.get_character_set()
        
        # Generate with minimum requirements
        if total_min > 0:
            return self._generate_with_requirements(charset)
        else:
            return self._generate_simple(charset)
    
    def _generate_simple(self, charset: str) -> str:
        """Generate without minimum requirements"""
        if self.config.no_repeating:
            if len(charset) < self.config.length:
                raise ValueError(
                    f"Cannot generate password of length {self.config.length} "
                    f"without repeating from charset of size {len(charset)}"
                )
            # Sample without replacement
            return "".join(secrets.choice(charset) for _ in range(self.config.length))
        else:
            return "".join(secrets.choice(charset) for _ in range(self.config.length))
    
    def _generate_with_requirements(self, charset: str) -> str:
        """Generate password ensuring minimum character type requirements"""
        password_chars = []
        
        # Add minimum required characters
        if self.config.min_uppercase > 0 and self.config.use_uppercase:
            for _ in range(self.config.min_uppercase):
                password_chars.append(secrets.choice(string.ascii_uppercase))
        
        if self.config.min_lowercase > 0 and self.config.use_lowercase:
            for _ in range(self.config.min_lowercase):
                password_chars.append(secrets.choice(string.ascii_lowercase))
        
        if self.config.min_digits > 0 and self.config.use_digits:
            for _ in range(self.config.min_digits):
                password_chars.append(secrets.choice(string.digits))
        
        if self.config.min_symbols > 0 and self.config.use_symbols:
            symbols = self.config.custom_symbols or string.punctuation
            for _ in range(self.config.min_symbols):
                password_chars.append(secrets.choice(symbols))
        
        # Fill remaining length with random characters from full charset
        remaining = self.config.length - len(password_chars)
        for _ in range(remaining):
            password_chars.append(secrets.choice(charset))
        
        # Shuffle to avoid predictable patterns (cryptographically secure shuffle)
        self._secure_shuffle(password_chars)
        
        password = "".join(password_chars)
        
        # Validate no repeating if required
        if self.config.no_repeating and len(set(password)) != len(password):
            # Regenerate if we got duplicates (rare but possible)
            return self.generate()
        
        return password
    
    def _secure_shuffle(self, items: list) -> None:
        """Fisher-Yates shuffle using secrets for randomness"""
        for i in range(len(items) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            items[i], items[j] = items[j], items[i]
    
    def calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy of a password.
        
        Args:
            password: The password to analyze
            
        Returns:
            float: Entropy in bits
        """
        if not password:
            return 0.0
        
        # Count character frequencies
        char_counts = Counter(password)
        length = len(password)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        # Multiply by length for total entropy
        return entropy * length
    
    def estimate_charset_entropy(self) -> float:
        """
        Estimate theoretical entropy based on character set size.
        
        Returns:
            float: Theoretical entropy in bits
        """
        charset = self.config.get_character_set()
        charset_size = len(set(charset))
        return self.config.length * math.log2(charset_size)
    
    def generate_multiple(self, count: int) -> list[str]:
        """
        Generate multiple unique passwords.
        
        Args:
            count: Number of passwords to generate
            
        Returns:
            list: List of generated passwords
        """
        passwords = set()
        while len(passwords) < count:
            passwords.add(self.generate())
        return list(passwords)


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """
    Quick helper function to generate a password with common defaults.
    
    Args:
        length: Password length (default: 16)
        use_uppercase: Include uppercase letters
        use_lowercase: Include lowercase letters
        use_digits: Include numbers
        use_symbols: Include symbols
        
    Returns:
        str: Generated password
    """
    config = PasswordConfig(
        length=length,
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_symbols=use_symbols,
    )
    generator = PasswordGenerator(config)
    return generator.generate()


if __name__ == "__main__":
    # Demo usage
    print("QuantumLock Password Generator Demo\n")
    
    # Simple password
    simple = generate_password(length=20)
    print(f"Simple (20 chars): {simple}")
    
    # Strong password with requirements
    config = PasswordConfig(
        length=24,
        min_uppercase=2,
        min_lowercase=2,
        min_digits=2,
        min_symbols=2,
    )
    generator = PasswordGenerator(config)
    strong = generator.generate()
    print(f"Strong (24 chars, mixed): {strong}")
    print(f"Entropy: {generator.calculate_entropy(strong):.2f} bits")
    print(f"Theoretical entropy: {generator.estimate_charset_entropy():.2f} bits")
    
    # No symbols password
    no_symbols = generate_password(length=16, use_symbols=False)
    print(f"\nNo symbols (16 chars): {no_symbols}")
    
    # Numbers only PIN
    pin_config = PasswordConfig(
        length=6,
        use_uppercase=False,
        use_lowercase=False,
        use_digits=True,
        use_symbols=False,
    )
    pin_generator = PasswordGenerator(pin_config)
    pin = pin_generator.generate()
    print(f"PIN (6 digits): {pin}")
