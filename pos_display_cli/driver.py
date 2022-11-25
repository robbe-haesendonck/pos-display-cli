"""
Driver for a pos display.

Lifted from the Odoo point of sale addons repository available at
https://github.com/OCA/pos/blob/8.0/hw_customer_display/controllers/main.py .

I take no credit for any of the code in this file, as I have merely performed
some pep8 cleanup and openerp decoupling.

"""
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Hardware Customer Display module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import logging
import simplejson
import time
from threading import Thread, Lock
import queue
from unidecode import unidecode
from serial import Serial


logger = logging.getLogger(__name__)


class CustomerDisplayDriver(Thread):

    """Customer display driver."""

    def __init__(self, device='/dev/ttyUSB0', baud_rate=9600, timeout=2):
        """Constructor."""
        Thread.__init__(self)
        self.queue = queue.Queue()
        self.lock = Lock()
        self.status = {'status': 'connecting', 'messages': []}
        self.device_name = device
        self.device_rate = baud_rate
        self.device_timeout = timeout
        self.serial = False

    def get_status(self):
        """Get the status of the display."""
        self.push_task('status')
        return self.status

    def set_status(self, status, message=None):
        """Set the status of the display."""
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            logger.error('Display Error: '+message)
        elif status == 'disconnected' and message:
            logger.warning('Disconnected Display: '+message)

    def lockedstart(self):
        """Start the thread."""
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def push_task(self, task, data=None):
        """Add a task to the task queue."""
        self.lockedstart()
        self.queue.put((time.time(), task, data))

    def move_cursor(self, col, row):
        """Move the cursor of the display."""
        # Bixolon spec : 11. "Move Cursor to Specified Position"
        self.cmd_serial_write('\x1B\x6C' + chr(col) + chr(row))

    def display_text(self, lines):
        """Display text on the display."""
        logger.debug(
            "Preparing to send the following lines to LCD: %s" % lines)
        # We don't check the number of rows/cols here, because it has already
        # been checked in the POS client in the JS code
        lines_ascii = []
        for line in lines:
            lines_ascii.append(unidecode(line))
        row = 0
        for dline in lines_ascii:
            row += 1
            self.move_cursor(1, row)
            self.serial_write(dline)

    def setup_customer_display(self):
        """
        Set LCD cursor to off.

        If your LCD has different setup instruction(s), you should
        inherit this function.

        """
        # Bixolon spec : 35. "Set Cursor On/Off"
        self.cmd_serial_write('\x1F\x43\x00')
        logger.debug('LCD cursor set to off')

    def clear_customer_display(self):
        """
        Clear the display.

        If your LCD has different clearing instruction, you should inherit this function.

        """
        # Bixolon spec : 12. "Clear Display Screen and Clear String Mode"
        self.cmd_serial_write('\x0C')
        logger.debug('Customer display cleared')

    def cmd_serial_write(self, command):
        """
        Write a serial command to the display.

        If your LCD requires a prefix and/or suffix on all commands,
        you should inherit this function.

        """
        assert isinstance(command, str), 'command must be a string'
        self.serial_write(command)

    def serial_write(self, text):
        """Write a serial string to the display."""
        # assert isinstance(text, str), 'text must be a string'
        self.serial.write(text.encode())

    def send_text_customer_display(self, text_to_display):
        """
        Send textual data to the display.

        This function sends the data to the serial/usb port.
        We open and close the serial connection on every message display.
        Why ?
        1. Because it is not a problem for the customer display
        2. Because it is not a problem for performance, according to my tests
        3. Because it allows recovery on errors : you can unplug/replug the
        customer display and it will work again on the next message without
        problem.

        """
        lines = simplejson.loads(text_to_display)
        assert isinstance(lines, list), 'lines_list should be a list'
        try:
            logger.debug(
                'Opening serial port %s for customer display with baudrate %d'
                % (self.device_name, self.device_rate))
            self.serial = Serial(
                self.device_name, self.device_rate,
                timeout=self.device_timeout)
            logger.debug('serial.is_open = %s' % self.serial.isOpen())
            self.setup_customer_display()
            self.clear_customer_display()
            self.display_text(lines)
        except Exception as e:
            logger.error('Exception in serial connection: %s' % str(e))
        finally:
            if self.serial:
                logger.debug('Closing serial port for customer display')
                self.serial.close()

    def run(self):
        """Run the driver thread."""
        while True:
            try:
                timestamp, task, data = self.queue.get(True)
                if task == 'display':
                    self.send_text_customer_display(data)
                elif task == 'status':
                    pass
            except Exception as e:
                self.set_status('error', str(e))
