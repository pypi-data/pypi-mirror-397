# DataMind AI

AI-powered data analysis, cleaning, and dashboard generator CLI tool.

## O'rnatish

```bash
pip install datamind-ai
```

## Ishga tushirish

```bash
datamind chat
```

## API Sozlash

Dastur ishga tushganda API tanlash so'raladi:

```
API tanlang:
  1. Mavjud API bilan (parol kerak)
  2. O'z API keyingiz bilan
  3. API keysiz davom etish

Tanlang [1/2/3]: 1
Parol kiriting: ****
```

**Parol:** `datamind2024`

Yoki o'z API keyingizni oling: https://console.groq.com (bepul)

## Ishlatish

### Interaktiv rejim

```bash
datamind chat
```

```
load data.csv          # Fayl yuklash
diagnose               # Muammolarni aniqlash
fix                    # AI avtomatik tuzatish
dashboard              # Dashboard yaratish
agent sales.csv        # Avtomatik tahlil
qaysi mahsulot eng ko'p sotilgan?  # AI ga savol
exit                   # Chiqish
```

### Buyruq qatori

```bash
datamind analyze data.csv -o report.html   # Dashboard
datamind diagnose data.csv                  # Muammolarni aniqlash
datamind fix data.csv -o cleaned.csv        # AI tuzatish
datamind clean data.csv -o cleaned.csv      # Tozalash
datamind validate data.csv                  # Validatsiya
datamind query data.csv "eng ko'p sotilgan?" # AI savol
datamind info data.csv                      # Ma'lumot
```

## Agent rejimi

Agent o'zi fikrlab ishlaydi - kod yozadi va bajaradi:

```
datamind: agent sales.csv

🤖 Agent ishga tushdi...
✅ Yuklandi: 50000 qator x 6 ustun

📝 Bajarilgan kodlar:
import pandas as pd
df = pd.read_csv("sales.csv")
result = df.describe()

💡 Topilmalar:
  1. Eng ko'p sotilgan: Electronics
  2. O'rtacha sotuv: $245
```

## Imkoniyatlar

- CSV, Excel, JSON fayllarni yuklash
- AI bilan avtomatik data tahlil
- Dublikatlarni o'chirish
- Bo'sh qiymatlarni to'ldirish
- Outlierlarni tuzatish
- Interaktiv HTML dashboard yaratish
- Natural language bilan ishlash (o'zbek/ingliz)
- Agent rejimi - AI o'zi kod yozib bajaradi

## To'liq qo'llanma

[docs/GUIDE.md](docs/GUIDE.md) - batafsil dokumentatsiya

## Muallif

**Saidjon Ravshanov**
- GitHub: https://github.com/SaidjonRavshanov
- Loyiha: https://github.com/SaidjonRavshanov/datamind

## Litsenziya

MIT
