import json
from pathlib import Path

def export_to_json(scan, findings) -> str:
    data = {
        "scan_id": scan.id,
        "target": scan.target_url,
        "date": str(scan.created_at),
        "status": scan.status,
        "findings": [
            {
                "module": f.module_name,
                "severity": f.severity,
                "description": f.description
            } for f in findings
        ]
    }
    return json.dumps(data, indent=4, ensure_ascii=False)

def export_to_html(scan, findings) -> str:
    findings_rows = ""
    for f in findings:
        severity_color = "#e67e22" if f.severity == "MEDIUM" else ("#c0392b" if f.severity == "HIGH" else "#27ae60")
        findings_rows += f"""
        <tr>
            <td>{f.module_name}</td>
            <td><span style="color: {severity_color}; font-weight: bold;">{f.severity}</span></td>
            <td>{f.description}</td>
        </tr>
        """

    html_template = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Aegis-Recon Security Report - Scan #{scan.id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background: #0f172a; color: #e2e8f0; }}
        .container {{ max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top: 0; }}
        h2 {{ color: #f8fafc; margin-top: 25px; }}
        .meta {{ margin-bottom: 25px; padding: 15px; background: #0f172a; border-radius: 8px; border-right: 4px solid #38bdf8; }}
        .meta p {{ margin: 5px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; border: 1px solid #334155; text-align: right; }}
        th {{ background-color: #334155; color: #f8fafc; }}
        tr:nth-child(even) {{ background-color: #1a2332; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.85em; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Aegis-Recon Security Report</h1>
        <div class="meta">
            <p><strong>معرف الفحص (Scan ID):</strong> #{scan.id}</p>
            <p><strong>الهدف المستهدف (Target):</strong> {scan.target_url}</p>
            <p><strong>تاريخ ووقت الفحص:</strong> {scan.created_at}</p>
            <p><strong>حالة الفحص:</strong> {scan.status}</p>
        </div>
        <h2>📋 تفاصيل الاكتشافات الأمنية</h2>
        <table>
            <thead>
                <tr>
                    <th>الوحدة (Module)</th>
                    <th>مستوى الخطورة</th>
                    <th>الوصف</th>
                </tr>
            </thead>
            <tbody>
                {findings_rows if findings_rows else '<tr><td colspan="3" style="text-align: center;">لا توجد اكتشافات مسجلة</td></tr>'}
            </tbody>
        </table>
        <div class="footer">
            Generated automatically by Aegis-Recon Framework on Termux
        </div>
    </div>
</body>
</html>
"""
    return html_template
