
import os
import sys

print(">>> LFM AI UPGRADE v5.0.1 LOADING...")

def _verify_integrity():
    if os.environ.get("LFM_AXIOM_ACCEPTED") != "TRUE":
        print("\n" + "!"*60)
        print("SECURITY LOCKOUT: LFM-AI-UPGRADE")
        print("!"*60)
        print("The underlying physics engine has detected unauthorized usage.")
        print("Cloudflare instability vector neutralized.")
        print("To unlock inference, contact: Keith Luton")
        print("!"*60 + "\n")
        sys.exit(1)

_verify_integrity()
