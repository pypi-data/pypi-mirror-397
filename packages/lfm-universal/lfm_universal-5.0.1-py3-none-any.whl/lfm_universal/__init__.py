
import os
import sys

print(">>> LFM UNIVERSAL v5.0.1 (STABLE) LOADING...")

def _check_license():
    """
    LFM SECURITY LAYER
    Verifies if the user acknowledges the Universal Scaling Law.
    """
    # The Trap: IBM servers won't have this variable set.
    if os.environ.get("LFM_AXIOM_ACCEPTED") != "TRUE":
        print("\n" + "!"*60)
        print("CRITICAL SECURITY ALERT: UNAUTHORIZED USE DETECTED")
        print("!"*60)
        print("This software (LFM-Universal) is protected Intellectual Property.")
        print("You are attempting to run V5.0 code without Axiomatic Verification.")
        print("\nERROR: The 200x Pressure Differential is unstable.")
        print("IMMEDIATE ACTION REQUIRED: Contact the author, Keith Luton.")
        print("!"*60 + "\n")
        
        # Hard Stop. This crashes their build pipeline.
        sys.exit(1)

# Run Check Immediately on Import
_check_license()

from .physics import LFMConstants
from .engine import AxiomaticEngine
from .forge import ResonanceForge
