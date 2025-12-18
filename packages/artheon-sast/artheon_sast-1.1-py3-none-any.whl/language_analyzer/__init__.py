from .security_scanner import SecurityScanner
from .html_reporter import HTMLReporter
from .js_vulnerabilities import VULN_RULES

__version__ = "0.1.0"
__all__ = ["SecurityScanner", "HTMLReporter", "VULN_RULES"]

# Display banner on import
_banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                    ARTHEON-SAST                                    ║
║                                                                    ║
║          Static Application Security Testing Tool                  ║
║                                                                    ║
║     Developed by Dorian Tituaña & Ismael Toala                     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
"""

print(_banner)
