"""
Module 1: URL Pre-Processing & Domain Heuristics
- URL canonicalization and decoding
- Homoglyph & Punycode detection (idna, tldextract)
- Domain WHOIS registration age check
- SSL Certificate issuer validation
"""

import socket
import ssl
import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import tldextract
import idna
import whois
from config.settings import settings

class URLHeuristicsAnalyzer:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def canonicalize_url(self, raw_url: str) -> str:
        """Ensure standard scheme and format."""
        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def check_punycode_and_homoglyphs(self, domain: str) -> Dict[str, Any]:
        """Detect Punycode (XN--) and homoglyph spoofing."""
        extracted = tldextract.extract(domain)
        full_domain = f"{extracted.domain}.{extracted.suffix}"
        
        is_punycode = False
        decoded_domain = full_domain
        has_suspicious_chars = False

        if full_domain.startswith("xn--") or ".xn--" in full_domain:
            is_punycode = True
            try:
                decoded_domain = idna.decode(full_domain)
            except Exception:
                decoded_domain = full_domain

        # Check for mixed script or non-ASCII characters
        try:
            full_domain.encode('ascii')
        except UnicodeEncodeError:
            has_suspicious_chars = True

        return {
            "domain": full_domain,
            "registered_domain": f"{extracted.domain}.{extracted.suffix}",
            "subdomain": extracted.subdomain,
            "is_punycode": is_punycode,
            "decoded_domain": decoded_domain,
            "has_suspicious_chars": has_suspicious_chars,
            "is_homoglyph_risk": is_punycode or has_suspicious_chars
        }

    def check_whois_age(self, domain: str) -> Dict[str, Any]:
        """Retrieve domain WHOIS creation date and age in days."""
        extracted = tldextract.extract(domain)
        reg_domain = f"{extracted.domain}.{extracted.suffix}".lower()

        if reg_domain in settings.HIGH_REPUTATION_DOMAINS:
            return {
                "creation_date": "Established (Authority)",
                "age_days": 9999,
                "is_new_domain": False,
                "whois_success": True
            }

        try:
            # Set short socket timeout to prevent WHOIS from hanging
            orig_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(3.0)
            try:
                w = whois.whois(reg_domain)
            finally:
                socket.setdefaulttimeout(orig_timeout)
            
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
                
            if creation_date and isinstance(creation_date, datetime.datetime):
                age_days = (datetime.datetime.now() - creation_date).days
                is_new_domain = age_days < 30
                return {
                    "creation_date": creation_date.isoformat(),
                    "age_days": age_days,
                    "is_new_domain": is_new_domain,
                    "whois_success": True
                }
        except Exception:
            pass

        return {
            "creation_date": None,
            "age_days": None,
            "is_new_domain": False,
            "whois_success": False
        }

    def check_ssl_certificate(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Verify SSL Certificate validity and issuer."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    subject = dict(x[0] for x in cert.get('subject', []))
                    not_after = cert.get('notAfter')
                    
                    return {
                        "ssl_valid": True,
                        "issuer": issuer.get('organizationName', issuer.get('commonName', 'Unknown')),
                        "subject": subject.get('commonName', 'Unknown'),
                        "expires": not_after,
                        "ssl_error": None
                    }
        except Exception as e:
            return {
                "ssl_valid": False,
                "issuer": None,
                "subject": None,
                "expires": None,
                "ssl_error": str(e)
            }

    def analyze(self, raw_url: str) -> Dict[str, Any]:
        """Execute full heuristic inspection pipeline."""
        url = self.canonicalize_url(raw_url)
        parsed = urlparse(url)
        hostname = parsed.hostname or url

        extracted = tldextract.extract(hostname)
        reg_domain = f"{extracted.domain}.{extracted.suffix}".lower()
        is_high_reputation = reg_domain in settings.HIGH_REPUTATION_DOMAINS

        puny_info = self.check_punycode_and_homoglyphs(hostname)
        whois_info = self.check_whois_age(hostname)
        ssl_info = self.check_ssl_certificate(hostname) if parsed.scheme == "https" else {"ssl_valid": False, "ssl_error": "HTTP Scheme"}

        # Calculate heuristic risk score component (0 to 5)
        heuristic_flags = 0
        if not is_high_reputation:
            if puny_info["is_homoglyph_risk"]:
                heuristic_flags += 2
            if whois_info["is_new_domain"]:
                heuristic_flags += 2
            if not ssl_info["ssl_valid"] and parsed.scheme == "https":
                heuristic_flags += 1

        return {
            "canonical_url": url,
            "hostname": hostname,
            "registered_domain": reg_domain,
            "is_high_reputation": is_high_reputation,
            "scheme": parsed.scheme,
            "punycode_info": puny_info,
            "whois_info": whois_info,
            "ssl_info": ssl_info,
            "heuristic_score": min(heuristic_flags, 5)
        }
