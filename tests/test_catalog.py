import unittest
from app.catalog import search, validate_all


class CatalogTests(unittest.TestCase):
    def test_all_photos_attributed_and_intact(self):
        failures=validate_all()
        self.assertEqual(failures,[])

    def test_search_english_disease_and_arabic_insect(self):
        self.assertTrue(search('Tomato'))
        self.assertTrue(search('الذبابة البيضاء'))
        self.assertEqual(search('no-match-747484'),[])

    def test_results_are_reference_only(self):
        for row in search(''):
            self.assertEqual(row['purpose'],'reference_only_not_training_split')
            self.assertTrue(row['source_page'].startswith('https://'))
