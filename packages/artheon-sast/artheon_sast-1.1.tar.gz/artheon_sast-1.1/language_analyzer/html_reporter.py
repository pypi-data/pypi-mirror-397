import os
from pathlib import Path
from datetime import datetime


class HTMLReporter:
    def __init__(self, findings, directory, js_files_count):
        self.findings = findings
        self.directory = directory
        self.js_files_count = js_files_count
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(self, output_path: str = "sast_report.html"):
        """Genera el reporte HTML y lo guarda."""
        html_content = self._build_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _build_html(self):
        """Construye el HTML del reporte."""
        severity_counts = self._count_by_severity()
        findings_by_file = self._group_by_file()
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAST Security Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: #fff;
            border-bottom: 1px solid #e0e0e0;
            padding: 40px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h1 {{
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 8px;
        }}
        
        .header-meta {{
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #666;
        }}
        
        .header-meta span {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .metrics {{
            background: transparent;
            margin: 40px 40px;
            border-radius: 0;
            box-shadow: none;
            border: none;
            border-bottom: 1px solid #e0e0e0;
            padding: 30px 0;
            overflow: visible;
        }}
        
        .metrics-title {{
            display: none;
        }}
        
        .metrics-top {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 60px;
            margin-bottom: 30px;
        }}
        
        .metrics-bottom {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 60px;
        }}
        
        .metric-box {{
            padding: 0;
            text-align: left;
            border-radius: 0;
            background: transparent;
            border: none;
            position: relative;
            transition: none;
        }}
        
        .metric-box:hover {{
            background: transparent;
            transform: none;
            box-shadow: none;
        }}
        
        .metric-icon {{
            display: none;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 6px;
            line-height: 1;
            letter-spacing: -0.5px;
        }}
        
        .metric-label {{
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 500;
        }}
        
        /* Estilos específicos por tipo de métrica - solo colores en números */
        .metric-critical .metric-value {{ color: #ef4444; }}
        
        .metric-high .metric-value {{ color: #f97316; }}
        
        .metric-medium .metric-value {{ color: #eab308; }}
        
        .metric-info .metric-value {{ color: #3b82f6; }}
        
        main {{
            padding: 30px 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .file-group {{
            background: #fff;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .file-header {{
            background: #f9f9f9;
            padding: 16px 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
        }}
        
        .file-name {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            color: #0d47a1;
        }}
        
        .file-count {{
            background: #e3f2fd;
            color: #0d47a1;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .findings-list {{
            padding: 0;
        }}
        
        .finding {{
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 16px;
            transition: background 0.2s;
        }}
        
        .finding:hover {{
            background: #fafafa;
        }}
        
        .finding:last-child {{
            border-bottom: none;
        }}
        
        .severity-indicator {{
            width: 4px;
            border-radius: 2px;
            flex-shrink: 0;
            margin-top: 4px;
        }}
        
        .severity-critical {{ background: #ef4444; }}
        .severity-high {{ background: #f97316; }}
        .severity-medium {{ background: #eab308; }}
        
        .finding-content {{
            flex: 1;
            min-width: 0;
        }}
        
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 8px;
        }}
        
        .finding-title {{
            font-weight: 600;
            color: #1a1a1a;
            font-size: 14px;
        }}
        
        .severity-badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .severity-badge.critical {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .severity-badge.high {{
            background: #ffedd5;
            color: #7c2d12;
        }}
        
        .severity-badge.medium {{
            background: #fef3c7;
            color: #78350f;
        }}
        
        .finding-meta {{
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .finding-meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .finding-meta-label {{
            color: #999;
            font-weight: 500;
        }}
        
        .finding-code {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 12px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin: 10px 0;
            border: 1px solid #333;
            line-height: 1.4;
            max-height: 120px;
            overflow-y: auto;
        }}
        
        .finding-code::-webkit-scrollbar {{
            height: 6px;
            width: 6px;
        }}
        
        .finding-code::-webkit-scrollbar-track {{
            background: #2a2a2a;
            border-radius: 3px;
        }}
        
        .finding-code::-webkit-scrollbar-thumb {{
            background: #404040;
            border-radius: 3px;
        }}
        
        .finding-code::-webkit-scrollbar-thumb:hover {{
            background: #505050;
        }}
        
        .finding-description {{
            color: #555;
            font-size: 13px;
            font-style: italic;
            margin-top: 8px;
            line-height: 1.5;
        }}
        
        .recommendations {{
            margin-top: 12px;
            padding: 12px;
            background: #f0f4ff;
            border-left: 3px solid #3b82f6;
            border-radius: 4px;
        }}
        
        .recommendations-title {{
            font-weight: 600;
            color: #1e40af;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .recommendations-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .recommendations-list li {{
            color: #1e40af;
            font-size: 12px;
            padding: 4px 0;
            padding-left: 20px;
            position: relative;
            line-height: 1.4;
        }}
        
        .recommendations-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            font-weight: bold;
        }}
        
        .no-findings {{
            text-align: center;
            padding: 60px 20px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        
        .no-findings h2 {{
            font-size: 24px;
            color: #28a745;
            margin-bottom: 10px;
        }}
        
        .no-findings p {{
            color: #666;
            font-size: 14px;
        }}
        
        footer {{
            background: #f9f9f9;
            padding: 20px 40px;
            text-align: center;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            header {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 20px;
            }}
            
            main {{
                padding: 20px;
            }}
            
            .header-meta {{
                flex-direction: column;
                gap: 8px;
            }}
            
            .metrics {{
                margin: 30px 20px;
                padding: 0;
            }}
            
            .metrics-title {{
                font-size: 12px;
                margin-bottom: 20px;
            }}
            
            .metrics-top,
            .metrics-bottom {{
                grid-template-columns: 1fr;
                gap: 32px;
            }}
            
            .metric-box {{
                padding: 0;
            }}
            
            .metric-value {{
                font-size: 32px;
            }}
            
            .metric-icon {{
                font-size: 20px;
            }}
            
            .finding {{
                flex-direction: column;
            }}
            
            .finding-header {{
                flex-direction: column;
            }}
            
            .file-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Security Analysis Report</h1>
            <div class="header-meta">
                <span><strong>Directory:</strong> {self.directory}</span>
                <span><strong>Generated:</strong> {self.timestamp}</span>
            </div>
        </div>
    </header>
    
    <div class="container">
        <div class="metrics">
            <div class="metrics-top">
                <div class="metric-box metric-info">
                    <div class="metric-value">{len(self.findings)}</div>
                    <div class="metric-label">Total Issues</div>
                </div>
                <div class="metric-box metric-critical">
                    <div class="metric-value">{self._count_by_severity().get('critical', 0)}</div>
                    <div class="metric-label">Critical</div>
                </div>
                <div class="metric-box metric-high">
                    <div class="metric-value">{self._count_by_severity().get('high', 0)}</div>
                    <div class="metric-label">High</div>
                </div>
            </div>
            <div class="metrics-bottom">
                <div class="metric-box metric-medium">
                    <div class="metric-value">{self._count_by_severity().get('medium', 0)}</div>
                    <div class="metric-label">Medium</div>
                </div>
                <div class="metric-box metric-info">
                    <div class="metric-value">{self.js_files_count}</div>
                    <div class="metric-label">JS Files</div>
                </div>
                <div class="metric-box metric-info">
                    <div class="metric-value">{len(self._group_by_file())}</div>
                    <div class="metric-label">Affected Files</div>
                </div>
            </div>
        </div>
        
        <main>
"""
        
        if not self.findings:
            html += """
            <div class="no-findings">
                <h2>✓ No vulnerabilities found</h2>
                <p>Your code passed the security analysis.</p>
            </div>
"""
        else:
            html += self._build_findings_html(self._group_by_file())
        
        html += """
        </main>
    </div>
    
    <footer>
        <p>SAST (Static Application Security Testing) • Professional Security Analysis</p>
    </footer>
</body>
</html>
"""
        return html

    def _count_by_severity(self):
        """Cuenta vulnerabilidades por severidad."""
        counts = {}
        for finding in self.findings:
            severity = finding['severity']
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _group_by_file(self):
        """Agrupa hallazgos por archivo."""
        grouped = {}
        for finding in self.findings:
            file_path = finding['file']
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(finding)
        return grouped

    def _build_findings_html(self, findings_by_file):
        """Construye el HTML de los hallazgos."""
        html = ""
        
        for file_path in sorted(findings_by_file.keys()):
            file_findings = findings_by_file[file_path]
            sorted_findings = sorted(file_findings, key=lambda x: x['line'])
            
            html += f"""
            <div class="file-group">
                <div class="file-header">
                    <span class="file-name">{file_path}</span>
                    <span class="file-count">{len(file_findings)} issue{'s' if len(file_findings) != 1 else ''}</span>
                </div>
                <div class="findings-list">
"""
            
            for finding in sorted_findings:
                severity = finding['severity']
                recommendations_html = ""
                
                # Agregar recomendaciones si existen
                if 'recommendations' in finding and finding['recommendations']:
                    recommendations_html = '<div class="recommendations"><div class="recommendations-title">Recommendations</div><ul class="recommendations-list">'
                    for rec in finding['recommendations']:
                        recommendations_html += f'<li>{self._escape_html(rec)}</li>'
                    recommendations_html += '</ul></div>'
                
                html += f"""
                    <div class="finding">
                        <div class="severity-indicator severity-{severity}"></div>
                        <div class="finding-content">
                            <div class="finding-header">
                                <div class="finding-title">{finding['rule_name']}</div>
                                <span class="severity-badge {severity}">{severity}</span>
                            </div>
                            <div class="finding-meta">
                                <div class="finding-meta-item">
                                    <span class="finding-meta-label">Line</span>
                                    {finding['line']}
                                </div>
                                <div class="finding-meta-item">
                                    <span class="finding-meta-label">Rule</span>
                                    {finding['rule_id']}
                                </div>
                            </div>
                            <div class="finding-code">{self._escape_html(finding['code'])}</div>
                            <div class="finding-description">{finding['description']}</div>
                            {recommendations_html}
                        </div>
                    </div>
"""
            
            html += """
                </div>
            </div>
"""
        
        return html

    def _escape_html(self, text):
        """Escapa caracteres HTML."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
