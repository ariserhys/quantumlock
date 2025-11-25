"""
TOTP (Time-based One-Time Password) Generator

Generates 2FA codes compatible with Google Authenticator, Authy, etc.
"""

import pyotp
import qrcode
import io
import base64
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class TOTPSecret:
    """TOTP secret configuration"""
    secret: str
    issuer: str
    account_name: str
    uri: str
    
    def to_dict(self):
        return {
            "secret": self.secret,
            "issuer": self.issuer,
            "account_name": self.account_name,
            "uri": self.uri,
        }


class TOTPGenerator:
    """Generate and verify TOTP codes"""
    
    def __init__(self, digits: int = 6, interval: int = 30):
        """
        Initialize TOTP generator.
        
        Args:
            digits: Number of digits in code (6 or 8)
            interval: Time interval in seconds (usually 30)
        """
        self.digits = digits
        self.interval = interval
    
    def generate_secret(
        self,
        issuer: str,
        account_name: str,
    ) -> TOTPSecret:
        """
        Generate a new TOTP secret.
        
        Args:
            issuer: Service name (e.g., "GitHub")
            account_name: User's account name/email
            
        Returns:
            TOTPSecret: Secret configuration
        """
        # Generate random base32 secret
        secret = pyotp.random_base32()
        
        # Create TOTP URI for QR code
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.interval)
        uri = totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )
        
        return TOTPSecret(
            secret=secret,
            issuer=issuer,
            account_name=account_name,
            uri=uri,
        )
    
    def get_current_code(self, secret: str) -> str:
        """
        Get current TOTP code.
        
        Args:
            secret: Base32-encoded secret
            
        Returns:
            str: Current TOTP code
        """
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.interval)
        return totp.now()
    
    def verify_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify a TOTP code.
        
        Args:
            secret: Base32-encoded secret
            code: Code to verify
            valid_window: Number of intervals to check (1 = ±30s)
            
        Returns:
            bool: True if code is valid
        """
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.interval)
        return totp.verify(code, valid_window=valid_window)
    
    def generate_qr_code(
        self,
        totp_secret: TOTPSecret,
        size: int = 300,
    ) -> bytes:
        """
        Generate QR code image for TOTP secret.
        
        Args:
            totp_secret: TOTP secret configuration
            size: QR code size in pixels
            
        Returns:
            bytes: PNG image data
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_secret.uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def generate_qr_code_base64(
        self,
        totp_secret: TOTPSecret,
        size: int = 300,
    ) -> str:
        """
        Generate QR code as base64 string.
        
        Args:
            totp_secret: TOTP secret configuration
            size: QR code size in pixels
            
        Returns:
            str: Base64-encoded PNG image
        """
        png_data = self.generate_qr_code(totp_secret, size)
        return base64.b64encode(png_data).decode('utf-8')
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Generate backup codes for account recovery.
        
        Args:
            count: Number of backup codes to generate
            
        Returns:
            list: Backup codes (8 characters each)
        """
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(8)
            )
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        
        return codes
    
    def parse_uri(self, uri: str) -> Optional[TOTPSecret]:
        """
        Parse a TOTP URI (otpauth://totp/...)
        
        Args:
            uri: TOTP URI string
            
        Returns:
            TOTPSecret or None if invalid
        """
        try:
            if not uri.startswith("otpauth://totp/"):
                return None
            
            # Extract components
            from urllib.parse import urlparse, parse_qs
            
            parsed = urlparse(uri)
            account_info = parsed.path.lstrip('/')
            params = parse_qs(parsed.query)
            
            # Extract issuer and account name
            if ':' in account_info:
                issuer, account_name = account_info.split(':', 1)
            else:
                issuer = params.get('issuer', [''])[0]
                account_name = account_info
            
            secret = params.get('secret', [''])[0]
            
            if not secret:
                return None
            
            return TOTPSecret(
                secret=secret,
                issuer=issuer,
                account_name=account_name,
                uri=uri,
            )
        except Exception:
            return None


def generate_totp_secret(issuer: str, account_name: str) -> TOTPSecret:
    """
    Quick helper to generate TOTP secret.
    
    Args:
        issuer: Service name
        account_name: User account
        
    Returns:
        TOTPSecret: Generated secret
    """
    generator = TOTPGenerator()
    return generator.generate_secret(issuer, account_name)


if __name__ == "__main__":
    # Demo usage
    print("QuantumLock TOTP Generator Demo\n")
    print("=" * 70)
    
    generator = TOTPGenerator()
    
    # Generate new secret
    print("\n1. Generating new TOTP secret for GitHub...")
    secret = generator.generate_secret("GitHub", "user@example.com")
    
    print(f"   Secret: {secret.secret}")
    print(f"   Issuer: {secret.issuer}")
    print(f"   Account: {secret.account_name}")
    print(f"   URI: {secret.uri}")
    
    # Get current code
    print(f"\n2. Current TOTP code:")
    code = generator.get_current_code(secret.secret)
    print(f"   Code: {code}")
    
    # Verify code
    print(f"\n3. Verifying code...")
    is_valid = generator.verify_code(secret.secret, code)
    print(f"   Valid: {is_valid}")
    
    # Verify wrong code
    wrong_code = "000000"
    is_valid = generator.verify_code(secret.secret, wrong_code)
    print(f"   Wrong code ({wrong_code}) valid: {is_valid}")
    
    # Generate backup codes
    print(f"\n4. Generating backup codes...")
    backup_codes = generator.generate_backup_codes(5)
    for i, code in enumerate(backup_codes, 1):
        print(f"   {i}. {code}")
    
    # QR code
    print(f"\n5. QR Code generated (base64)")
    qr_base64 = generator.generate_qr_code_base64(secret)
    print(f"   Length: {len(qr_base64)} characters")
    print(f"   First 50 chars: {qr_base64[:50]}...")
    
    print("\n" + "=" * 70)
    print("Scan the QR code with Google Authenticator or Authy to test!")
