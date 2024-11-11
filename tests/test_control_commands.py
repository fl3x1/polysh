"""Polysh - Tests - Control Commands

Copyright (c) 2006 Guillaume Chazarain <guichaz@gmail.com>
Copyright (c) 2024 InnoGames GmbH
"""
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
import pexpect

from tests import launch_polysh


class TestControlCommands(unittest.TestCase):
    def testControl(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline(':')
        child.expect('ready \(1\)> ')
        child.sendline('echo a; echo; echo; echo; echo; echo; echo; echo b')
        child.expect('a')
        child.expect('b')
        child.expect('ready \(1\)> ')
        child.sendline(':unknown')
        child.expect('Unknown control command: unknown')
        child.expect('ready \(1\)> ')
        child.sendline('cat')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':send_ctrl \tz\t\t')
        child.expect('ready \(1\)> ')
        child.sendline(':send_ctrl')
        child.expect('Expected at least a letter')
        child.expect('ready \(1\)> ')
        child.sendline(':send_ctrl word')
        child.expect('Expected a single letter, got: word')
        child.expect('ready \(1\)> ')
        child.sendline('fg')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':send_ctrl d')
        child.expect('ready \(1\)> ')
        child.sendline('sleep 1h')
        child.expect('waiting \(1/1\)> ')
        child.sendcontrol('c')
        child.expect('ready \(1\)> ')
        child.sendline('cat')
        child.expect('waiting \(1/1\)> ')
        child.sendcontrol('d')
        child.expect('ready \(1\)> ')
        child.sendline('cat')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':disabl\tlocal* not_found\t')
        child.expect('not_found not found\r\n')
        child.expect('ready \(0\)> ')
        child.sendline(':enable local\t')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':list')
        child.expect('localhost enabled running:')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':list local\t')
        child.expect('localhost enabled running:')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':list unknown')
        child.expect('unknown not found')
        child.expect('waiting \(1/1\)> ')
        child.sendline(':send_ctrl c')
        child.expect('ready \(1\)> ')
        child.sendline(':quit')
        child.expect(pexpect.EOF)

    def testReconnect(self):
        child = launch_polysh(['localhost'] * 2)
        child.expect('ready \(2\)> ')
        child.sendline(':disable localhost')
        child.sendline('exit')
        child.expect('exit\r\n')
        child.expect('ready \(0\)>')
        child.sendline(':reconnect l\t')
        child.sendline(':enable')
        child.expect('ready \(2\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testListManipulation(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline(':add localhost')
        child.expect('ready \(2\)> ')
        child.sendline(':rename $(echo newname)')
        child.expect('ready \(2\)> ')
        child.sendline('date')
        child.expect('newname')
        child.expect('newname')
        child.expect('ready \(2\)> ')
        child.sendline(':rename $EMPTY_VARIABLE')
        child.expect('ready \(2\)> ')
        child.sendline('date')
        child.expect('localhost')
        child.expect('localhost')
        child.expect('ready \(2\)> ')
        child.sendline(':rename $(echo newname)')
        child.expect('ready \(2\)> ')
        child.sendline('date')
        child.expect('newname')
        child.expect('newname')
        child.expect('ready \(2\)> ')
        child.sendline(':disable newname')
        child.sendline(':purge')
        child.sendline(':enable *')
        child.expect('ready \(1\)> ')
        child.sendline(':rename')
        child.expect('ready \(1\)> ')
        child.sendline('date')
        child.expect('localhost :')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testLocalCommand(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline('cat')
        child.expect('waiting \(1/1\)> ')
        child.sendline('!ech\t te""st')
        child.expect('test')
        child.sendline(':send_ctrl d')
        child.expect('ready \(1\)> ')
        child.sendline('!exit 42')
        child.expect('Child returned 42')
        child.expect('ready \(1\)> ')
        child.sendline('!python -c "import os; os.kill(os.getpid(), 9)"')
        child.expect('Child was terminated by signal 9')
        child.expect('ready \(1\)> ')
        child.sendline(':chdir /does/not/exist')
        child.expect("\[Errno 2\] .*: '/does/not/exist'")
        child.sendline(':chdir /usr/sbi\t/does/not/exist')
        child.expect('/usr/sbin')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testLocalAbsPathCompletion(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline('echo /dev/nul\t')
        child.expect('\033\[1;36mlocalhost : \033\[1;m/dev/null')
        child.expect('ready \(1\)> ')
        child.sendline('echo /sbi\t')
        child.expect('\033\[1;36mlocalhost : \033\[1;m/sbin/')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testLogOutput(self):
        child = launch_polysh(['--log-file=/', 'localhost'])
        child.expect("\[Errno 21\].*'/'")
        child.expect(pexpect.EOF)
        child = launch_polysh(['--log-file=/cannot_write', 'localhost'])
        child.expect("\[Errno 13\].*'/cannot_write'")
        child.expect(pexpect.EOF)
        child = launch_polysh(['--log-file=/dev/full', 'localhost'])
        child.sendline('echo something')
        child.expect('Exception while writing log: /dev/full')
        child.expect('\[Errno 28\]')
        child.expect(pexpect.EOF)

        child = launch_polysh(['localhost'])

        def testEcho(msg):
            child.expect('ready \(1\)> ')
            child.sendline('echo %s' % msg)
            child.expect('\033\[1;36mlocalhost : \033\[1;m%s' % msg)
        testEcho('not logging')
        child.sendline(':set_log')
        testEcho('still not logging')
        child.sendline('!rm -f /tmp/polysh_test.log')
        testEcho('still not logging')
        child.sendline(':set_log /tmp/polysh_test.log')
        testEcho('now logging')
        testEcho('still logging')
        child.sendline(':set_log')
        testEcho('back to no logging')
        child.sendline(':set_log /tmp/polysh_test.lo\t')
        testEcho('appended to the log')
        child.sendline(':set_log')
        child.expect('ready \(1\)> ')
        child.sendline(':set_log /no-permission')
        child.expect("[Errno 13] .*: '/no-permission'")
        child.expect('Logging disabled')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

        EXPECTED_LOG = """
> echo now logging
localhost : now logging
> echo still logging
localhost : still logging
> :set_log
> echo appended to the log
localhost : appended to the log
> :set_log
""".strip()
        log = open('/tmp/polysh_test.log')
        log_lines = [l for l in log.readlines() if not l.startswith('[dbg] ')]
        actual_log = ''.join(log_lines).strip()
        self.assertEqual(actual_log, EXPECTED_LOG)
        os.remove('/tmp/polysh_test.log')

    def testSetDebug(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline(':set_debug')
        child.expect('Expected at least a letter')
        child.sendline(':set_debug word')
        child.expect("Expected 'y' or 'n', got: word")
        child.sendline(':set_debug \ty\t\t')
        child.expect('ready \(1\)> ')
        child.sendline('echo "te""st"')
        child.expect('\[dbg\] localhost\[idle\]: state => running')
        child.expect('\[dbg\] localhost\[running\]: <== echo "te""st"')
        child.expect('\[dbg\] localhost\[running\]: ==> test')
        child.expect('\033\[1;36mlocalhost : \033\[1;mtest')
        child.expect('\[dbg\] localhost\[running\]: state => idle')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testHidePassword(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline('# passwordnotprotected')
        child.expect('ready \(1\)> ')
        child.sendline(':set_debug y')
        child.sendline(':set_log /dev/nul\t')
        child.sendline(':hide_password')
        child.expect('Debugging disabled')
        child.expect('Logging disabled')
        child.expect('ready \(1\)> ')
        child.sendline('# passwordprotected')
        child.expect('ready \(1\)> ')
        child.sendline('echo password\t')
        child.expect('passwordnotprotected')
        child.expect('ready \(1\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testResetPrompt(self):
        child = launch_polysh(['localhost'])
        child.expect('ready \(1\)> ')
        child.sendline('bash')
        child.sendline(':reset_prompt l\t')
        child.expect('ready \(1\)> ')
        child.sendline(':quit')
        child.expect(pexpect.EOF)

    def testPurge(self):
        child = launch_polysh(['localhost'] * 3)
        child.expect('ready \(3\)> ')
        child.sendline(':disable localhost#*')
        child.expect('ready \(1\)> ')
        child.sendline('kill -9 $$')
        child.expect('ready \(0\)> ')
        child.sendline(':enable')
        child.expect('ready \(2\)> ')
        child.sendline(':pur\t\t')
        child.expect('ready \(2\)> ')
        child.sendline(':list')
        child.expect('localhost#1 enabled idle:')
        child.expect('localhost#2 enabled idle:')
        child.expect('ready \(2\)> ')
        child.sendeof()
        child.expect(pexpect.EOF)

    def testPrintReadBuffer(self):
        child = launch_polysh(['--ssh=echo message; sleep'] + ['2h'] * 3)
        child.expect('waiting \(3/3\)> ')
        child.sendline(':show_read_buffer \t*')
        for i in range(3):
            child.expect('\033\[1;[0-9]+m2h[ #][ 12] : \033\[1;mmessage')
        child.expect('waiting \(3/3\)> ')
        child.sendintr()
        child.expect(pexpect.EOF)
