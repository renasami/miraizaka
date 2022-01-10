import unittest
import os
import sys

workspace = os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)
sys.path.append(workspace)
print(workspace)
from main import recognize


class Test(unittest.TestCase):
    def test_recog(self):
        self.assertEqual(1, recognize())
