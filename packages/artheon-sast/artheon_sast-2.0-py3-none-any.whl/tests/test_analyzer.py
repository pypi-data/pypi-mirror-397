import pytest
import tempfile
from pathlib import Path
from language_analyzer import SecurityScanner


def test_scanner_initialization():
    scanner = SecurityScanner()
    assert scanner.directory.exists()


def test_scanner_invalid_directory():
    with pytest.raises(ValueError):
        SecurityScanner("/ruta/inexistente/12345")


def test_scan_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        scanner = SecurityScanner(tmpdir)
        scanner.scan()
        assert scanner.findings == []


def test_scan_with_vulnerabilities():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir, "vulnerable.js")
        test_file.write_text("eval(userInput);")
        scanner = SecurityScanner(tmpdir)
        scanner.scan()
        assert len(scanner.findings) > 0
        assert scanner.findings[0]['rule_id'] == 'eval_usage'


def test_ignore_directories():
    with tempfile.TemporaryDirectory() as tmpdir:
        node_modules = Path(tmpdir, "node_modules")
        node_modules.mkdir()
        Path(node_modules, "package.js").write_text("eval(x);")
        Path(tmpdir, "app.js").write_text("eval(y);")
        scanner = SecurityScanner(tmpdir)
        scanner.scan()
        assert len(scanner.findings) == 1


def test_html_report_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir, "test.js")
        test_file.write_text("eval(x);")
        scanner = SecurityScanner(tmpdir)
        scanner.scan()
        report_path = scanner.generate_html_report(open_browser=False)
        assert Path(report_path).exists()
        assert report_path.endswith('.html')
