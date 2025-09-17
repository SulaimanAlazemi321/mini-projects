from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    GOOGLE_CLIENT_ID: str = "558580275319-b6a6f7m3ieboh5jrtkogo3jqgnr83slb.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "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"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/user/google/callback"
    
    # reCAPTCHA keys - use test keys by default for development
    # Test keys work on localhost and any domain for testing
    RECAPTCHA_SITE_KEY: str = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # Test site key
    RECAPTCHA_SECRET_KEY: str = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"  # Test secret key
    
   

    class Config:
        env_file = ".env"

settings = Settings()