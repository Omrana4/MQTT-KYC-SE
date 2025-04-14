import unittest
import json
from unittest.mock import Mock
from src.verifier.verifier import Verifier  # Correct import path
from datetime import datetime, timedelta

class TestVerifier(unittest.TestCase):
    def setUp(self):
        # Instantiate Verifier and mock MQTT client
        self.verifier = Verifier()
        self.verifier.client = Mock()  # Mock client to avoid MQTT connect
        self.verifier.setup_logging = Mock()  # Skip logging setup

    def test_valid_card(self):
        card = {
            'id': '1234-5678-9012',
            'name': 'Alice Smith',
            'expiry': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'region': 'US',
            'card_type': 'Visa'
        }
        self.verifier.on_message(self.verifier.client, None, Mock(payload=json.dumps(card).encode()))
        result = self.verifier.results[-1]  # Get the last result
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
        self.verifier.on_message(self.verifier.client, None, Mock(payload=json.dumps(card).encode()))
        result = self.verifier.results[-1]
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
        self.verifier.on_message(self.verifier.client, None, Mock(payload=json.dumps(card).encode()))
        result = self.verifier.results[-1]
        self.assertEqual(result['status'], 'rejected')
        self.assertIn('Card expired', result['reasons'])

if __name__ == '__main__':
    unittest.main()
