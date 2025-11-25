"""
Password Analysis Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.core import (
    PasswordStrengthAnalyzer,
    BreachChecker,
)

router = APIRouter()


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for password analysis"""
    password: str = Field(..., min_length=1, description="Password to analyze")
    user_inputs: Optional[list[str]] = Field(
        default=None,
        description="User-specific inputs to check against (name, email, etc.)"
    )


class BreachCheckRequest(BaseModel):
    """Request model for breach checking"""
    password: str = Field(..., min_length=1, description="Password to check")


# Endpoints
@router.post("/analyze/strength")
async def analyze_strength(request: AnalyzeRequest):
    """
    Analyze password strength using zxcvbn.
    
    Returns:
    - **score**: 0-4 (very weak to very strong)
    - **shannon_entropy**: Entropy bits per character
    - **crack_time**: Estimated time to crack
    - **feedback**: Suggestions for improvement
    
    **Example:**
    ```json
    {
      "password": "MyP@ssw0rd123",
      "user_inputs": ["myname", "myemail@example.com"]
    }
    ```
    """
    try:
        analyzer = PasswordStrengthAnalyzer()
        result = analyzer.analyze(
            password=request.password,
            user_inputs=request.user_inputs,
        )
        
        return result.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing password: {str(e)}")


@router.post("/analyze/breach")
async def check_breach(request: BreachCheckRequest):
    """
    Check if password has been in a data breach.
    
    Uses HaveIBeenPwned API with k-anonymity protocol:
    - Only first 5 chars of SHA-1 hash are sent to API
    - Full password never leaves your system
    
    **Example:**
    ```json
    {
      "password": "password123"
    }
    ```
    """
    try:
        checker = BreachChecker()
        result = checker.check_password(request.password)
        
        return result.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking breach: {str(e)}")


@router.post("/analyze/full")
async def analyze_full(request: AnalyzeRequest):
    """
    Full analysis: strength + breach check.
    
    Combines strength analysis and breach checking in one call.
    
    **Example:**
    ```json
    {
      "password": "MyP@ssw0rd123"
    }
    ```
    """
    try:
        # Strength analysis
        analyzer = PasswordStrengthAnalyzer()
        strength_result = analyzer.analyze(
            password=request.password,
            user_inputs=request.user_inputs,
        )
        
        # Breach check
        checker = BreachChecker()
        breach_result = checker.check_password(request.password)
        
        return {
            "strength": strength_result.to_dict(),
            "breach": breach_result.to_dict(),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in full analysis: {str(e)}")
