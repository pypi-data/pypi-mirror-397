from .security_scanner import SecurityScanner
from .html_reporter import HTMLReporter
from .js_vulnerabilities import VULN_RULES
from .python_vulnerabilities import PYTHON_VULN_RULES
from .java_vulnerabilities import JAVA_VULN_RULES
from .csharp_vulnerabilities import CSHARP_VULN_RULES

__version__ = "0.1.0"
__all__ = ["SecurityScanner", "HTMLReporter", "VULN_RULES", "PYTHON_VULN_RULES", "JAVA_VULN_RULES", "CSHARP_VULN_RULES"]

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
