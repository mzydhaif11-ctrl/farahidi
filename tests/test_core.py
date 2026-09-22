import unittest
import sqlite3
import farahidi_engine as fe

class TestFarahidiEngine(unittest.TestCase):
    def setUp(self):
        # تهيئة المحرك بمفتاح وهمي لاختبار التخزين المحلي فقط
        fe.init_farahidi(api_key="TEST_API_KEY")
        
        # حقن كلمة في قاعدة البيانات المحلية يدوياً للاختبار
        conn = sqlite3.connect("arabic_lexicon.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS lexicon 
                     (word TEXT PRIMARY KEY, root TEXT, meaning TEXT, synonyms TEXT, context TEXT)''')
        c.execute("INSERT OR REPLACE INTO lexicon VALUES ('اختبار', 'خ-ب-ر', 'تجربة', 'فحص', 'رسمي')")
        conn.commit()
        conn.close()

    def test_lookup_local(self):
        # التأكد أن الدالة ترجع النتيجة من SQLite بنجاح
        result = fe.lookup("اختبار")
        self.assertEqual(result.get('source'), 'محلي (موثق)')
        self.assertEqual(result.get('root'), 'خ-ب-ر')

if __name__ == '__main__':
    unittest.main()
