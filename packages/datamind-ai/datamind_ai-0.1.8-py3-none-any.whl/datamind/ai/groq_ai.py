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

    def auto_analyze(self, file_path: str) -> dict:
        """
        Fully autonomous analysis - agent decides what to do.
        Returns dict with: df, code_history, insights, summary
        """
        results = {
            'df': None,
            'code_history': [],
            'insights': [],
            'summary': '',
            'charts_data': []
        }

        # Step 1: Load and explore data
        explore_prompt = f"""
Fayl: {file_path}

1-QADAM: Faylni yukla va struktura ko'r.
Kod yoz:
- pd.read_csv() bilan yukla (katta fayl bo'lsa nrows=10000 ishlatish mumkin)
- df.shape, df.dtypes, df.head() ko'r
- result = df qil
"""
        try:
            code1 = self.generate_code(explore_prompt, file_path)
            local_vars = {'pd': pd, 'file_path': file_path}
            exec(code1, {'__builtins__': {'print': print, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict}}, local_vars)
            df = local_vars.get('result', local_vars.get('df'))
            results['df'] = df
            results['code_history'].append(('Yuklash', code1))
        except Exception as e:
            results['insights'].append(f"Yuklash xatosi: {e}")
            return results

        # Step 2: Get AI analysis plan
        df_info = {
            'columns': list(df.columns),
            'shape': df.shape,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'sample': df.head(5).to_string(),
            'missing': df.isnull().sum().to_dict(),
            'numeric_cols': list(df.select_dtypes(include=['number']).columns),
            'cat_cols': list(df.select_dtypes(include=['object']).columns)
        }

        plan_prompt = f"""
Sen data analyst agent san. Quyidagi data haqida tahlil reja tuz.

DATA INFO:
- Shape: {df_info['shape']}
- Ustunlar: {df_info['columns']}
- Raqamli ustunlar: {df_info['numeric_cols']}
- Kategorik ustunlar: {df_info['cat_cols']}
- Bo'sh qiymatlar: {df_info['missing']}

SAMPLE:
{df_info['sample']}

Quyidagi JSON formatda javob ber:
{{
    "summary": "Data haqida 1-2 gap",
    "analysis_steps": [
        {{"name": "Statistika", "code": "result = df.describe()"}},
        {{"name": "Top qiymatlar", "code": "result = df['ustun'].value_counts().head(10)"}}
    ],
    "insights": ["topilma 1", "topilma 2"],
    "chart_suggestions": [
        {{"type": "bar", "x": "ustun1", "y": "ustun2", "title": "Sarlavha"}}
    ]
}}

FAQAT JSON qaytar!
"""
        try:
            plan_response = self._chat(plan_prompt).strip()
            if '```json' in plan_response:
                plan_response = plan_response.split('```json')[1].split('```')[0]
            elif '```' in plan_response:
                plan_response = plan_response.split('```')[1].split('```')[0]

            plan = json.loads(plan_response.strip())
            results['summary'] = plan.get('summary', '')
            results['insights'] = plan.get('insights', [])
            results['charts_data'] = plan.get('chart_suggestions', [])

            # Step 3: Execute analysis steps
            for step in plan.get('analysis_steps', [])[:5]:  # Max 5 steps
                try:
                    step_code = step.get('code', '')
                    if step_code:
                        local_vars = {'pd': pd, 'df': df}
                        exec(step_code, {'__builtins__': {'print': print, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict, 'sum': sum, 'min': min, 'max': max}}, local_vars)
                        results['code_history'].append((step.get('name', 'Tahlil'), step_code))
                except:
                    pass

        except json.JSONDecodeError:
            results['insights'].append("AI rejani parse qilib bo'lmadi")
        except Exception as e:
            results['insights'].append(f"Tahlil xatosi: {str(e)}")

        return results
