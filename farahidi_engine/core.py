import os
import json
import sqlite3
import google.generativeai as genai

DB_FILE = "arabic_lexicon.db"

def init_farahidi(api_key: str):
    genai.configure(api_key=api_key)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionary (
        word TEXT PRIMARY KEY,
        root TEXT,
        definition TEXT,
        synonyms TEXT,
        antonyms TEXT,
        register TEXT,
        source TEXT
    )
    """)
    conn.commit()
    conn.close()

def _fetch_gemini(prompt: str) -> dict:
    try:
        model = genai.GenerativeModel("gemini-3.6-flash")
        res = model.generate_content(prompt, generation_config={"temperature": 0.2})
        text = res.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def lookup(word: str) -> dict:
    word = word.strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dictionary WHERE word = ?", (word,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "word": row[0], "root": row[1], "definition": row[2],
            "synonyms": json.loads(row[3]), "antonyms": json.loads(row[4]),
            "register": row[5], "source": "محلي (موثق)"
        }
        
    prompt = f'أنت معجم عربي موثق. حلل كلمة "{word}" ورد بصيغة JSON فقط: definition, root, synonyms, antonyms, register'
    data = _fetch_gemini(prompt)
    if "error" not in data:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO dictionary VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (word, data.get("root", ""), data.get("definition", ""), 
                        json.dumps(data.get("synonyms", []), ensure_ascii=False),
                        json.dumps(data.get("antonyms", []), ensure_ascii=False),
                        data.get("register", "عام"), "Gemini (تم الحفظ)"))
        conn.commit()
        conn.close()
        data["word"] = word
        data["source"] = "Gemini AI"
    return data

def enhance_text(text: str) -> dict:
    prompt = f'حسّن النص العربي التالي مع الحفاظ على المعنى. رد بصيغة JSON تحوي: original, enhanced, changes, explanation\nالنص: "{text}"'
    return _fetch_gemini(prompt)
