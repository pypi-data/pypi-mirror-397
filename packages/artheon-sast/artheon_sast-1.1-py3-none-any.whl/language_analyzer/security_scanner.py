import os
import re
import webbrowser
from pathlib import Path
from .js_vulnerabilities import VULN_RULES
from .html_reporter import HTMLReporter


class SecurityScanner:
    def __init__(self, directory: str = None):
        if directory is None:
            directory = os.getcwd()
        self.directory = Path(directory)
        if not self.directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        self.js_files = []
        self.findings = []

    def find_js_files(self):
        """Find all .js files in the directory."""
        self.js_files = []
        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in self._ignore_dirs()]
            for file in files:
                if file.endswith('.js'):
                    self.js_files.append(Path(root) / file)
        return self.js_files

    def scan(self):
        """Scan all found JS files."""
        self.findings = []
        self.find_js_files()
        
        for js_file in self.js_files:
            self._scan_file(js_file)
        
        return self.findings

    def _scan_file(self, file_path):
        """Scan an individual JS file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return
        
        seen = set()
        
        for rule_id, rule in VULN_RULES.items():
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
                            'code': line_content.strip()
                        })
                        break

    def _ignore_dirs(self):
        return {
            ".git", ".venv", "venv", "node_modules", "__pycache__",
            ".pytest_cache", "dist", "build", ".tox", ".env",
            ".idea", ".vscode", "target", ".gradle",
        }

    def generate_html_report(self, output_path: str = "sast_report.html", open_browser: bool = True):
        """Generate HTML report and optionally open in browser."""
        reporter = HTMLReporter(self.findings, str(self.directory), len(self.js_files))
        report_path = reporter.generate(output_path)
        
        if open_browser:
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        
        return report_path
