import os
import re
import webbrowser
from pathlib import Path
from .js_vulnerabilities import VULN_RULES as JS_RULES
from .python_vulnerabilities import PYTHON_VULN_RULES
from .java_vulnerabilities import JAVA_VULN_RULES
from .csharp_vulnerabilities import CSHARP_VULN_RULES
from .html_reporter import HTMLReporter


class SecurityScanner:
    def __init__(self, directory: str = None):
        if directory is None:
            directory = os.getcwd()
        self.directory = Path(directory)
        if not self.directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        self.source_files = []
        self.findings = []
        self.language_rules = {
            '.js': JS_RULES,
            '.py': PYTHON_VULN_RULES,
            '.java': JAVA_VULN_RULES,
            '.cs': CSHARP_VULN_RULES,
        }

    def find_source_files(self):
        """Find all source files in the directory."""
        self.source_files = []
        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in self._ignore_dirs()]
            for file in files:
                if any(file.endswith(ext) for ext in self.language_rules.keys()):
                    self.source_files.append(Path(root) / file)
        return self.source_files

    def scan(self):
        """Scan all found source files."""
        self.findings = []
        self.find_source_files()
        
        for source_file in self.source_files:
            self._scan_file(source_file)
        
        return self.findings

    def _scan_file(self, file_path):
        """Scan an individual source file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return
        
        # Determine file language
        file_ext = file_path.suffix
        rules = self.language_rules.get(file_ext, {})
        
        if not rules:
            return
        
        seen = set()
        
        for rule_id, rule in rules.items():
            for line_num, line_content in enumerate(lines, 1):
                finding_key = (str(file_path), line_num, rule_id)
                
                if finding_key in seen:
                    continue
                
                for pattern in rule.get('patterns', []):
                    try:
                        regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                    except:
                        continue
                    
                    if regex.search(line_content):
                        seen.add(finding_key)
                        self.findings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'rule_id': rule_id,
                            'rule_name': rule['name'],
                            'severity': rule['severity'],
                            'description': rule['description'],
                            'recommendations': rule.get('recommendations', []),
                            'code': line_content.strip(),
                            'language': file_ext[1:].upper()
                        })
                        break

    def _ignore_dirs(self):
        return {
            ".git", ".venv", "venv", "node_modules", "__pycache__",
            ".pytest_cache", "dist", "build", ".tox", ".env",
            ".idea", ".vscode", "target", ".gradle", "bin", "obj",
            ".vs", "node_modules", "vendor", "package", ".bundle",
        }

    def generate_html_report(self, output_path: str = "sast_report.html", open_browser: bool = True):
        """Generate HTML report and optionally open in browser."""
        reporter = HTMLReporter(self.findings, str(self.directory), len(self.source_files))
        report_path = reporter.generate(output_path)
        
        if open_browser:
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        
        return report_path
