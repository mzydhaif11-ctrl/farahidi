# Farahidi Engine — محرك الفراهيدي

محرك لغوي عربي هجين مفتوح المصدر يجمع بين التخزين المحلي (SQLite) واستدعاءات الذكاء الاصطناعي (Gemini AI).

## التثبيت
```bash
pip install farahidi-engine
```

## الاستخدام
```python
import farahidi_engine as fe
fe.init_farahidi(api_key='YOUR_API_KEY')
print(fe.lookup('اليعسوب'))
```
