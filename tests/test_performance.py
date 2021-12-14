import unittest

from RaspberryPi import main as RasPi


class Test(unittest.TestCase):
    def test_performance(self):
        RasPi.SHOW_WINDOW = True
        RasPi.SAVE_PIC = False
        RasPi.SEND_HTTP = False
        RasPi.main(30)


if __name__ == "__main__":
    unittest.main()
