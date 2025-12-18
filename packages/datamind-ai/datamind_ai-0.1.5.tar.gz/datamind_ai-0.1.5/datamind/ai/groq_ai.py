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

    def chat(self, message: str) -> str:
        """General chat without data context."""
        prompt = f"""
Sen DataMind AI yordamchisi san. Data analitika, Python, dasturlash va umumiy savolarga javob berasan.

MUHIM MA'LUMOT:
- DataMind dasturini Saidjon Ravshanov yaratgan
- GitHub: https://github.com/SaidjonRavshanov
- Loyiha: https://github.com/SaidjonRavshanov/datamind
- Bu data analitika uchun AI-powered CLI tool

Agar "kim yaratgan", "kim dasturlagan", "muallif kim", "author" kabi savollar bo'lsa:
- Javob: "DataMind dasturini Saidjon Ravshanov yaratgan. GitHub: https://github.com/SaidjonRavshanov"

O'zbek tilida javob ber. Qisqa va aniq bo'l.

Savol: {message}
"""
        try:
            return self._chat(prompt).strip()
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}"

    def generate_code(self, task: str, file_path: str = None, df_info: dict = None) -> str:
        """Generate Python code for a data task."""
        context = ""
        if file_path:
            context += f"Fayl: {file_path}\n"
        if df_info:
            context += f"Ustunlar: {df_info.get('column_names', [])}\n"
            context += f"Qatorlar soni: {df_info.get('rows', 'noma`lum')}\n"
            context += f"Data turlari: {df_info.get('dtypes', {})}\n"

        prompt = f"""
Sen Python data analyst san. Vazifani bajarish uchun Python kod yoz.

{context}

VAZIFA: {task}

QOIDALAR:
1. FAQAT Python kod yoz, boshqa hech narsa yo'q
2. Kod ```python va ``` orasida bo'lsin
3. pandas importi: import pandas as pd
4. Fayl yuklash: pd.read_csv(file_path, nrows=N) - katta fayllar uchun nrows ishlatish kerak
5. Natijani result o'zgaruvchisiga saqla
6. print() ishlatma, faqat result = ... qil

MISOL:
```python
import pandas as pd
df = pd.read_csv("{file_path or 'data.csv'}", nrows=90000)
result = df.head()
```
"""
        try:
            response = self._chat(prompt).strip()
            # Extract code from response
            if '```python' in response:
                code = response.split('```python')[1].split('```')[0]
            elif '```' in response:
                code = response.split('```')[1].split('```')[0]
            else:
                code = response
            return code.strip()
        except Exception as e:
            return f"# Xato: {str(e)}"

    def execute_task(self, task: str, file_path: str = None, df: pd.DataFrame = None) -> tuple:
        """Generate and execute code for a task. Returns (result, code)."""
        df_info = None
        if df is not None:
            df_info = {
                'column_names': list(df.columns),
                'rows': len(df),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }

        # Generate code
        code = self.generate_code(task, file_path, df_info)

        # Execute code safely
        try:
            local_vars = {'pd': pd, 'df': df, 'file_path': file_path}
            exec(code, {'__builtins__': {'print': print, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict, 'range': range, 'sum': sum, 'min': min, 'max': max, 'sorted': sorted, 'abs': abs, 'round': round}}, local_vars)
            result = local_vars.get('result', local_vars.get('df', 'Natija topilmadi'))
            return result, code
        except Exception as e:
            return f"Xato: {str(e)}", code
