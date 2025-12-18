# DataMind AI

AI-powered data analysis, cleaning, and dashboard generator CLI tool.

## O'rnatish

```bash
pip install datamind-ai
```

## API Key olish (bepul)

Groq dan API key oling: https://console.groq.com

```bash
export GROQ_API_KEY='sizning-api-key'
```

## Ishlatish

### Interaktiv rejim (tavsiya etiladi)

```bash
datamind chat
```

```
load data.csv
diagnose
fix
dashboard qilib ber
qaysi mahsulot eng ko'p sotilgan?
exit
```

### Buyruqlar

```bash
# Data tahlil va dashboard
datamind analyze data.csv -o report.html

# Muammolarni aniqlash
datamind diagnose data.csv

# AI avtomatik tuzatish
datamind fix data.csv -o cleaned.csv

# Data tozalash
datamind clean data.csv -o cleaned.csv

# Validatsiya
datamind validate data.csv

# AI ga savol
datamind query data.csv "eng ko'p sotilgan mahsulot?"

# Ma'lumot
datamind info data.csv
```

## Imkoniyatlar

- CSV, Excel, JSON fayllarni yuklash
- AI bilan avtomatik data tahlil
- Dublikatlarni o'chirish
- Bo'sh qiymatlarni to'ldirish
- Outlierlarni tuzatish
- Interaktiv HTML dashboard yaratish
- Natural language bilan ishlash

## Litsenziya

MIT
