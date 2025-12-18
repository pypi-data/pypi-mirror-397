# ARTHEON-SAST

**Static Application Security Testing Tool for JavaScript**

A powerful, minimalist SAST scanner designed to detect security vulnerabilities in JavaScript code with precision and simplicity.

---

## Features

- 🔍 **11 Vulnerability Categories** - Detects eval usage, hardcoded secrets, SQL injection, XSS, and more
- 128 **Comprehensive Regex Patterns** - Covers common security pitfalls
- 📊 **Professional HTML Reports** - Clean, minimalista design inspired by SonarQube
- ⚡ **Fast Scanning** - Efficient line-by-line vulnerability detection
- 🎯 **No Duplicates** - Smart duplicate prevention system
- 📱 **Responsive Reports** - Works on desktop and mobile devices

## Installation

### From PyPI
```bash
pip install artheon-sast
```

### Development Installation
```bash
git clone https://github.com/yourusername/artheon-sast.git
cd artheon-sast
pip install -e .
```

## Usage

### Command Line
```bash
artheon-sast /path/to/your/project
```

This will:
1. Scan all `.js` files in the directory
2. Detect security vulnerabilities
3. Generate an HTML report
4. Automatically open the report in your browser

### Python API
```python
from language_analyzer import SecurityScanner

scanner = SecurityScanner("/path/to/project")
scanner.scan()
report_path = scanner.generate_html_report()
```

## Vulnerability Categories

| Category | Severity | Examples |
|----------|----------|----------|
| eval() Usage | CRITICAL | `eval(userInput)` |
| Hardcoded Secrets | CRITICAL | API keys, passwords in code |
| SQL Injection | CRITICAL | Dynamic SQL queries |
| Command Injection | CRITICAL | Shell command execution |
| XSS Vulnerabilities | HIGH | Unsafe HTML injection |
| Insecure Crypto | HIGH | MD5, SHA1 usage |
| Path Traversal | HIGH | Unsafe file path handling |
| Insecure CORS | MEDIUM | Wildcard CORS policies |
| No Input Validation | MEDIUM | Missing parameter checks |
| Prototype Pollution | HIGH | Unsafe object manipulation |
| Insecure Dependencies | MEDIUM | Known vulnerable packages |

## Report Format

The tool generates a professional HTML report with:

- **Summary Metrics** - Total issues, critical, high, and medium severity counts
- **File Grouping** - Vulnerabilities organized by file
- **Context Display** - Shows the exact line of code with the vulnerability
- **Severity Indicators** - Color-coded by severity level
- **Responsive Design** - Works on all screen sizes

## Testing

```bash
pytest tests/ -v
```

All tests pass: ✅ 6/6 tests passing

## Requirements

- Python 3.8+
- No external dependencies (uses only stdlib)

## Authors

- **Dorian Tituaña**
- **Ismael Toala**

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is designed for authorized security testing only. Users are responsible for ensuring they have permission to scan the code they analyze.

---

**Developed with ❤️ for secure code**
