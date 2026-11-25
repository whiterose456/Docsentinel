import unittest

from docsentinel.verifier import normalize_text, verify_payload


class NormalizeTests(unittest.TestCase):
    def test_case_and_whitespace(self):
        self.assertEqual(normalize_text("  HELLO   World "), "hello world")

    def test_curly_quotes_and_dash(self):
        self.assertEqual(normalize_text("“A—B”"), '"a-b"')

    def test_soft_hyphen(self):
        self.assertEqual(normalize_text("inter\u00adnational"), "international")


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "question": "What is the date?",
            "chunks": [
                {"chunk_id": "p1", "text": "The date is 31 December 2027."},
                {"chunk_id": "p2", "text": "Renewal must be in writing."},
            ],
            "claims": [],
        }

    def test_quote_in_cited_chunk(self):
        self.payload["claims"] = [{
            "text": "The date is 31 December 2027.",
            "chunk_id": "p1",
            "quote": "THE DATE IS 31  December 2027.",
        }]
        report = verify_payload(self.payload)
        self.assertEqual(report["claims"][0]["verdict"], "QUOTE_VERIFIED")
        self.assertFalse(report["abstained"])

    def test_quote_in_wrong_chunk_is_misattributed(self):
        self.payload["claims"] = [{
            "text": "Renewal must be in writing.",
            "chunk_id": "p1",
            "quote": "Renewal must be in writing.",
        }]
        report = verify_payload(self.payload)
        self.assertEqual(report["claims"][0]["verdict"], "MISATTRIBUTED")
        self.assertTrue(report["abstained"])

    def test_nonexistent_quote(self):
        self.payload["claims"] = [{
            "text": "There is a 90-day extension.",
            "chunk_id": "p1",
            "quote": "There is a 90-day extension.",
        }]
        self.assertEqual(verify_payload(self.payload)["claims"][0]["verdict"], "QUOTE_NOT_FOUND")

    def test_missing_attribution(self):
        self.payload["claims"] = [{"text": "Some claim", "quote": "", "chunk_id": None}]
        self.assertEqual(verify_payload(self.payload)["claims"][0]["verdict"], "UNATTRIBUTED")

    def test_empty_claims_abstain(self):
        self.assertTrue(verify_payload(self.payload)["abstained"])

    def test_changed_year_does_not_match(self):
        self.payload["claims"] = [{
            "text": "The date is 2028.",
            "chunk_id": "p1",
            "quote": "The date is 31 December 2028.",
        }]
        self.assertEqual(verify_payload(self.payload)["claims"][0]["verdict"], "QUOTE_NOT_FOUND")

    def test_duplicate_chunk_ids_rejected(self):
        self.payload["chunks"].append({"chunk_id": "p1", "text": "duplicate"})
        with self.assertRaises(ValueError):
            verify_payload(self.payload)


if __name__ == "__main__":
    unittest.main()
