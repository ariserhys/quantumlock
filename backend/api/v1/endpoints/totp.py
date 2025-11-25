"""
TOTP/2FA Endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional

from backend.features import TOTPGenerator

router = APIRouter()


# Request/Response Models
class TOTPGenerateRequest(BaseModel):
    """Request model for TOTP secret generation"""
    issuer: str = Field(..., description="Service name (e.g., GitHub)")
    account_name: str = Field(..., description="User's account/email")


class TOTPVerifyRequest(BaseModel):
    """Request model for TOTP code verification"""
    secret: str = Field(..., description="Base32-encoded secret")
    code: str = Field(..., min_length=6, max_length=8, description="TOTP code to verify")


class BackupCodesRequest(BaseModel):
    """Request model for backup codes generation"""
    count: int = Field(default=10, ge=5, le=20, description="Number of backup codes")


# Endpoints
@router.post("/generate")
async def generate_totp_secret(request: TOTPGenerateRequest):
    """
    Generate a new TOTP secret.
    
    Returns secret, QR code URI, and QR code image (base64).
    
    **Example:**
    ```json
    {
      "issuer": "GitHub",
      "account_name": "user@example.com"
    }
    ```
    """
    try:
        generator = TOTPGenerator()
        secret = generator.generate_secret(
            issuer=request.issuer,
            account_name=request.account_name,
        )
        
        # Generate QR code as base64
        qr_base64 = generator.generate_qr_code_base64(secret)
        
        return {
            **secret.to_dict(),
            "qr_code_base64": qr_base64,
            "qr_code_data_uri": f"data:image/png;base64,{qr_base64}",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating TOTP: {str(e)}")


@router.get("/current/{secret}")
async def get_current_code(secret: str):
    """
    Get current TOTP code for a secret.
    
    **Example:** `/api/v1/totp/current/JBSWY3DPEHPK3PXP`
    """
    try:
        generator = TOTPGenerator()
        code = generator.get_current_code(secret)
        
        return {
            "code": code,
            "valid_for_seconds": 30,  # Standard TOTP interval
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting code: {str(e)}")


@router.post("/verify")
async def verify_code(request: TOTPVerifyRequest):
    """
    Verify a TOTP code.
    
    **Example:**
    ```json
    {
      "secret": "JBSWY3DPEHPK3PXP",
      "code": "123456"
    }
    ```
    """
    try:
        generator = TOTPGenerator()
        is_valid = generator.verify_code(
            secret=request.secret,
            code=request.code,
        )
        
        return {
            "valid": is_valid,
            "message": "Code is valid" if is_valid else "Code is invalid or expired",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying code: {str(e)}")


@router.post("/backup-codes")
async def generate_backup_codes(request: BackupCodesRequest):
    """
    Generate backup codes for account recovery.
    
    **Example:**
    ```json
    {
      "count": 10
    }
    ```
    """
    try:
        generator = TOTPGenerator()
        codes = generator.generate_backup_codes(count=request.count)
        
        return {
            "backup_codes": codes,
            "count": len(codes),
            "message": "Store these backup codes securely. Each can only be used once.",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating backup codes: {str(e)}")


@router.get("/qr/{secret}")
async def get_qr_code(
    secret: str,
    issuer: str = "QuantumLock",
    account: str = "user@example.com"
):
    """
    Get QR code image for a TOTP secret.
    
    Returns PNG image directly.
    
    **Example:** `/api/v1/totp/qr/JBSWY3DPEHPK3PXP?issuer=GitHub&account=user@example.com`
    """
    try:
        from backend.features import TOTPSecret
        
        generator = TOTPGenerator()
        
        # Create TOTP secret object
        totp_secret = TOTPSecret(
            secret=secret,
            issuer=issuer,
            account_name=account,
            uri=f"otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}"
        )
        
        # Generate QR code
        qr_png = generator.generate_qr_code(totp_secret)
        
        return Response(content=qr_png, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")
