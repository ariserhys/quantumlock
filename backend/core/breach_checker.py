"""
HaveIBeenPwned API Integration

Checks passwords against breach database using k-anonymity protocol.
Only sends first 5 characters of SHA-1 hash for privacy.
"""

import hashlib
import time
from typing import Optional, Tuple
import requests
from dataclasses import dataclass


@dataclass
class BreachResult:
    """Result of breach check"""
    is_breached: bool
    breach_count: int  # Number of times password appeared in breaches
    message: str
    
    def to_dict(self):
        return {
            "is_breached": self.is_breached,
            "breach_count": self.breach_count,
            "message": self.message,
        }


class BreachChecker:
    """Check passwords against HaveIBeenPwned database"""
    
    API_URL = "https://api.pwnedpasswords.com/range/"
    USER_AGENT = "QuantumLock-Password-Manager/1.0"
    
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        use_padding: bool = True,
    ):
        """
        Initialize breach checker.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts on rate limiting
            use_padding: Add padding to response for additional security
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_padding = use_padding
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
        })
        
        if self.use_padding:
            self.session.headers.update({
                "Add-Padding": "true",
            })
    
    def check_password(self, password: str) -> BreachResult:
        """
        Check if password has been breached using k-anonymity.
        
        The k-anonymity protocol:
        1. Hash password with SHA-1
        2. Send only first 5 characters of hash to API
        3. API returns all hash suffixes matching the prefix
        4. Check locally if full hash is in results
        
        Args:
            password: Password to check (never sent to API)
            
        Returns:
            BreachResult: Result of breach check
        """
        if not password:
            return BreachResult(
                is_breached=False,
                breach_count=0,
                message="Empty password"
            )
        
        # Hash password with SHA-1
        password_hash = self._hash_password(password)
        
        # Split into prefix (first 5 chars) and suffix
        prefix = password_hash[:5]
        suffix = password_hash[5:]
        
        # Query API with prefix only
        try:
            hashes = self._query_api(prefix)
        except Exception as e:
            return BreachResult(
                is_breached=False,
                breach_count=0,
                message=f"Error checking breach: {str(e)}"
            )
        
        # Check if our suffix is in the results
        breach_count = hashes.get(suffix, 0)
        
        if breach_count > 0:
            return BreachResult(
                is_breached=True,
                breach_count=breach_count,
                message=f"This password has been seen {breach_count:,} times in data breaches"
            )
        else:
            return BreachResult(
                is_breached=False,
                breach_count=0,
                message="Good news! This password has not been found in any known breaches"
            )
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password with SHA-1.
        
        Note: SHA-1 is used for breach checking, NOT for password storage.
        This is the standard required by HaveIBeenPwned API.
        
        Args:
            password: Password to hash
            
        Returns:
            str: Uppercase SHA-1 hex digest
        """
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        return sha1_hash.upper()
    
    def _query_api(self, prefix: str) -> dict[str, int]:
        """
        Query HaveIBeenPwned API with hash prefix.
        
        Args:
            prefix: First 5 characters of SHA-1 hash
            
        Returns:
            dict: Mapping of hash suffixes to breach counts
            
        Raises:
            requests.RequestException: On API errors
        """
        url = f"{self.API_URL}{prefix}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise requests.RequestException(
                            f"Rate limited. Retry after {retry_after} seconds"
                        )
                
                response.raise_for_status()
                
                # Parse response
                return self._parse_response(response.text)
                
            except requests.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise requests.RequestException("Request timed out")
            
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise
        
        raise requests.RequestException("Max retries exceeded")
    
    def _parse_response(self, response_text: str) -> dict[str, int]:
        """
        Parse API response into dict.
        
        Response format:
        SUFFIX1:COUNT1
        SUFFIX2:COUNT2
        ...
        
        Args:
            response_text: Raw API response
            
        Returns:
            dict: Hash suffix -> breach count mapping
        """
        hashes = {}
        
        for line in response_text.strip().split('\n'):
            if ':' in line:
                suffix, count = line.split(':', 1)
                hashes[suffix.strip()] = int(count.strip())
        
        return hashes
    
    def check_multiple(self, passwords: list[str]) -> dict[str, BreachResult]:
        """
        Check multiple passwords for breaches.
        
        Args:
            passwords: List of passwords to check
            
        Returns:
            dict: Password -> BreachResult mapping
        """
        results = {}
        
        for password in passwords:
            # Be respectful to API - small delay between requests
            if results:
                time.sleep(0.1)
            
            results[password] = self.check_password(password)
        
        return results


def check_breach(password: str) -> BreachResult:
    """
    Quick helper function to check a password.
    
    Args:
        password: Password to check
        
    Returns:
        BreachResult: Check result
    """
    checker = BreachChecker()
    return checker.check_password(password)


if __name__ == "__main__":
    # Demo usage
    print("QuantumLock Breach Checker Demo\n")
    print("Using HaveIBeenPwned API with k-anonymity protocol")
    print("Only first 5 characters of SHA-1 hash are sent to API\n")
    print("=" * 70)
    
    test_passwords = [
        "password",  # Very common, will be breached
        "P@ssw0rd123",  # Common variant
        "X9#mK$2vL@pQ7nR",  # Strong random, likely not breached
    ]
    
    checker = BreachChecker()
    
    for pwd in test_passwords:
        print(f"\nChecking: {pwd}")
        print("-" * 70)
        
        # Show the hash (for educational purposes)
        pwd_hash = checker._hash_password(pwd)
        print(f"SHA-1 Hash: {pwd_hash}")
        print(f"Prefix sent to API: {pwd_hash[:5]}")
        print(f"Suffix checked locally: {pwd_hash[5:]}")
        
        # Check breach
        result = checker.check_password(pwd)
        
        print(f"\n{result.message}")
        if result.is_breached:
            print(f"⚠️  WARNING: This password is NOT SAFE to use!")
        else:
            print(f"✓ This password has not been found in known breaches")
        
        print("=" * 70)
