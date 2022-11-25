## pos-display-cli

pos-display-cli is a command-line utility for printing to a pos display.
It utilizes a driver lifted from the Odoo point of sale addons repository,
available [here](https://github.com/OCA/pos/blob/8.0/hw_customer_display/controllers/main.py).

### Installing

```
pip3 install -U git+https://github.com/robbe-haesendonck/pos-display-cli.git
```

### Usage

From the command line:

```
$ pos-display-cli --device /dev/ttyUSB0 --baud-rate 9600 --timeout 2 '["line1", "line2"]'
```