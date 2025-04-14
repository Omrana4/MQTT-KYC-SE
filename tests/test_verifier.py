import unittest
from src.verifier import Verifier
from datetime import datetime, timedelta

class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = Verifier()

    def test_valid_card(self):
        card = {
            'id': '1234-5678-9012',
            'name': 'Alice Smith',
            'expiry': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'region': 'US',
            'card_type': 'Visa'
        }
        result = self.verifier.verify_card(card)
        self.assertEqual(result['status'], 'approved')
        self.assertEqual(result['reasons'], [])

    def test_invalid_id(self):
        card = {
            'id': 'invalid_id',
            'name': 'Bob Jones',
            'expiry': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'region': 'EU',
            'card_type': 'MasterCard'
        }
        result = self.verifier.verify_card(card)
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('Invalid ID format', result['reasons'])

    def test_expired_card(self):
        card = {
            'id': '1234-5678-9012',
            'name': 'Charlie Brown',
            'expiry': '2024-09-07',
            'region': 'ASIA',
            'card_type': 'Amex'
        }
        result = self.verifier.verify_card(card)
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('Card expired', result['reasons'])

if __name__ == '__main__':
    unittest.main()
