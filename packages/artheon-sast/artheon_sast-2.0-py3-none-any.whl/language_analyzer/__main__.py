import sys
from .security_scanner import SecurityScanner


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        scanner = SecurityScanner(directory)
        scanner.scan()
        report_path = scanner.generate_html_report()
        print(f"Report generated: {report_path}")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
