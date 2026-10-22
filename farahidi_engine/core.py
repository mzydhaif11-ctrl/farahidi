"""
Farahidi Engine v0.4.0 — محرك لغوي عربي محلي بالكامل
بدون أي API Key خارجي 🔒🇸🇦
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


# ═══════ إعدادات ═══════

GENERATIVE_MODEL = os.getenv(
    "ARABIC_GENERATIVE_MODEL",
    "CohereForAI/aya-23-8b"
)
DB_FILE = os.getenv("FARAHIDI_DB", "arabic_lexicon.db")


_engine_state = {"tokenizer": None, "model": None}


def _load_model():
    if _engine_state["model"] is not None:
        return _engine_state["tokenizer"], _engine_state["model"]
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        _engine_state["tokenizer"] = AutoTokenizer.from_pretrained(GENERATIVE_MODEL)
        _engine_state["model"] = AutoModelForCausalLM.from_pretrained(GENERATIVE_MODEL)
    except ImportError:
        raise RuntimeError("pip install transformers torch accelerate sentencepiece")
    return _engine_state["tokenizer"], _engine_state["model"]


def _generate(prompt: str) -> dict:
    tokenizer, model = _load_model()
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=500, do_sample=True, temperature=0.2, top_p=0.9)
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated = full_text[len(prompt):].strip()
        if "```json" in generated:
            generated = generated.split("```json")[1].split("```")[0].strip()
        elif "```" in generated:
            generated = generated.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(generated)
        except json.JSONDecodeError:
            return {"raw_response": generated}
    except Exception as e:
        return {"error": str(e)}


# ═══════ SQLite ═══════

def _get_conn():
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            word TEXT PRIMARY KEY, root TEXT, definition TEXT,
            synonyms TEXT, antonyms TEXT, register TEXT, source TEXT
        )
    """)
    conn.commit()
    return conn


# ═══════ Public API ═══════

def init_farahidi(api_key=None):
    """تهيئة المحرك — api_key لم تعد مطلوبة."""
    if api_key:
        logger.warning("api_key deprecated — engine runs locally")
    _get_conn()
    logger.info(f"Farahidi Engine v0.4.0 | Model: {GENERATIVE_MODEL}")


def lookup(word: str) -> dict:
    """بحث عن كلمة عربية."""
    word = word.strip()
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dictionary WHERE word = ?", (word,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "word": row[0], "root": row[1], "definition": row[2],
            "synonyms": json.loads(row[3]) if row[3] else [],
            "antonyms": json.loads(row[4]) if row[4] else [],
            "register": row[5], "source": "محلي (موثق)",
        }

    prompt = f'أنت معجم عربي موثق متخصص. حلل كلمة "{word}" ورد بصيغة JSON فقط تحتوي على: definition, root, synonyms, antonyms, register\n\nرد:'
    data = _generate(prompt)

    if "error" not in data:
        conn = _get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO dictionary VALUES (?, ?, ?, ?, ?, ?, ?)",
            (word, data.get("root", ""), data.get("definition", ""),
             json.dumps(data.get("synonyms", []), ensure_ascii=False),
             json.dumps(data.get("antonyms", []), ensure_ascii=False),
             data.get("register", "عام"), "محلي AI"),
        )
        conn.commit()
        conn.close()
        data["word"] = word
        data["source"] = "محلي AI"

    return data


def enhance_text(text: str) -> dict:
    """تحسين نص عربي بالنموذج المحلي."""
    prompt = f'حسّن النص العربي التالي مع الحفاظ على المعنى. رد بصيغة JSON تحوي: original, enhanced, changes (قائمة), explanation\n\nالنص: "{text}"\n\nرد:'
    return _generate(prompt)


# ═══════ CLI ═══════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    init_farahidi()
    print("\n🌊 Farahidi Engine v0.4.0 — محلي بالكامل")
    print("=" * 50)
    print("اكتب كلمة (أو 'exit' للخروج)\n")
    while True:
        try:
            user_input = input("❓ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 وداعا!")
            break
        if user_input.lower() in ("exit", "quit", "خروج"):
            print("👋 وداعا!")
            break
        if not user_input:
            continue
        result = lookup(user_input)
        if "error" in result:
            print(f"\n❌ خطأ: {result['error']}")
        else:
            print(f"\n📖 {result.get('word', user_input)}:")
            print(f"   التعريف: {result.get('definition', 'غير متوفر')}")
            print(f"   الجذر: {result.get('root', 'غير متوفر')}")
            print(f"   المرادفات: {result.get('synonyms', [])}")
            print(f"   المصدر: {result.get('source', 'غير معروف')}")
        print()
