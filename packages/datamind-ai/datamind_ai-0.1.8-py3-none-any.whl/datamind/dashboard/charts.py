"""Chart generation using Plotly."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional


class ChartGenerator:
    """Generate interactive charts using Plotly."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_chart(
        self,
        chart_type: str,
        x_column: str,
        y_column: Optional[str] = None,
        title: str = "",
        color_column: Optional[str] = None,
    ) -> go.Figure:
        """Create a chart based on type."""

        chart_methods = {
            'bar': self._bar_chart,
            'line': self._line_chart,
            'pie': self._pie_chart,
            'scatter': self._scatter_chart,
            'histogram': self._histogram,
            'box': self._box_chart,
            'heatmap': self._heatmap,
        }

        if chart_type not in chart_methods:
            raise ValueError(f"Noma'lum chart turi: {chart_type}")

        return chart_methods[chart_type](
            x_column=x_column,
            y_column=y_column,
            title=title,
            color_column=color_column,
        )

    def _bar_chart(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create bar chart."""
        if y_column:
            fig = px.bar(
                self.df,
                x=x_column,
                y=y_column,
                title=title,
                color=color_column,
            )
        else:
            # Count values if no y column
            counts = self.df[x_column].value_counts().reset_index()
            counts.columns = [x_column, 'count']
            fig = px.bar(counts, x=x_column, y='count', title=title)

        fig.update_layout(template='plotly_white')
        return fig

    def _line_chart(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create line chart."""
        fig = px.line(
            self.df,
            x=x_column,
            y=y_column,
            title=title,
            color=color_column,
            markers=True,
        )
        fig.update_layout(template='plotly_white')
        return fig

    def _pie_chart(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create pie chart."""
        if y_column:
            fig = px.pie(
                self.df,
                names=x_column,
                values=y_column,
                title=title,
            )
        else:
            counts = self.df[x_column].value_counts().reset_index()
            counts.columns = [x_column, 'count']
            fig = px.pie(counts, names=x_column, values='count', title=title)

        fig.update_layout(template='plotly_white')
        return fig

    def _scatter_chart(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create scatter plot."""
        fig = px.scatter(
            self.df,
            x=x_column,
            y=y_column,
            title=title,
            color=color_column,
        )
        fig.update_layout(template='plotly_white')
        return fig

    def _histogram(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create histogram."""
        fig = px.histogram(
            self.df,
            x=x_column,
            title=title,
            color=color_column,
        )
        fig.update_layout(template='plotly_white')
        return fig

    def _box_chart(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create box plot."""
        fig = px.box(
            self.df,
            x=x_column,
            y=y_column,
            title=title,
            color=color_column,
        )
        fig.update_layout(template='plotly_white')
        return fig

    def _heatmap(
        self,
        x_column: str,
        y_column: Optional[str],
        title: str,
        color_column: Optional[str],
    ) -> go.Figure:
        """Create correlation heatmap."""
        numeric_df = self.df.select_dtypes(include=['number'])
        corr_matrix = numeric_df.corr()

        fig = px.imshow(
            corr_matrix,
            title=title or "Correlation Heatmap",
            color_continuous_scale='RdBu_r',
            aspect='auto',
        )
        fig.update_layout(template='plotly_white')
        return fig

    def auto_charts(self, suggestions: list[dict]) -> list[go.Figure]:
        """Generate charts from AI suggestions."""
        charts = []

        for suggestion in suggestions:
            try:
                chart = self.create_chart(
                    chart_type=suggestion.get('type', 'bar'),
                    x_column=suggestion.get('x_column', self.df.columns[0]),
                    y_column=suggestion.get('y_column'),
                    title=suggestion.get('title', ''),
                )
                charts.append(chart)
            except Exception as e:
                print(f"Chart yaratishda xato: {e}")
                continue

        return charts
