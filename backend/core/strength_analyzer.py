"""
Password Strength Analyzer

Integrates with zxcvbn for comprehensive password strength assessment.
Calculates Shannon entropy and estimates crack time.
"""

import math
import time
from collections import Counter
from typing import Optional, Dict, Any
from datetime import timedelta


try:
    import zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False


class StrengthResult:
    """Result of password strength analysis"""
    
    def __init__(
        self,
        password: str,
        score: int,  # 0-4 (very weak to very strong)
        shannon_entropy: float,
        crack_time_seconds: float,
        crack_time_display: str,
        feedback: Dict[str, Any],
        guesses: Optional[int] = None,
        pattern_analysis: Optional[Dict[str, Any]] = None,
    ):
        self.password_length = len(password)
        self.score = score
        self.shannon_entropy = shannon_entropy
        self.crack_time_seconds = crack_time_seconds
        self.crack_time_display = crack_time_display
        self.feedback = feedback
        self.guesses = guesses
        self.pattern_analysis = pattern_analysis or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "password_length": self.password_length,
            "score": self.score,
            "score_label": self.get_score_label(),
            "shannon_entropy": round(self.shannon_entropy, 2),
            "crack_time_seconds": self.crack_time_seconds,
            "crack_time_display": self.crack_time_display,
            "crack_time_scenarios": self.get_crack_scenarios(),
            "feedback": self.feedback,
            "guesses": self.guesses,
            "pattern_analysis": self.pattern_analysis,
        }
    
    def get_score_label(self) -> str:
        """Get human-readable score label"""
        labels = {
            0: "Very Weak",
            1: "Weak",
            2: "Fair",
            3: "Strong",
            4: "Very Strong",
        }
        return labels.get(self.score, "Unknown")
    
    def get_crack_scenarios(self) -> Dict[str, str]:
        """Get crack time for different attack scenarios"""
        return {
            "online_throttled": self._format_crack_time(self.crack_time_seconds * 100),
            "online_unthrottled": self._format_crack_time(self.crack_time_seconds * 10),
            "offline_slow": self._format_crack_time(self.crack_time_seconds),
            "offline_fast": self._format_crack_time(self.crack_time_seconds / 100),
        }
    
    def _format_crack_time(self, seconds: float) -> str:
        """Format seconds into human-readable time"""
        if seconds < 1:
            return "Instant"
        elif seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours"
        elif seconds < 2592000:  # 30 days
            return f"{int(seconds / 86400)} days"
        elif seconds < 31536000:  # 365 days
            return f"{int(seconds / 2592000)} months"
        else:
            years = int(seconds / 31536000)
            if years > 1000000:
                return f"{years / 1000000:.1f} million years"
            elif years > 1000:
                return f"{years / 1000:.1f} thousand years"
            else:
                return f"{years} years"


class PasswordStrengthAnalyzer:
    """Analyze password strength using multiple methods"""
    
    def __init__(self):
        self.zxcvbn_available = ZXCVBN_AVAILABLE
    
    def analyze(self, password: str, user_inputs: Optional[list[str]] = None) -> StrengthResult:
        """
        Comprehensive password strength analysis.
        
        Args:
            password: The password to analyze
            user_inputs: Optional list of user-specific inputs (name, email, etc.)
                        to check against common patterns
        
        Returns:
            StrengthResult: Detailed analysis results
        """
        if not password:
            return StrengthResult(
                password="",
                score=0,
                shannon_entropy=0.0,
                crack_time_seconds=0.0,
                crack_time_display="Instant",
                feedback={"warning": "Password is empty", "suggestions": []},
            )
        
        # Calculate Shannon entropy
        shannon_entropy = self.calculate_shannon_entropy(password)
        
        # Use zxcvbn if available, otherwise use basic analysis
        if self.zxcvbn_available:
            result = self._analyze_with_zxcvbn(password, user_inputs)
        else:
            result = self._analyze_basic(password, shannon_entropy)
        
        # Add pattern analysis
        pattern_analysis = self.detect_patterns(password)
        result.pattern_analysis = pattern_analysis
        
        return result
    
    def _analyze_with_zxcvbn(
        self, password: str, user_inputs: Optional[list[str]] = None
    ) -> StrengthResult:
        """Analyze using zxcvbn library"""
        user_inputs = user_inputs or []
        zxcvbn_result = zxcvbn.zxcvbn(password, user_inputs=user_inputs)
        
        score = zxcvbn_result["score"]  # 0-4
        guesses = zxcvbn_result["guesses"]
        crack_time = zxcvbn_result["crack_times_seconds"]["offline_slow_hashing_1e4_per_second"]
        
        # Extract feedback
        feedback = {
            "warning": zxcvbn_result["feedback"].get("warning", ""),
            "suggestions": zxcvbn_result["feedback"].get("suggestions", []),
        }
        
        shannon_entropy = self.calculate_shannon_entropy(password)
        
        return StrengthResult(
            password=password,
            score=score,
            shannon_entropy=shannon_entropy,
            crack_time_seconds=crack_time,
            crack_time_display=self._format_crack_time(crack_time),
            feedback=feedback,
            guesses=guesses,
        )
    
    def _analyze_basic(self, password: str, shannon_entropy: float) -> StrengthResult:
        """Basic analysis without zxcvbn"""
        # Simple scoring based on length and entropy
        length = len(password)
        
        # Calculate basic score
        if length < 8 or shannon_entropy < 2.5:
            score = 0
        elif length < 10 or shannon_entropy < 3.0:
            score = 1
        elif length < 14 or shannon_entropy < 3.5:
            score = 2
        elif length < 18 or shannon_entropy < 4.0:
            score = 3
        else:
            score = 4
        
        # Estimate crack time based on charset and length
        crack_time = self._estimate_crack_time_basic(password)
        
        # Generate feedback
        feedback = self._generate_basic_feedback(password, score)
        
        return StrengthResult(
            password=password,
            score=score,
            shannon_entropy=shannon_entropy,
            crack_time_seconds=crack_time,
            crack_time_display=self._format_crack_time(crack_time),
            feedback=feedback,
        )
    
    def calculate_shannon_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy per character.
        
        Args:
            password: Password to analyze
            
        Returns:
            float: Entropy per character in bits
        """
        if not password:
            return 0.0
        
        char_counts = Counter(password)
        length = len(password)
        
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def calculate_charset_entropy(self, password: str) -> float:
        """
        Calculate theoretical entropy based on character set size.
        
        Returns:
            float: Total entropy in bits
        """
        charset_size = 0
        
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_symbol:
            charset_size += 32  # Approximate
        
        if charset_size == 0:
            return 0.0
        
        return len(password) * math.log2(charset_size)
    
    def _estimate_crack_time_basic(self, password: str) -> float:
        """
        Basic crack time estimation.
        Assumes 10,000 hashes/second (bcrypt-like speed)
        """
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(not c.isalnum() for c in password):
            charset_size += 32
        
        if charset_size == 0:
            charset_size = 26  # Minimum
        
        # Calculate total combinations
        total_combinations = charset_size ** len(password)
        
        # Average time to crack (half of search space)
        hashes_per_second = 10000  # Offline slow hashing
        seconds = (total_combinations / 2) / hashes_per_second
        
        return min(seconds, 1e100)  # Cap at reasonable max
    
    def _format_crack_time(self, seconds: float) -> str:
        """Format crack time"""
        if seconds < 1:
            return "Instant"
        elif seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours"
        elif seconds < 2592000:
            return f"{int(seconds / 86400)} days"
        elif seconds < 31536000:
            return f"{int(seconds / 2592000)} months"
        elif seconds < 1e10:
            years = int(seconds / 31536000)
            return f"{years:,} years"
        else:
            return "Centuries"
    
    def _generate_basic_feedback(self, password: str, score: int) -> Dict[str, Any]:
        """Generate basic feedback without zxcvbn"""
        suggestions = []
        warning = ""
        
        if score < 3:
            if len(password) < 12:
                suggestions.append("Use at least 12 characters")
            
            if not any(c.isupper() for c in password):
                suggestions.append("Add uppercase letters")
            
            if not any(c.islower() for c in password):
                suggestions.append("Add lowercase letters")
            
            if not any(c.isdigit() for c in password):
                suggestions.append("Add numbers")
            
            if not any(not c.isalnum() for c in password):
                suggestions.append("Add symbols")
            
            if score < 2:
                warning = "This password is too weak"
        
        return {
            "warning": warning,
            "suggestions": suggestions,
        }
    
    def detect_patterns(self, password: str) -> Dict[str, Any]:
        """Detect common patterns in password"""
        patterns = {
            "has_sequential": self._has_sequential_chars(password),
            "has_repeating": self._has_repeating_chars(password),
            "is_keyboard_pattern": self._is_keyboard_pattern(password),
            "char_frequency": self._get_char_frequency(password),
        }
        return patterns
    
    def _has_sequential_chars(self, password: str, min_length: int = 3) -> bool:
        """Check for sequential characters (abc, 123, etc.)"""
        for i in range(len(password) - min_length + 1):
            substring = password[i:i + min_length]
            if all(ord(substring[j]) == ord(substring[j-1]) + 1 for j in range(1, len(substring))):
                return True
        return False
    
    def _has_repeating_chars(self, password: str, min_length: int = 3) -> bool:
        """Check for repeating characters (aaa, 111, etc.)"""
        for i in range(len(password) - min_length + 1):
            substring = password[i:i + min_length]
            if len(set(substring)) == 1:
                return True
        return False
    
    def _is_keyboard_pattern(self, password: str) -> bool:
        """Check for common keyboard patterns"""
        keyboard_patterns = [
            "qwerty", "asdfgh", "zxcvbn", "12345", "qazwsx",
            "!@#$%", "abcdef", "password", "admin"
        ]
        lower_pass = password.lower()
        return any(pattern in lower_pass for pattern in keyboard_patterns)
    
    def _get_char_frequency(self, password: str) -> Dict[str, int]:
        """Get character type frequency"""
        return {
            "uppercase": sum(1 for c in password if c.isupper()),
            "lowercase": sum(1 for c in password if c.islower()),
            "digits": sum(1 for c in password if c.isdigit()),
            "symbols": sum(1 for c in password if not c.isalnum()),
        }


if __name__ == "__main__":
    # Demo usage
    analyzer = PasswordStrengthAnalyzer()
    
    test_passwords = [
        "password",
        "P@ssw0rd",
        "MyP@ssw0rd123",
        "correct horse battery staple",
        "X9#mK$2vL@pQ7nR",
        "Tr0ub4dor&3",
    ]
    
    print("QuantumLock Password Strength Analyzer Demo\n")
    print("=" * 70)
    
    for pwd in test_passwords:
        result = analyzer.analyze(pwd)
        print(f"\nPassword: {pwd}")
        print(f"Score: {result.score}/4 ({result.get_score_label()})")
        print(f"Shannon Entropy: {result.shannon_entropy:.2f} bits/char")
        print(f"Crack Time: {result.crack_time_display}")
        
        if result.feedback["warning"]:
            print(f"Warning: {result.feedback['warning']}")
        
        if result.feedback["suggestions"]:
            print("Suggestions:")
            for suggestion in result.feedback["suggestions"]:
                print(f"  - {suggestion}")
        
        print("-" * 70)
