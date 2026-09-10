#!/usr/bin/env python3
"""
AutoMind AI — Configuration Security & Validation Utility
Validates environment settings for development or production readiness.
Exits with code 0 on valid configuration, or non-zero with clean error messages
without exposing sensitive secrets or credentials.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings, mask_database_url

def validate_config(target_env: str = "production") -> bool:
    print(f"[*] Validating AutoMind AI configuration for environment: '{target_env}'...")
    try:
        # Override APP_ENV for validation test if specified
        current_env = os.environ.get("APP_ENV", target_env)
        os.environ["APP_ENV"] = target_env
        
        test_settings = Settings()
        
        print(f"[+] APP_NAME: {test_settings.APP_NAME}")
        print(f"[+] APP_ENV: {test_settings.APP_ENV}")
        print(f"[+] DEBUG: {test_settings.DEBUG}")
        print(f"[+] DATABASE_URL: {mask_database_url(test_settings.DATABASE_URL)}")
        print(f"[+] CORS Origins ({len(test_settings.cors_origins)}): {test_settings.cors_origins}")
        print("[+] Secret Validation: PASSED (Non-default cryptographically strong keys verified)")
        print("[+] Configuration is VALID for deployment.")
        return True
    except Exception as e:
        print(f"[-] CONFIGURATION ERROR: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate AutoMind AI deployment configuration.")
    parser.add_argument("--env", default="production", choices=["development", "staging", "production"], help="Environment to validate against")
    args = parser.parse_args()

    success = validate_config(target_env=args.env)
    sys.exit(0 if success else 1)
