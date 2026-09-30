"""
CloakBuster Configuration and Risk Scoring Parameters
"""
import os

class Settings:
    # Server configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    MOCK_SERVER_PORT: int = 5000
    
    # Timeout Settings (seconds)
    HTTP_TIMEOUT: float = 10.0
    PLAYWRIGHT_TIMEOUT: float = 15.0
    
    # Risk Score Weights & Coefficients
    WEIGHT_STATUS_DIVERGENCE: float = 30.0   # Delta S weight (when cloaking credentials)
    WEIGHT_DOM_RATIO: float = 3.0           # R_DOM multiplier
    MAX_DOM_RATIO_CAP: float = 10.0         # Max cap for DOM ratio
    WEIGHT_FORM_DIVERGENCE: float = 15.0    # Delta F multiplier per missing sensitive input
    MAX_FORM_DIVERGENCE_CAP: float = 2.0    # Max cap for form divergence count
    WEIGHT_BEHAVIORAL_TRAP: float = 20.0    # S_trap weight for back button trap
    WEIGHT_HEURISTICS: float = 5.0          # S_heuristics weight per domain anomaly
    WEIGHT_EXFILTRATION: float = 15.0       # Score penalty for 3rd party exfiltration
    WEIGHT_PHASH_MATCH: float = 25.0        # Score penalty for high-fidelity visual impersonation
    
    # Visual Twin / pHash Settings
    PHASH_HAMMING_THRESHOLD: int = 10       # Max Hamming distance for pHash match (>=85-88% visual similarity)
    
    # High-Reputation Authoritative Domains (Tranco/Alexa Top Whitelist)
    HIGH_REPUTATION_DOMAINS: set = {
        "google.com", "google.co.in", "google.co.uk", "google.de", "google.fr", "google.ca", "google.com.au",
        "youtube.com", "gmail.com", "googlevideo.com", "gstatic.com",
        "microsoft.com", "live.com", "office.com", "office365.com", "bing.com", "msn.com", "outlook.com", "windows.net", "azure.com",
        "apple.com", "icloud.com",
        "amazon.com", "amazon.co.uk", "amazon.de", "amazon.in", "aws.amazon.com",
        "wikipedia.org", "wikimedia.org", "w3.org", "example.com", "example.org", "example.net",
        "github.com", "github.io", "gitlab.com", "stackoverflow.com", "stackexchange.com",
        "mozilla.org", "python.org", "golang.org", "rust-lang.org", "nodejs.org",
        "facebook.com", "fb.com", "instagram.com", "whatsapp.com",
        "x.com", "twitter.com", "linkedin.com", "reddit.com", "pinterest.com",
        "netflix.com", "spotify.com", "zoom.us", "dropbox.com", "slack.com",
        "cloudflare.com", "fastly.net", "akamai.com", "archive.org",
        "nytimes.com", "bbc.com", "bbc.co.uk", "cnn.com", "theguardian.com", "reuters.com", "bloomberg.com", "forbes.com"
    }

    # User-Agents
    USER_AGENT_BOT: str = "User-Agent: python-requests/2.31.0 (CloakBuster-Bot-Probe)"
    USER_AGENT_DESKTOP: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    USER_AGENT_MOBILE: str = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"

settings = Settings()
