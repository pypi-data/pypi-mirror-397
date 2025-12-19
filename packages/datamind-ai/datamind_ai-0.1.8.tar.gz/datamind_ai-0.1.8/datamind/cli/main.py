"""DataMind CLI - AI-powered data analysis tool."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional

from datamind.core.loader import DataLoader
from datamind.dashboard.charts import ChartGenerator
from datamind.dashboard.generator import DashboardGenerator

import os

def get_ai_analyzer():
    """Get available AI analyzer (Groq or Gemini)."""
    # Try Groq first (faster, more reliable)
    if os.environ.get('GROQ_API_KEY'):
        from datamind.ai.groq_ai import GroqAnalyzer
        return GroqAnalyzer()
    # Fall back to Gemini
    elif os.environ.get('GEMINI_API_KEY'):
        from datamind.ai.gemini import GeminiAnalyzer
        return GeminiAnalyzer()
    else:
        raise ValueError(
            "API key topilmadi!\n"
            "Quyidagilardan birini o'rnating:\n"
            "  export GROQ_API_KEY='your-key'  (https://console.groq.com)\n"
            "  export GEMINI_API_KEY='your-key'  (https://makersuite.google.com/app/apikey)"
        )

app = typer.Typer(
    name="datamind",
    help="🧠 DataMind - AI bilan data tahlil va dashboard yaratish",
    add_completion=False,
)
console = Console()


@app.command()
def chat():
    """
    💬 Interaktiv rejim - bir marta chaqirib, ko'p buyruq bering.

    Misol: datamind chat
    """
    from datamind.cli.interactive import run_interactive
    run_interactive()


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Data fayl yo'li (CSV, Excel, JSON)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Dashboard fayl nomi"),
    no_ai: bool = typer.Option(False, "--no-ai", help="AI tahlilsiz, faqat statistika"),
):
    """
    📊 Data faylni tahlil qilish va dashboard yaratish.

    Misol: datamind analyze sales.csv -o report.html
    """

    console.print(Panel.fit(
        "[bold cyan]🧠 DataMind[/bold cyan] - AI Data Analyzer",
        border_style="cyan"
    ))

    # Load data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Data yuklanmoqda...", total=None)

        try:
            loader = DataLoader(file_path)
            df = loader.load()
            info = loader.get_info()
            progress.update(task, description="✅ Data yuklandi!")
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")
            raise typer.Exit(1)

    # Show basic info
    info_table = Table(title="📋 Data Ma'lumotlari", show_header=True, header_style="bold cyan")
    info_table.add_column("Parametr", style="cyan")
    info_table.add_column("Qiymat", style="white")
    info_table.add_row("Qatorlar", str(info['rows']))
    info_table.add_row("Ustunlar", str(info['columns']))
    info_table.add_row("Xotira", info['memory_usage'])
    console.print(info_table)

    # Show columns
    col_table = Table(title="📊 Ustunlar", show_header=True, header_style="bold green")
    col_table.add_column("Ustun", style="green")
    col_table.add_column("Tur", style="yellow")
    col_table.add_column("Bo'sh", style="red")
    for col in info['column_names']:
        col_table.add_row(
            col,
            info['dtypes'][col],
            str(info['missing_values'][col])
        )
    console.print(col_table)

    analysis = {}

    if not no_ai:
        # AI Analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🤖 AI tahlil qilmoqda...", total=None)

            try:
                analyzer = get_ai_analyzer()
                analysis = analyzer.analyze_data(df, info)
                progress.update(task, description="✅ AI tahlil tugadi!")
            except Exception as e:
                console.print(f"[yellow]⚠️ AI xatosi: {e}[/yellow]")
                analysis = {}

        # Show AI insights
        if analysis.get('summary'):
            console.print(Panel(
                analysis['summary'],
                title="🧠 AI Xulosasi",
                border_style="green"
            ))

        if analysis.get('insights'):
            console.print("\n[bold cyan]💡 Muhim Topilmalar:[/bold cyan]")
            for i, insight in enumerate(analysis['insights'], 1):
                console.print(f"  {i}. {insight}")

        if analysis.get('data_quality'):
            score = analysis['data_quality'].get('score', 0)
            color = "green" if score >= 7 else "yellow" if score >= 4 else "red"
            console.print(f"\n[bold]📈 Data Sifati:[/bold] [{color}]{score}/10[/{color}]")

    # Generate dashboard
    if output:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📊 Dashboard yaratilmoqda...", total=None)

            try:
                # Generate charts
                chart_gen = ChartGenerator(df)
                charts = []

                if analysis.get('suggested_charts'):
                    charts = chart_gen.auto_charts(analysis['suggested_charts'])
                else:
                    # Default charts if no AI suggestions
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns

                    if len(numeric_cols) >= 2:
                        charts.append(chart_gen.create_chart(
                            'scatter',
                            x_column=numeric_cols[0],
                            y_column=numeric_cols[1],
                            title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
                        ))

                    if len(cat_cols) > 0:
                        charts.append(chart_gen.create_chart(
                            'bar',
                            x_column=cat_cols[0],
                            title=f"{cat_cols[0]} taqsimoti"
                        ))

                    if len(numeric_cols) > 0:
                        charts.append(chart_gen.create_chart(
                            'histogram',
                            x_column=numeric_cols[0],
                            title=f"{numeric_cols[0]} histogramma"
                        ))

                # Generate dashboard
                dashboard = DashboardGenerator(
                    title=Path(file_path).stem.replace('_', ' ').title(),
                    analysis=analysis,
                    info=info,
                )
                dashboard.add_charts(charts)

                output_file = dashboard.generate(output)
                progress.update(task, description="✅ Dashboard tayyor!")

                console.print(f"\n[bold green]✅ Dashboard yaratildi:[/bold green] {output_file}")
                console.print(f"[dim]Brauzerda ochish uchun: file://{output_file}[/dim]")

            except Exception as e:
                console.print(f"[red]❌ Dashboard xatosi: {e}[/red]")


@app.command()
def query(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
    question: str = typer.Argument(..., help="Savol"),
):
    """
    ❓ Data haqida savol berish.

    Misol: datamind query sales.csv "eng ko'p sotilgan mahsulot qaysi?"
    """

    console.print(Panel.fit(
        "[bold cyan]🧠 DataMind[/bold cyan] - AI Question Answering",
        border_style="cyan"
    ))

    # Load data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Data yuklanmoqda...", total=None)

        try:
            loader = DataLoader(file_path)
            df = loader.load()
            progress.update(task, description="✅ Data yuklandi!")
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")
            raise typer.Exit(1)

    # Ask AI
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🤖 AI javob izlamoqda...", total=None)

        try:
            analyzer = get_ai_analyzer()
            answer = analyzer.ask_question(df, question)
            progress.update(task, description="✅ Javob topildi!")
        except Exception as e:
            console.print(f"[red]❌ AI xatosi: {e}[/red]")
            raise typer.Exit(1)

    console.print(f"\n[bold cyan]❓ Savol:[/bold cyan] {question}")
    console.print(Panel(answer, title="💡 Javob", border_style="green"))


@app.command()
def info(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
):
    """
    ℹ️ Data fayl haqida ma'lumot ko'rsatish.

    Misol: datamind info sales.csv
    """

    try:
        loader = DataLoader(file_path)
        df = loader.load()
        info = loader.get_info()
        summary = loader.get_summary()
    except Exception as e:
        console.print(f"[red]❌ Xato: {e}[/red]")
        raise typer.Exit(1)

    # Basic info
    console.print(Panel.fit(f"[bold]{file_path}[/bold]", border_style="cyan"))

    info_table = Table(show_header=False)
    info_table.add_column("", style="cyan")
    info_table.add_column("")
    info_table.add_row("Qatorlar", str(info['rows']))
    info_table.add_row("Ustunlar", str(info['columns']))
    info_table.add_row("Xotira", info['memory_usage'])
    console.print(info_table)

    # Numeric summary
    if summary['numeric_summary']:
        console.print("\n[bold cyan]📊 Raqamli ustunlar statistikasi:[/bold cyan]")
        for col, stats in summary['numeric_summary'].items():
            console.print(f"\n  [green]{col}[/green]")
            console.print(f"    Min: {stats.get('min', 'N/A'):.2f}")
            console.print(f"    Max: {stats.get('max', 'N/A'):.2f}")
            console.print(f"    O'rtacha: {stats.get('mean', 'N/A'):.2f}")


@app.command()
def diagnose(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
):
    """
    🔍 Data muammolarini aniqlash (diagnose).

    Misol: datamind diagnose sales.csv
    """
    from datamind.agents import AutoFixAgent

    console.print(Panel.fit(
        "[bold cyan]🔍 DataMind[/bold cyan] - Data Diagnostics",
        border_style="cyan"
    ))

    # Load data
    try:
        loader = DataLoader(file_path)
        df = loader.load()
    except Exception as e:
        console.print(f"[red]❌ Xato: {e}[/red]")
        raise typer.Exit(1)

    # Diagnose
    agent = AutoFixAgent(df)
    diagnosis = agent.diagnose()

    # Quality Score
    score = diagnosis['quality_score']
    color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    console.print(f"\n[bold]📊 Data Sifati:[/bold] [{color}]{score}/100[/{color}]")

    # Shape
    console.print(f"\n[bold cyan]📐 Shape:[/bold cyan] {diagnosis['shape']['rows']} qator x {diagnosis['shape']['columns']} ustun")

    # Duplicates
    dup = diagnosis['duplicates']
    if dup['count'] > 0:
        console.print(f"\n[bold red]🔄 Dublikatlar:[/bold red] {dup['count']} ({dup['percentage']}%)")
    else:
        console.print(f"\n[bold green]✅ Dublikatlar:[/bold green] Yo'q")

    # Missing values
    missing = diagnosis['missing']
    if missing['total'] > 0:
        console.print(f"\n[bold yellow]❓ Bo'sh qiymatlar:[/bold yellow] {missing['total']} ({missing['total_percentage']}%)")
        for col, count in missing['by_column'].items():
            console.print(f"   • {col}: {count}")
    else:
        console.print(f"\n[bold green]✅ Bo'sh qiymatlar:[/bold green] Yo'q")

    # Outliers
    outliers = diagnosis['outliers']
    if outliers['total_count'] > 0:
        console.print(f"\n[bold yellow]📈 Outliers:[/bold yellow] {outliers['total_count']}")
        for col, info in outliers['by_column'].items():
            console.print(f"   • {col}: {info['count']} (chegaralar: {info['bounds']})")
    else:
        console.print(f"\n[bold green]✅ Outliers:[/bold green] Yo'q")

    # Dtype suggestions
    dtypes = diagnosis['dtypes']
    if dtypes['suggestions']:
        console.print(f"\n[bold blue]🔧 Tur o'zgartirish tavsiyalari:[/bold blue]")
        for col, suggested in dtypes['suggestions'].items():
            console.print(f"   • {col}: → {suggested}")


@app.command()
def clean(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
    output: str = typer.Option(..., "--output", "-o", help="Tozalangan fayl nomi"),
    strategy: str = typer.Option("auto", "--strategy", "-s", help="Missing values strategiyasi: auto, mean, median, mode, drop"),
):
    """
    🧹 Data tozalash (dublikatlar, missing values, outliers).

    Misol: datamind clean sales.csv -o cleaned.csv
    """
    from datamind.agents import CleaningAgent

    console.print(Panel.fit(
        "[bold cyan]🧹 DataMind[/bold cyan] - Data Cleaning",
        border_style="cyan"
    ))

    # Load data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Data yuklanmoqda...", total=None)

        try:
            loader = DataLoader(file_path)
            df = loader.load()
            progress.update(task, description="✅ Data yuklandi!")
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")
            raise typer.Exit(1)

    # Clean
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🧹 Tozalanmoqda...", total=None)

        agent = CleaningAgent(df)
        agent.remove_duplicates()
        agent.fix_inconsistencies()
        agent.fill_missing(strategy=strategy)
        agent.handle_outliers(strategy='clip')

        cleaned_df = agent.get_result()
        report = agent.get_report_dict()

        progress.update(task, description="✅ Tozalandi!")

    # Show report
    console.print(f"\n[bold cyan]📋 Tozalash Hisoboti:[/bold cyan]")
    console.print(f"   Asl: {report['original_shape']}")
    console.print(f"   Natija: {report['final_shape']}")

    if report['duplicates_removed'] > 0:
        console.print(f"   [green]✓[/green] {report['duplicates_removed']} dublikat o'chirildi")

    if report['missing_filled']:
        for col, count in report['missing_filled'].items():
            console.print(f"   [green]✓[/green] {col}: {count} bo'sh qiymat to'ldirildi")

    if report['outliers_handled']:
        for col, count in report['outliers_handled'].items():
            console.print(f"   [green]✓[/green] {col}: {count} outlier tuzatildi")

    # Save
    output_path = Path(output)
    if output_path.suffix == '.csv':
        cleaned_df.to_csv(output, index=False)
    elif output_path.suffix in ['.xlsx', '.xls']:
        cleaned_df.to_excel(output, index=False)
    else:
        cleaned_df.to_csv(output, index=False)

    console.print(f"\n[bold green]✅ Saqlandi:[/bold green] {output}")


@app.command()
def fix(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
    output: str = typer.Option(..., "--output", "-o", help="Tuzatilgan fayl nomi"),
):
    """
    🔧 AI bilan avtomatik data tuzatish.

    Misol: datamind fix sales.csv -o fixed.csv
    """
    from datamind.agents import AutoFixAgent

    console.print(Panel.fit(
        "[bold cyan]🔧 DataMind[/bold cyan] - AI Auto-Fix",
        border_style="cyan"
    ))

    # Load data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Data yuklanmoqda...", total=None)

        try:
            loader = DataLoader(file_path)
            df = loader.load()
            progress.update(task, description="✅ Data yuklandi!")
        except Exception as e:
            console.print(f"[red]❌ Xato: {e}[/red]")
            raise typer.Exit(1)

    # Auto-fix
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔧 AI tuzatmoqda...", total=None)

        agent = AutoFixAgent(df, use_ai=True)
        agent.auto_fix()
        fixed_df = agent.get_result()
        report = agent.get_report_dict()
        comparison = agent.compare()

        progress.update(task, description="✅ Tuzatildi!")

    # Show comparison
    console.print(f"\n[bold cyan]📊 Solishtirma:[/bold cyan]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("")
    table.add_column("Oldin", style="red")
    table.add_column("Keyin", style="green")
    table.add_row("Qatorlar", str(comparison['original']['rows']), str(comparison['fixed']['rows']))
    table.add_row("Bo'sh qiymatlar", str(comparison['original']['missing']), str(comparison['fixed']['missing']))
    table.add_row("Dublikatlar", str(comparison['original']['duplicates']), str(comparison['fixed']['duplicates']))
    console.print(table)

    # Show actions
    if report['fixes_applied']:
        console.print(f"\n[bold green]✅ Bajarilgan amallar:[/bold green]")
        for fix in report['fixes_applied']:
            console.print(f"   • {fix['action']}")

    # Get AI recommendations
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🤖 AI tavsiyalar...", total=None)
        try:
            recommendations = agent.get_ai_recommendations()
            progress.update(task, description="✅ Tavsiyalar tayyor!")

            if recommendations and recommendations[0] != "AI analyzer not available":
                console.print(f"\n[bold cyan]💡 AI Tavsiyalari:[/bold cyan]")
                for rec in recommendations:
                    if rec.strip():
                        console.print(f"   • {rec}")
        except:
            pass

    # Save
    output_path = Path(output)
    if output_path.suffix == '.csv':
        fixed_df.to_csv(output, index=False)
    elif output_path.suffix in ['.xlsx', '.xls']:
        fixed_df.to_excel(output, index=False)
    else:
        fixed_df.to_csv(output, index=False)

    console.print(f"\n[bold green]✅ Saqlandi:[/bold green] {output}")


@app.command()
def validate(
    file_path: str = typer.Argument(..., help="Data fayl yo'li"),
):
    """
    ✅ Data validatsiya qilish.

    Misol: datamind validate sales.csv
    """
    from datamind.agents import ValidatorAgent

    console.print(Panel.fit(
        "[bold cyan]✅ DataMind[/bold cyan] - Data Validation",
        border_style="cyan"
    ))

    # Load data
    try:
        loader = DataLoader(file_path)
        df = loader.load()
    except Exception as e:
        console.print(f"[red]❌ Xato: {e}[/red]")
        raise typer.Exit(1)

    # Validate
    agent = ValidatorAgent(df)
    agent.run_all_checks()
    report = agent.get_report_dict()

    # Show score
    score = report['score']
    color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    console.print(f"\n[bold]📊 Validatsiya Bali:[/bold] [{color}]{score}/100[/{color}]")

    # Show results
    console.print(f"\n[bold cyan]📋 Natijalar:[/bold cyan]")
    console.print(f"   Jami tekshiruvlar: {report['total_checks']}")
    console.print(f"   [green]✓ O'tdi:[/green] {report['passed']}")
    console.print(f"   [red]✗ O'tmadi:[/red] {report['failed']}")
    console.print(f"   [yellow]⚠ Ogohlantirishlar:[/yellow] {report['warnings']}")

    # Show details
    if report['failed'] > 0 or report['warnings'] > 0:
        console.print(f"\n[bold]Tafsilotlar:[/bold]")
        for result in report['results']:
            if not result['passed']:
                icon = "❌" if result['level'] == 'error' else "⚠️"
                console.print(f"   {icon} {result['message']}")


@app.command()
def version():
    """Versiya ma'lumotlari."""
    from datamind import __version__
    console.print(f"[bold cyan]DataMind AI[/bold cyan] v{__version__}")
    console.print("\n[bold]Muallif:[/bold] Saidjon Ravshanov")
    console.print("[bold]GitHub:[/bold] https://github.com/SaidjonRavshanov")
    console.print("[bold]Loyiha:[/bold] https://github.com/SaidjonRavshanov/datamind")
    console.print("\n[dim]Buyruqlar:[/dim]")
    console.print("  chat     - Interaktiv rejim")
    console.print("  analyze  - Data tahlil va dashboard")
    console.print("  query    - AI ga savol berish")
    console.print("  diagnose - Data muammolarini aniqlash")
    console.print("  clean    - Data tozalash")
    console.print("  fix      - AI avtomatik tuzatish")
    console.print("  validate - Data validatsiya")
    console.print("  info     - Data haqida ma'lumot")


if __name__ == "__main__":
    app()
