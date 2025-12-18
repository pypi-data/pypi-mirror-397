"""Dashboard HTML generator."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import numpy as np
import plotly.graph_objects as go
from jinja2 import Template


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


class DashboardGenerator:
    """Generate HTML dashboards from charts and analysis."""

    TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - DataMind Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e4e4e4;
        }

        .header {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header h1 {
            font-size: 24px;
            font-weight: 600;
            color: #fff;
        }

        .header .subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 5px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }

        .summary-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .summary-section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #4ecdc4;
        }

        .summary-text {
            line-height: 1.7;
            color: #ccc;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .metric-label {
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #4ecdc4;
            margin-top: 5px;
        }

        .insights-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .insights-section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #ff6b6b;
        }

        .insight-item {
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #4ecdc4;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chart-container {
            width: 100%;
            min-height: 400px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 12px;
        }

        .footer a {
            color: #4ecdc4;
            text-decoration: none;
        }

        .quality-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .quality-good { background: #27ae60; color: white; }
        .quality-medium { background: #f39c12; color: white; }
        .quality-poor { background: #e74c3c; color: white; }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="subtitle">Yaratilgan: {{ generated_at }} | DataMind AI Dashboard</div>
    </div>

    <div class="container">
        <!-- Summary Section -->
        <div class="summary-section">
            <h2>📊 Ma'lumotlar Xulosasi</h2>
            <p class="summary-text">{{ summary }}</p>
        </div>

        <!-- Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Qatorlar</div>
                <div class="metric-value">{{ rows | default(0) }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Ustunlar</div>
                <div class="metric-value">{{ columns | default(0) }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Data Sifati</div>
                <div class="metric-value">
                    <span class="quality-badge {% if quality_score >= 7 %}quality-good{% elif quality_score >= 4 %}quality-medium{% else %}quality-poor{% endif %}">
                        {{ quality_score }}/10
                    </span>
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Chartlar</div>
                <div class="metric-value">{{ chart_count }}</div>
            </div>
        </div>

        <!-- Insights -->
        {% if insights %}
        <div class="insights-section">
            <h2>💡 Muhim Topilmalar</h2>
            {% for insight in insights %}
            <div class="insight-item">{{ insight }}</div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- Charts -->
        <div class="charts-grid">
            {% for chart in charts %}
            <div class="chart-card">
                <div id="chart-{{ loop.index }}" class="chart-container"></div>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="footer">
        <p>Powered by <a href="#">DataMind</a> - AI-powered Data Analytics</p>
    </div>

    <script>
        // Render charts
        {% for chart in charts %}
        Plotly.newPlot('chart-{{ loop.index }}', {{ chart.data | safe }}, {{ chart.layout | safe }}, {responsive: true});
        {% endfor %}
    </script>
</body>
</html>
"""

    def __init__(
        self,
        title: str = "Data Analysis Report",
        analysis: Optional[dict] = None,
        info: Optional[dict] = None,
    ):
        self.title = title
        self.analysis = analysis or {}
        self.info = info or {}
        self.charts: list[go.Figure] = []

    def add_chart(self, fig: go.Figure):
        """Add a chart to the dashboard."""
        self.charts.append(fig)

    def add_charts(self, figs: list[go.Figure]):
        """Add multiple charts."""
        self.charts.extend(figs)

    def generate(self, output_path: str) -> str:
        """Generate HTML dashboard and save to file."""

        # Prepare chart data for template
        charts_data = []
        for fig in self.charts:
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e4e4e4',
            )
            charts_data.append({
                'data': json.dumps([trace.to_plotly_json() for trace in fig.data], cls=NumpyEncoder),
                'layout': json.dumps(fig.layout.to_plotly_json(), cls=NumpyEncoder),
            })

        # Render template
        template = Template(self.TEMPLATE)
        html_content = template.render(
            title=self.title,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            summary=self.analysis.get('summary', 'Tahlil mavjud emas'),
            rows=self.info.get('rows', 0),
            columns=self.info.get('columns', 0),
            quality_score=self.analysis.get('data_quality', {}).get('score', 0),
            chart_count=len(self.charts),
            insights=self.analysis.get('insights', []),
            charts=charts_data,
        )

        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')

        return str(output_file.absolute())
