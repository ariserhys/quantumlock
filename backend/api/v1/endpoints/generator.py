"""
Password & Passphrase Generation Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

from backend.core import (
    PasswordGenerator,
    PasswordConfig,
    PassphraseGenerator,
    PassphraseConfig,
)

router = APIRouter()


# Request/Response Models
class PasswordGenerateRequest(BaseModel):
    """Request model for password generation"""
    length: int = Field(default=16, ge=4, le=128, description="Password length")
    use_uppercase: bool = Field(default=True, description="Include uppercase letters")
    use_lowercase: bool = Field(default=True, description="Include lowercase letters")
    use_digits: bool = Field(default=True, description="Include numbers")
    use_symbols: bool = Field(default=True, description="Include symbols")
    custom_symbols: Optional[str] = Field(default=None, description="Custom symbol set")
    exclude_chars: Optional[str] = Field(default=None, description="Characters to exclude")
    no_repeating: bool = Field(default=False, description="No repeating characters")
    min_uppercase: int = Field(default=0, ge=0, description="Minimum uppercase letters")
    min_lowercase: int = Field(default=0, ge=0, description="Minimum lowercase letters")
    min_digits: int = Field(default=0, ge=0, description="Minimum digits")
    min_symbols: int = Field(default=0, ge=0, description="Minimum symbols")


class PasswordGenerateResponse(BaseModel):
    """Response model for password generation"""
    password: str
    length: int
    entropy_bits: float
    charset_size: int


class PassphraseGenerateRequest(BaseModel):
    """Request model for passphrase generation"""
    word_count: int = Field(default=6, ge=3, le=20, description="Number of words")
    wordlist_type: Literal["diceware", "bip39"] = Field(default="diceware")
    separator: str = Field(default=" ", max_length=5, description="Word separator")
    capitalize_words: bool = Field(default=False, description="Capitalize words")
    add_number: bool = Field(default=False, description="Add number at end")
    add_symbol: bool = Field(default=False, description="Add symbol at end")


class PassphraseGenerateResponse(BaseModel):
    """Response model for passphrase generation"""
    passphrase: str
    word_count: int
    entropy_bits: float
    wordlist_type: str


# Endpoints
@router.post("/generate/password", response_model=PasswordGenerateResponse)
async def generate_password(request: PasswordGenerateRequest):
    """
    Generate a cryptographically secure password.
    
    Uses Python's `secrets` module (CSPRNG) for true randomness.
    
    **Example:**
    ```json
    {
      "length": 20,
      "use_symbols": true,
      "min_uppercase": 2,
      "min_digits": 2
    }
    ```
    """
    try:
        config = PasswordConfig(
            length=request.length,
            use_uppercase=request.use_uppercase,
            use_lowercase=request.use_lowercase,
            use_digits=request.use_digits,
            use_symbols=request.use_symbols,
            custom_symbols=request.custom_symbols,
            exclude_chars=request.exclude_chars,
            no_repeating=request.no_repeating,
            min_uppercase=request.min_uppercase,
            min_lowercase=request.min_lowercase,
            min_digits=request.min_digits,
            min_symbols=request.min_symbols,
        )
        
        generator = PasswordGenerator(config)
        password = generator.generate()
        
        return PasswordGenerateResponse(
            password=password,
            length=len(password),
            entropy_bits=generator.calculate_entropy(password),
            charset_size=len(config.get_character_set()),
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating password: {str(e)}")


@router.post("/generate/passphrase", response_model=PassphraseGenerateResponse)
async def generate_passphrase(request: PassphraseGenerateRequest):
    """
    Generate a memorable passphrase.
    
    **Wordlists:**
    - **Diceware**: 7776 words (~12.9 bits/word)
    - **BIP39**: 2048 words (~11 bits/word)
    
    **Example:**
    ```json
    {
      "word_count": 6,
      "wordlist_type": "diceware",
      "separator": "-",
      "capitalize_words": true
    }
    ```
    """
    try:
        config = PassphraseConfig(
            word_count=request.word_count,
            wordlist_type=request.wordlist_type,
            separator=request.separator,
            capitalize_words=request.capitalize_words,
            add_number=request.add_number,
            add_symbol=request.add_symbol,
        )
        
        generator = PassphraseGenerator(config)
        passphrase = generator.generate()
        
        return PassphraseGenerateResponse(
            passphrase=passphrase,
            word_count=config.word_count,
            entropy_bits=generator.calculate_entropy(),
            wordlist_type=config.wordlist_type,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating passphrase: {str(e)}")


@router.get("/generate/password/quick")
async def generate_password_quick(
    length: int = 16,
    symbols: bool = True,
):
    """
    Quick password generation with minimal parameters.
    
    **Example:** `/api/v1/generate/password/quick?length=20&symbols=true`
    """
    try:
        config = PasswordConfig(
            length=length,
            use_symbols=symbols,
        )
        generator = PasswordGenerator(config)
        password = generator.generate()
        
        return {
            "password": password,
            "length": len(password),
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/generate/passphrase/quick")
async def generate_passphrase_quick(
    words: int = 6,
    wordlist: Literal["diceware", "bip39"] = "diceware",
):
    """
    Quick passphrase generation.
    
    **Example:** `/api/v1/generate/passphrase/quick?words=8&wordlist=diceware`
    """
    try:
        config = PassphraseConfig(
            word_count=words,
            wordlist_type=wordlist,
        )
        generator = PassphraseGenerator(config)
        passphrase = generator.generate()
        
        return {
            "passphrase": passphrase,
            "word_count": words,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
