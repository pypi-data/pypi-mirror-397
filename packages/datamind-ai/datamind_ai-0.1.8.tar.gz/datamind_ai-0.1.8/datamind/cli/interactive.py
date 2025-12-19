"""Interactive mode for DataMind."""

import os
import pandas as pd
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


class InteractiveSession:
    """Interactive DataMind session."""

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.ai_analyzer = None
        self._init_ai()

    def _init_ai(self):
        """Initialize AI analyzer."""
        try:
            if os.environ.get('GROQ_API_KEY'):
                from datamind.ai.groq_ai import GroqAnalyzer
                self.ai_analyzer = GroqAnalyzer()
            elif os.environ.get('GEMINI_API_KEY'):
                from datamind.ai.gemini import GeminiAnalyzer
                self.ai_analyzer = GeminiAnalyzer()
        except Exception as e:
            console.print(f"[yellow]AI yuklanmadi: {e}[/yellow]")

    def load(self, file_path: str) -> bool:
        """Load a data file."""
        try:
            from datamind.core.loader import DataLoader
            loader = DataLoader(file_path)
            self.df = loader.load()
            self.file_path = file_path
            info = loader.get_info()

            console.print(f"[green]✅ Yuklandi:[/green] {file_path}")
            console.print(f"   {info['rows']} qator x {info['columns']} ustun")
            return True
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")
            return False

    def diagnose(self) -> None:
        """Diagnose data issues."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang: load fayl.csv[/yellow]")
            return

        from datamind.agents import AutoFixAgent
        agent = AutoFixAgent(self.df)
        diagnosis = agent.diagnose()

        score = diagnosis['quality_score']
        color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        console.print(f"\n[bold]📊 Data Sifati:[/bold] [{color}]{score}/100[/{color}]")

        dup = diagnosis['duplicates']
        if dup['count'] > 0:
            console.print(f"[red]🔄 Dublikatlar:[/red] {dup['count']}")

        missing = diagnosis['missing']
        if missing['total'] > 0:
            console.print(f"[yellow]❓ Bo'sh qiymatlar:[/yellow] {missing['total']}")

        outliers = diagnosis['outliers']
        if outliers['total_count'] > 0:
            console.print(f"[yellow]📈 Outliers:[/yellow] {outliers['total_count']}")

    def fix(self, output: Optional[str] = None) -> None:
        """Auto-fix data issues."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang: load fayl.csv[/yellow]")
            return

        from datamind.agents import AutoFixAgent
        agent = AutoFixAgent(self.df, use_ai=True)
        agent.auto_fix()

        self.df = agent.get_result()
        comparison = agent.compare()

        console.print(f"\n[green]✅ Tuzatildi![/green]")
        console.print(f"   Qatorlar: {comparison['original']['rows']} → {comparison['fixed']['rows']}")
        console.print(f"   Bo'sh: {comparison['original']['missing']} → {comparison['fixed']['missing']}")
        console.print(f"   Dublikat: {comparison['original']['duplicates']} → {comparison['fixed']['duplicates']}")

        if output:
            self._save(output)

    def clean(self, output: Optional[str] = None) -> None:
        """Clean data."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang: load fayl.csv[/yellow]")
            return

        from datamind.agents import CleaningAgent
        agent = CleaningAgent(self.df)
        agent.auto_clean()

        self.df = agent.get_result()
        report = agent.get_report_dict()

        console.print(f"\n[green]✅ Tozalandi![/green]")
        console.print(f"   {report['original_shape']} → {report['final_shape']}")

        if output:
            self._save(output)

    def validate(self) -> None:
        """Validate data."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang: load fayl.csv[/yellow]")
            return

        from datamind.agents import ValidatorAgent
        agent = ValidatorAgent(self.df)
        agent.run_all_checks()
        report = agent.get_report_dict()

        score = report['score']
        color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        console.print(f"\n[bold]📊 Validatsiya:[/bold] [{color}]{score}/100[/{color}]")
        console.print(f"   ✓ O'tdi: {report['passed']} | ✗ O'tmadi: {report['failed']}")

    def analyze(self, output: Optional[str] = None) -> None:
        """Analyze and create dashboard."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang: load fayl.csv[/yellow]")
            return

        from datamind.core.loader import DataLoader
        from datamind.dashboard.charts import ChartGenerator
        from datamind.dashboard.generator import DashboardGenerator

        loader = DataLoader.__new__(DataLoader)
        loader.df = self.df
        info = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'column_names': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'missing_values': self.df.isnull().sum().to_dict(),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }

        analysis = {}
        if self.ai_analyzer:
            try:
                analysis = self.ai_analyzer.analyze_data(self.df, info)
                if analysis.get('summary'):
                    console.print(f"\n[cyan]🧠 AI:[/cyan] {analysis['summary']}")
            except:
                pass

        if output:
            chart_gen = ChartGenerator(self.df)
            charts = []

            if analysis.get('suggested_charts'):
                charts = chart_gen.auto_charts(analysis['suggested_charts'])
            else:
                numeric_cols = self.df.select_dtypes(include=['number']).columns
                cat_cols = self.df.select_dtypes(include=['object']).columns

                if len(cat_cols) > 0:
                    charts.append(chart_gen.create_chart('bar', x_column=cat_cols[0], title=f"{cat_cols[0]} taqsimoti"))
                if len(numeric_cols) > 0:
                    charts.append(chart_gen.create_chart('histogram', x_column=numeric_cols[0], title=f"{numeric_cols[0]} histogramma"))

            title = Path(self.file_path).stem if self.file_path else "Data"
            dashboard = DashboardGenerator(title=title.replace('_', ' ').title(), analysis=analysis, info=info)
            dashboard.add_charts(charts)

            # Ensure output is just the filename
            output_filename = Path(output).name if output else "dashboard.html"
            if not output_filename.endswith('.html'):
                output_filename = "dashboard.html"

            output_file = dashboard.generate(output_filename)
            console.print(f"[green]✅ Dashboard yaratildi:[/green] {output_file}")

    def query(self, question: str) -> None:
        """Ask AI a question about the data or general chat."""
        if not self.ai_analyzer:
            console.print("[yellow]AI mavjud emas. API key o'rnating.[/yellow]")
            return

        try:
            if self.df is not None:
                # Data mavjud - data haqida savol
                answer = self.ai_analyzer.ask_question(self.df, question)
            else:
                # Data yo'q - oddiy suhbat
                answer = self.ai_analyzer.chat(question)
            console.print(f"\n[cyan]💡 Javob:[/cyan] {answer}")
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")

    def run_task(self, task: str) -> None:
        """Execute a data task using AI-generated code."""
        if not self.ai_analyzer:
            console.print("[yellow]AI mavjud emas. API key o'rnating.[/yellow]")
            return

        try:
            console.print(f"[dim]🤖 Kod generatsiya qilinmoqda...[/dim]")
            result, code = self.ai_analyzer.execute_task(task, self.file_path, self.df)

            # Show generated code
            console.print(f"\n[cyan]📝 Kod:[/cyan]")
            console.print(f"[dim]{code}[/dim]")

            # Show result
            console.print(f"\n[green]✅ Natija:[/green]")
            if isinstance(result, pd.DataFrame):
                self.df = result  # Update current dataframe
                console.print(result.to_string(max_rows=20))
                console.print(f"\n[dim]{len(result)} qator x {len(result.columns)} ustun[/dim]")
            else:
                console.print(str(result))
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")

    def auto_agent(self, file_path: str) -> None:
        """Fully autonomous agent - analyzes file on its own."""
        if not self.ai_analyzer:
            console.print("[yellow]AI mavjud emas. API key o'rnating.[/yellow]")
            return

        console.print(f"\n[bold cyan]🤖 Agent ishga tushdi...[/bold cyan]")
        console.print(f"[dim]Fayl: {file_path}[/dim]\n")

        try:
            # Run autonomous analysis
            console.print("[dim]1️⃣ Data yuklanmoqda...[/dim]")
            results = self.ai_analyzer.auto_analyze(file_path)

            # Update session state
            if results['df'] is not None:
                self.df = results['df']
                self.file_path = file_path
                console.print(f"[green]✅ Yuklandi:[/green] {len(self.df)} qator x {len(self.df.columns)} ustun\n")

            # Show executed code
            if results['code_history']:
                console.print("[bold]📝 Bajarilgan kodlar:[/bold]")
                for name, code in results['code_history']:
                    console.print(f"[cyan]{name}:[/cyan]")
                    console.print(f"[dim]{code}[/dim]\n")

            # Show summary
            if results['summary']:
                console.print(f"[bold]📊 Xulosa:[/bold]")
                console.print(f"{results['summary']}\n")

            # Show insights
            if results['insights']:
                console.print(f"[bold]💡 Topilmalar:[/bold]")
                for i, insight in enumerate(results['insights'], 1):
                    console.print(f"  {i}. {insight}")
                console.print()

            # Show chart suggestions
            if results['charts_data']:
                console.print(f"[bold]📈 Tavsiya etilgan grafiklar:[/bold]")
                for chart in results['charts_data']:
                    console.print(f"  • {chart.get('type', 'chart')}: {chart.get('title', '')}")
                console.print(f"\n[dim]Dashboard yaratish uchun: dashboard[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Agent xatosi: {e}[/red]")

    def head(self, n: int = 5) -> None:
        """Show first n rows."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang[/yellow]")
            return
        console.print(self.df.head(n).to_string())

    def columns(self) -> None:
        """Show columns info."""
        if self.df is None:
            console.print("[yellow]Avval fayl yuklang[/yellow]")
            return

        table = Table(title="Ustunlar", show_header=True)
        table.add_column("Ustun", style="cyan")
        table.add_column("Tur", style="yellow")
        table.add_column("Bo'sh", style="red")

        for col in self.df.columns:
            table.add_row(col, str(self.df[col].dtype), str(self.df[col].isnull().sum()))
        console.print(table)

    def _save(self, output: str) -> None:
        """Save DataFrame to file."""
        if self.df is None:
            return

        output_path = Path(output)
        if output_path.suffix == '.csv':
            self.df.to_csv(output, index=False)
        elif output_path.suffix in ['.xlsx', '.xls']:
            self.df.to_excel(output, index=False)
        else:
            self.df.to_csv(output, index=False)

        console.print(f"[green]✅ Saqlandi:[/green] {output}")

    def save(self, output: str) -> None:
        """Save current data."""
        self._save(output)

    def help(self) -> None:
        """Show help."""
        console.print(Panel("""
[bold cyan]DataMind Interaktiv Buyruqlar:[/bold cyan]

[green]Fayl bilan ishlash:[/green]
  load <fayl>         - Fayl yuklash
  save <fayl>         - Saqlash
  head [n]            - Birinchi n qatorni ko'rish
  columns             - Ustunlar haqida ma'lumot

[green]Tahlil:[/green]
  diagnose            - Muammolarni aniqlash
  validate            - Validatsiya
  analyze [fayl.html] - Dashboard yaratish

[green]Tuzatish:[/green]
  fix [fayl]          - AI avtomatik tuzatish
  clean [fayl]        - Tozalash

[green]AI:[/green]
  <savol>             - AI ga savol berish

[green]Boshqa:[/green]
  help                - Yordam
  exit / quit         - Chiqish
""", title="Yordam", border_style="cyan"))


def setup_api():
    """Setup API key with password protection or user's own key."""
    # Check if API key already exists
    if os.environ.get('GROQ_API_KEY') or os.environ.get('GEMINI_API_KEY'):
        return True

    console.print(Panel.fit(
        "[bold cyan]🔐 API Sozlash[/bold cyan]",
        border_style="cyan"
    ))

    console.print("\n[bold]API tanlang:[/bold]")
    console.print("  [cyan]1.[/cyan] Mavjud API bilan (parol kerak)")
    console.print("  [cyan]2.[/cyan] O'z API keyingiz bilan")
    console.print("  [cyan]3.[/cyan] API keysiz davom etish\n")

    choice = Prompt.ask("Tanlang", choices=["1", "2", "3"], default="1")

    if choice == "1":
        # Password protected shared API
        password = Prompt.ask("Parol kiriting", password=True)
        if password == "datamind2024":
            os.environ['GROQ_API_KEY'] = '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'
            console.print("[green]✅ API tayyor![/green]\n")
            return True
        else:
            console.print("[red]❌ Parol noto'g'ri![/red]")
            console.print("[dim]Parolni olish uchun: https://github.com/SaidjonRavshanov/datamind[/dim]\n")
            return False

    elif choice == "2":
        # User's own API key
        console.print("\n[dim]Groq API key olish: https://console.groq.com (bepul)[/dim]")
        api_key = Prompt.ask("API key kiriting")
        if api_key and api_key.startswith("gsk_"):
            os.environ['GROQ_API_KEY'] = api_key
            console.print("[green]✅ API tayyor![/green]\n")
            return True
        else:
            console.print("[yellow]⚠️ Noto'g'ri format. Groq key 'gsk_' bilan boshlanadi[/yellow]\n")
            return False

    else:
        # Continue without API
        console.print("[yellow]⚠️ AI funksiyalari ishlamaydi[/yellow]\n")
        return True


def run_interactive():
    """Run interactive mode."""
    console.print(Panel.fit(
        "[bold cyan]🧠 DataMind[/bold cyan] - Interaktiv Rejim\n[dim]Yordam uchun: help[/dim]",
        border_style="cyan"
    ))

    # Setup API if needed
    if not setup_api():
        return

    session = InteractiveSession()

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]datamind[/bold cyan]").strip()

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            # Exit commands
            if cmd in ['exit', 'quit', 'q']:
                console.print("[dim]Xayr![/dim]")
                break

            # File commands
            elif cmd == 'load':
                if args:
                    session.load(args)
                else:
                    console.print("[yellow]Foydalanish: load fayl.csv[/yellow]")

            elif cmd == 'save':
                if args:
                    session.save(args)
                else:
                    console.print("[yellow]Foydalanish: save fayl.csv[/yellow]")

            elif cmd == 'head':
                n = int(args) if args.isdigit() else 5
                session.head(n)

            elif cmd == 'columns':
                session.columns()

            # Analysis commands
            elif cmd == 'diagnose':
                session.diagnose()

            elif cmd == 'validate':
                session.validate()

            elif cmd == 'analyze':
                session.analyze(args if args else None)

            elif cmd == 'dashboard':
                # dashboard yoki dashboard report.html
                output = args if args else "dashboard.html"
                session.analyze(output)

            # Fix commands
            elif cmd == 'fix':
                session.fix(args if args else None)

            elif cmd == 'clean':
                session.clean(args if args else None)

            # Help
            elif cmd == 'help':
                session.help()

            # Run/execute task
            elif cmd == 'run':
                if args:
                    session.run_task(args)
                else:
                    console.print("[yellow]Foydalanish: run <vazifa>[/yellow]")
                    console.print("[dim]Misol: run 90000 qator yukla[/dim]")

            # Agent - autonomous analysis
            elif cmd == 'agent':
                if args:
                    session.auto_agent(args)
                else:
                    console.print("[yellow]Foydalanish: agent fayl.csv[/yellow]")
                    console.print("[dim]Agent faylni o'zi tahlil qiladi[/dim]")

            # Natural language commands
            else:
                lower_input = user_input.lower()

                # About/Author commands
                if any(word in lower_input for word in ['kim yaratgan', 'kim qilgan', 'muallif', 'author', 'yaratuvchi', 'dasturchi', 'kim tayyorlagan', 'kim dasturlagan', 'developer', 'created by', 'made by', 'who made', 'who created']):
                    console.print(Panel("""
[bold cyan]DataMind AI[/bold cyan]

[bold]Muallif:[/bold] Saidjon Ravshanov
[bold]GitHub:[/bold] https://github.com/SaidjonRavshanov
[bold]Loyiha:[/bold] https://github.com/SaidjonRavshanov/datamind
[bold]PyPI:[/bold] https://pypi.org/project/datamind-ai/

Data analitika uchun AI-powered CLI tool.
""", title="Haqida", border_style="cyan"))

                # About DataMind / What is this
                elif any(word in lower_input for word in ['vazifang nima', 'nima qila olasan', 'what can you do', 'nimalar qila olasan', 'qanday yordam', 'nima uchun kerak', 'sen nima', 'bu nima', 'what is this', 'what is datamind']):
                    console.print(Panel("""
[bold cyan]DataMind AI - Vazifalar[/bold cyan]

Men data analitika uchun AI yordamchiman. Quyidagilarni qila olaman:

[bold green]📊 Data bilan ishlash:[/bold green]
  • CSV, Excel, JSON fayllarni yuklash
  • Data haqida ma'lumot olish

[bold green]🔍 Tahlil:[/bold green]
  • Muammolarni aniqlash (diagnose)
  • Data sifatini tekshirish (validate)
  • AI bilan savolga javob berish

[bold green]🛠 Tuzatish:[/bold green]
  • Dublikatlarni o'chirish
  • Bo'sh qiymatlarni to'ldirish
  • Outlierlarni tuzatish
  • Avtomatik tozalash (fix, clean)

[bold green]📈 Vizualizatsiya:[/bold green]
  • Interaktiv dashboard yaratish
  • Grafiklar generatsiya qilish

[bold yellow]Boshlash:[/bold yellow] load fayl.csv
""", title="Imkoniyatlar", border_style="cyan"))

                # Dashboard commands
                elif any(word in lower_input for word in ['dashboard', 'дашборд', 'hisobot', 'report', 'grafik', 'qilib ber']):
                    session.analyze("dashboard.html")
                    console.print(f"[dim]Brauzerda ochish: xdg-open dashboard.html[/dim]")

                # Fix/clean commands
                elif any(word in lower_input for word in ['tozala', 'tuzat', 'fix', 'clean', 'почисти']):
                    session.fix()

                # Diagnose commands
                elif any(word in lower_input for word in ['tekshir', 'diagnose', 'muammo', 'xato']):
                    session.diagnose()

                # Validate commands
                elif any(word in lower_input for word in ['validatsiya', 'validate', 'tekshir']):
                    session.validate()

                # Agent/Analyze file commands (e.g., "data.csv tahlil qil", "analyze sales.csv")
                elif any(word in lower_input for word in ['tahlil qil', 'analyze', 'tahlil', 'o\'rgat', 'tekshir', 'ko\'r']):
                    # Extract file path from input
                    import re
                    file_match = re.search(r'[\w\-./\\]+\.(csv|xlsx|xls|json)', user_input, re.IGNORECASE)
                    if file_match:
                        file_path = file_match.group()
                        session.auto_agent(file_path)
                    elif session.file_path:
                        # Use already loaded file
                        session.auto_agent(session.file_path)
                    else:
                        console.print("[yellow]Fayl topilmadi. Misol: data.csv tahlil qil[/yellow]")

                # AI query (anything else)
                else:
                    session.query(user_input)

        except KeyboardInterrupt:
            console.print("\n[dim]Ctrl+C - Chiqish uchun 'exit' yozing[/dim]")
        except Exception as e:
            console.print(f"[red]Xato: {e}[/red]")
