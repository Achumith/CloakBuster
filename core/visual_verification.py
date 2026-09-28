"""
Module 8: Visual Verification via Perceptual Hashing (pHash)
Computes Perceptual Hash (pHash) of page screenshots and evaluates Hamming distance
against reference target signatures (Google, Microsoft, PayPal, Netflix).
"""

import io
from typing import Dict, Any, Optional
from PIL import Image
import imagehash
from config.settings import settings

class VisualTwinClassifier:
    def __init__(self):
        # Reference pHash signatures for target login portals (Sample 64-bit Hex Hashes)
        self.known_targets = {
            "Google Login": {
                "phash": "a1b2c3d4e5f60718",
                "legitimate_domains": ["accounts.google.com", "google.com"]
            },
            "Microsoft 365": {
                "phash": "f0e1d2c3b4a59687",
                "legitimate_domains": ["login.microsoftonline.com", "live.com", "microsoft.com"]
            },
            "PayPal Portal": {
                "phash": "1234567890abcdef",
                "legitimate_domains": ["paypal.com", "www.paypal.com"]
            }
        }

    def compute_phash_from_bytes(self, image_bytes: bytes) -> Optional[imagehash.ImageHash]:
        """Convert PNG image bytes to PIL Image and compute pHash."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return imagehash.phash(image)
        except Exception:
            return None

    def evaluate_visual_impersonation(self, screenshot_bytes: Optional[bytes], current_domain: str) -> Dict[str, Any]:
        """Check for visual similarity match against target vector signatures."""
        if not screenshot_bytes:
            return {
                "phash_computed": None,
                "is_visual_impersonation": False,
                "matched_brand": None,
                "hamming_distance": None
            }

        phash_val = self.compute_phash_from_bytes(screenshot_bytes)
        if not phash_val:
            return {
                "phash_computed": None,
                "is_visual_impersonation": False,
                "matched_brand": None,
                "hamming_distance": None
            }

        phash_str = str(phash_val)

        for brand_name, info in self.known_targets.items():
            target_hash = imagehash.hex_to_hash(info["phash"])
            distance = phash_val - target_hash  # Hamming distance

            # If visually similar (distance <= threshold)
            if distance <= settings.PHASH_HAMMING_THRESHOLD:
                # Check if current domain is legitimate
                is_legit = any(legit in current_domain.lower() for legit in info["legitimate_domains"])
                if not is_legit:
                    return {
                        "phash_computed": phash_str,
                        "is_visual_impersonation": True,
                        "matched_brand": brand_name,
                        "hamming_distance": int(distance),
                        "alert": f"CRITICAL: Visual twin match ({distance} Hamming distance) for {brand_name} on unauthorized domain '{current_domain}'!"
                    }

        return {
            "phash_computed": phash_str,
            "is_visual_impersonation": False,
            "matched_brand": None,
            "hamming_distance": None
        }
