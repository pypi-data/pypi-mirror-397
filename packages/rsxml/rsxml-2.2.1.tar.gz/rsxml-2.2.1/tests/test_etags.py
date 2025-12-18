"""Testing for the vector ops"""

import os
import unittest

from rsxml.dotenv import parse_dotenv
from rsxml.etag import calculate_etag


class EtagTests(unittest.TestCase):
    """[summary]

    Args:
        unittest ([type]): [description]
    """

    def test_calculate_etag(self):
        """[summary]"""
        env = parse_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

        if not env or "ETAG_TEST_DATA" not in env or not os.path.exists(env["ETAG_TEST_DATA"]):
            self.skipTest("ETAG_TEST_DATA not found in .env file.")

        data_dir = env["ETAG_TEST_DATA"]

        etag_verify = {
            "cat.jpg": ['"a7eac640e7a66bdb9a0855c5137c81e5"',
                        '"665bec20e3e85efd5055ecb9ae5a1c99-1"'],
            "5mb.zip": ['"0bcc4b703f25a9caf1b79316a79555c6"',
                        '"80ab5d2025dea57e7f6977cef01b0d25-1"'],
            "100Mb.zip": ['"a7bf4a3167615963ec5216b0ae395792"',
                          '"3d7a5327d0882dfe163f2176e5619b4c-2"'],
            "262Mb.zip": ['"4c19ac8705002920e5ef7535fb2f35e1"',
                          '"12878d9ab1bb5f9e0d35470ebd468f21-6"'],
            "2Gb.zip": ['"f77c0c2655ccdaf6f6363b981b149fc9"',
                        '"0d61a9abe6db277e0c84407122404529-41"'],
        }
        for filename, etag in etag_verify.items():
            filename = os.path.join(data_dir, filename)
            # Standard single part calculation. This will give us the etag form for small files that doesn't end with "-N"
            self.assertEqual(etag[0], calculate_etag(filename, force_single_part=True))
            # Force multipart calculation by setting threshold to 0. This ensures we get the multipart etag even for small files.
            self.assertEqual(etag[1], calculate_etag(filename, force_single_part=False, chunk_thresh_bytes=0))
