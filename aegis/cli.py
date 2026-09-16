import asyncio
from pathlib import Path
import argparse
from rich.console import Console
from rich.table import Table

from aegis.config import Settings
from aegis.core.http import HttpClient
from aegis.db.session import Database
from aegis.db.models import ScanModel, FindingModel
from aegis.scope import Scope
from aegis.modules.headers import HeadersModule
from aegis.modules.paths import PathDiscoveryModule
from aegis.modules.ports import PortScannerModule
from aegis.modules.signatures import SignaturesModule
from aegis.runner import ModuleRunner
from aegis.report import export_to_json, export_to_html
from sqlalchemy import select

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Aegis-Recon: Lightweight Security Scanner for Termux")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # أمر الفحص
    scan_parser = subparsers.add_parser("scan", help="Scan a target URL")
    scan_parser.add_argument("target", help="Target URL or IP to scan")
    scan_parser.add_argument("-m", "--module", action="append", default=["headers"], help="Modules to run")
    scan_parser.add_argument("--db", default="aegis.db", help="Path to SQLite database")

    # أمر عرض السجل العام
    history_parser = subparsers.add_parser("history", help="View past scan history")
    history_parser.add_argument("--db", default="aegis.db", help="Path to SQLite database")

    # أمر عرض تفاصيل فحص معين
    details_parser = subparsers.add_parser("details", help="View findings for a specific scan ID")
    details_parser.add_argument("scan_id", type=int, help="Scan ID to view details for")
    details_parser.add_argument("--db", default="aegis.db", help="Path to SQLite database")

    # أمر تصدير التقارير
    report_parser = subparsers.add_parser("report", help="Export scan results to JSON or HTML")
    report_parser.add_argument("scan_id", type=int, help="Scan ID to export")
    report_parser.add_argument("--format", choices=["json", "html"], default="html", help="Export format")
    report_parser.add_argument("-o", "--output", help="Output file path")
    report_parser.add_argument("--db", default="aegis.db", help="Path to SQLite database")

    args = parser.parse_args()

    async def _run():
        db = Database(f"sqlite+aiosqlite:///{args.db}")
        await db.init()

        if args.command == "history":
            async with db.get_session() as session:
                result = await session.execute(select(ScanModel))
                scans = result.scalars().all()

            table = Table(title="Scan History")
            table.add_column("ID", style="cyan")
            table.add_column("Target", style="magenta")
            table.add_column("Date", style="green")
            table.add_column("Status", style="yellow")

            for s in scans:
                table.add_row(str(s.id), s.target_url, str(s.created_at), s.status)

            console.print(table)
            return

        if args.command == "details":
            async with db.get_session() as session:
                scan_res = await session.execute(select(ScanModel).where(ScanModel.id == args.scan_id))
                scan = scan_res.scalar_one_or_none()

                if not scan:
                    console.print(f"[bold red][-] Scan ID {args.scan_id} not found![/bold red]")
                    return

                findings_res = await session.execute(select(FindingModel).where(FindingModel.scan_id == args.scan_id))
                findings = findings_res.scalars().all()

            table = Table(title=f"Findings for Scan #{scan.id} ({scan.target_url})")
            table.add_column("Module", style="magenta")
            table.add_column("Severity", style="yellow")
            table.add_column("Description", style="white")

            for f in findings:
                table.add_row(f.module_name, f.severity, f.description)

            console.print(table)
            return

        if args.command == "report":
            async with db.get_session() as session:
                scan_res = await session.execute(select(ScanModel).where(ScanModel.id == args.scan_id))
                scan = scan_res.scalar_one_or_none()

                if not scan:
                    console.print(f"[bold red][-] Scan ID {args.scan_id} not found![/bold red]")
                    return

                findings_res = await session.execute(select(FindingModel).where(FindingModel.scan_id == args.scan_id))
                findings = findings_res.scalars().all()

            if args.format == "json":
                content = export_to_json(scan, findings)
                default_output = f"report_scan_{scan.id}.json"
            else:
                content = export_to_html(scan, findings)
                default_output = f"report_scan_{scan.id}.html"

            output_path = args.output or default_output
            Path(output_path).write_text(content, encoding="utf-8")
            console.print(f"[bold green][+] Report successfully exported to: {output_path}[/bold green]")
            return

        if args.command == "scan":
            settings = Settings()
            scope = Scope.load(Path("scope.yaml"))
            if scope.allow or scope.deny:
                if not scope.is_allowed(args.target):
                    console.print(f"[bold red][-] Target {args.target} is blocked by scope.yaml rules![/bold red]")
                    return

            mod_instances = []
            for m in args.module:
                if m == "headers":
                    mod_instances.append(HeadersModule())
                elif m == "paths":
                    mod_instances.append(PathDiscoveryModule())
                elif m == "ports":
                    mod_instances.append(PortScannerModule())
                elif m == "signatures":
                    mod_instances.append(SignaturesModule())
                else:
                    console.print(f"[yellow][!] Unknown module: {m}[/yellow]")

            if not mod_instances:
                console.print("[red][-] No valid modules selected.[/red]")
                return

            console.print(f"[bold cyan][*] Starting scan against target: {args.target}[/bold cyan]")
            
            async with HttpClient(settings) as client:
                runner = ModuleRunner(db, client)
                result = await runner.run(args.target, mod_instances)

            table = Table(title=f"Scan Results for {result.target_url}")
            table.add_column("Module", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Findings", style="yellow")
            table.add_column("Error", style="red")

            for r in result.modules:
                table.add_row(
                    r.module_name,
                    r.status.value,
                    str(r.findings_count),
                    r.error or "-"
                )

            console.print(table)

    asyncio.run(_run())

if __name__ == "__main__":
    main()
