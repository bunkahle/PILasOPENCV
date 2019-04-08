import unittest

import PILasOPENCV as Image


class TestImageFromBytes(unittest.TestCase):
    def test_frombytes(self):
        im1 = Image.open("lena.jpg")
        im2 = Image.frombytes(im1.mode, im1.size, im1.getdata())
        self.assertEqual(im1.getdata().tolist(), im2.getdata().tolist())
