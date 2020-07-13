import unittest
import i18n

i18n.load_path.append('locales')
i18n.set('file_format', 'json')
i18n.set('fallback', 'en')

class TranslationTest(unittest.TestCase):
    """Test translation work normally"""
    def test_zhtw(self):
        i18n.set('locale', 'zh-tw')
        self.assertEqual(i18n.t('guess.test'), "測試字串")

if __name__ == "__main__":
    unittest.main()
