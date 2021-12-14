import unittest
from ..RaspberryPi import main as RaspberryPi


class Test(unittest.TestCase):
    def test_performance(self):
        RaspberryPi.SHOW_WINDOW = True
        RaspberryPi.SAVE_PIC = False
        RaspberryPi.SEND_HTTP = False
        RaspberryPi.main(100)
