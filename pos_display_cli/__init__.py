"""Main module."""
import sys
from loguru import logger
import argparse

from .driver import CustomerDisplayDriver


__VERSION__ = '0.0.2'


def main():
    """Main function."""
    parser = argparse.ArgumentParser(prog='pos-display-cli',
                                     description='%(prog)s is a command-line utility for printing to a pos display')
    parser.add_argument('--device', default='/dev/ttyUSB0', type=str)
    parser.add_argument('-b', '--baud-rate', default=9600, type=int)
    parser.add_argument('-t', '--timeout', default=2, type=int)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __VERSION__)
    parser.add_argument('text_json', type=str)
    args = parser.parse_args()
    if (args.debug == False):
        logger.remove()
        logger.add(sys.stderr, level="INFO")
    device = CustomerDisplayDriver(args.device, args.baud_rate, args.timeout)
    device.send_text_customer_display(args.text_json)


if __name__ == '__main__':
    """Standard import guard."""
    main()
