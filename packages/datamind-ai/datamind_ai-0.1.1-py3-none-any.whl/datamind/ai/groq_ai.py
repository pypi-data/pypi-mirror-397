"""Groq AI integration for data analysis."""

import os
import json
from typing import Optional
from groq import Groq
import pandas as pd


class GroqAnalyzer:
    """AI-powered data analyzer using Groq (free & fast)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY topilmadi!\n"
                "1. https://console.groq.com dan API key oling (BEPUL)\n"
                "2. export GROQ_API_KEY='your-key' buyrug'ini ishga tushiring"
            )
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def _chat(self, prompt: str) -> str:
        """Send a chat request to Groq."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content

    def analyze_data(self, df: pd.DataFrame, info: dict) -> dict:
        """Analyze data and suggest visualizations."""

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
            "type": "bar",
            "title": "Mahsulotlar bo'yicha sotuvlar",
            "x_column": "product",
            "y_column": "sales",
            "reason": "Mahsulotlarni solishtirish uchun"
        }},
        {{
            "type": "pie",
            "title": "Kategoriyalar ulushi",
            "x_column": "category",
            "y_column": "sales",
            "reason": "Kategoriyalar taqsimotini ko'rsatish"
        }},
        {{
            "type": "line",
            "title": "Vaqt bo'yicha trend",
            "x_column": "date",
            "y_column": "sales",
            "reason": "Vaqt bo'yicha o'zgarishni ko'rsatish"
        }}
    ],
    "data_quality": {{
        "score": 8,
        "issues": ["muammo bo'lsa yozing"]
    }},
    "recommended_actions": ["tavsiya 1", "tavsiya 2"]
}}

MUHIM:
- suggested_charts da x_column va y_column FAQAT mavjud ustun nomlaridan bo'lsin: {info['column_names']}
- type faqat: bar, line, pie, scatter, histogram bo'lishi mumkin
- FAQAT JSON qaytar, boshqa hech narsa yo'q!
"""

        try:
            result_text = self._chat(prompt).strip()

            # Clean JSON from markdown code blocks
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            result_text = result_text.strip()

            return json.loads(result_text)
        except json.JSONDecodeError as e:
            return {
                "summary": "AI tahlil natijasini parse qilib bo'lmadi",
                "insights": [],
                "suggested_charts": [],
                "data_quality": {"score": 0, "issues": [f"JSON xatosi: {str(e)}"]},
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
O'zbek tilida javob ber.
"""

        try:
            return self._chat(prompt).strip()
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"
