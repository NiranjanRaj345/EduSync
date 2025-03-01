#!/usr/bin/env python3
import base64
import sys

def encode_file(filename):
    """Encode a file to base64."""
    try:
        with open(filename, 'rb') as f:
            encoded = base64.b64encode(f.read())
            print(f"\nBase64 encoded string for {filename}:")
            print(encoded.decode('utf-8'))
            print("\nAdd this to your Koyeb environment variables as GOOGLE_DRIVE_CREDENTIALS_B64")
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error encoding file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 encode_credentials.py service-account.json")
        sys.exit(1)
    
    encode_file(sys.argv[1])
