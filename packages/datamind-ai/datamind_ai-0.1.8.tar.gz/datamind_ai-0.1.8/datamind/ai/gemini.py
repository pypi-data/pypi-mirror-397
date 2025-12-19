"""Gemini AI integration for data analysis."""

import os
import json
from typing import Optional
import google.generativeai as genai
import pandas as pd


class GeminiAnalyzer:
    """AI-powered data analyzer using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY topilmadi!\n"
                "1. https://makersuite.google.com/app/apikey dan API key oling\n"
                "2. export GEMINI_API_KEY='your-key' buyrug'ini ishga tushiring"
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_data(self, df: pd.DataFrame, info: dict) -> dict:
        """Analyze data and suggest visualizations."""

        # Prepare data summary for AI
        sample_data = df.head(10).to_string()

        prompt = f"""
Sen data analyst AI san. Quyidagi ma'lumotlarni tahlil qil va JSON formatda javob ber.

DATA INFO:
- Qatorlar soni: {info['rows']}
- Ustunlar: {info['column_names']}
- Data turlari: {info['dtypes']}
- Bo'sh qiymatlar: {info['missing_values']}

SAMPLE DATA:
{sample_data}

Quyidagilarni JSON formatda qaytar:
{{
    "summary": "Ma'lumotlar haqida qisqa tavsif (2-3 gap)",
    "insights": ["muhim topilma 1", "muhim topilma 2", "muhim topilma 3"],
    "suggested_charts": [
        {{
            "type": "bar|line|pie|scatter|heatmap",
            "title": "Chart nomi",
            "x_column": "x o'qi uchun ustun",
            "y_column": "y o'qi uchun ustun",
            "reason": "Nima uchun bu chart mos"
        }}
    ],
    "data_quality": {{
        "score": 1-10 ball,
        "issues": ["muammo 1", "muammo 2"]
    }},
    "recommended_actions": ["tavsiya 1", "tavsiya 2"]
}}

FAQAT JSON qaytar, boshqa hech narsa yo'q.
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean JSON from markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            result_text = result_text.strip()

            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "summary": "AI tahlil natijasini parse qilib bo'lmadi",
                "insights": [],
                "suggested_charts": [],
                "data_quality": {"score": 0, "issues": ["AI javobini o'qib bo'lmadi"]},
                "recommended_actions": []
            }
        except Exception as e:
            return {
                "summary": f"AI xatosi: {str(e)}",
                "insights": [],
                "suggested_charts": [],
                "data_quality": {"score": 0, "issues": [str(e)]},
                "recommended_actions": []
            }

    def ask_question(self, df: pd.DataFrame, question: str) -> str:
        """Ask a natural language question about the data."""

        sample_data = df.head(20).to_string()
        stats = df.describe().to_string()

        prompt = f"""
Sen data analyst AI san. Quyidagi ma'lumotlar asosida savolga javob ber.

DATA (birinchi 20 qator):
{sample_data}

STATISTIKA:
{stats}

USTUNLAR: {list(df.columns)}

SAVOL: {question}

Qisqa va aniq javob ber. Agar kerak bo'lsa, raqamlar va statistikalarni ko'rsat.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"

    def suggest_cleaning(self, df: pd.DataFrame, info: dict) -> dict:
        """Suggest data cleaning operations."""

        prompt = f"""
Data cleaning tavsiyalari ber. JSON formatda javob qaytar.

DATA INFO:
- Qatorlar: {info['rows']}
- Ustunlar: {info['column_names']}
- Data turlari: {info['dtypes']}
- Bo'sh qiymatlar: {info['missing_values']}

JSON format:
{{
    "cleaning_steps": [
        {{
            "column": "ustun nomi",
            "action": "fill_mean|fill_median|fill_mode|drop_rows|drop_column|convert_type",
            "reason": "sabab"
        }}
    ],
    "overall_recommendation": "umumiy tavsiya"
}}

FAQAT JSON qaytar.
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            result_text = result_text.strip()

            return json.loads(result_text)
        except:
            return {
                "cleaning_steps": [],
                "overall_recommendation": "Avtomatik tavsiya berib bo'lmadi"
            }
