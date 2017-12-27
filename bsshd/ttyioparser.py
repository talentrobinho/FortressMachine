#!/usr/local/python279/bin/python

import pyte
import re

class TtyIOParser(object):
    def __init__(self, width=80, height=24):
        self.screen = pyte.Screen(width, height)
        self.stream = pyte.ByteStream()
        self.stream.attach(self.screen)
        self.ps1_pattern = re.compile(r'^\[?.*@.*\]?[\$#]\s|mysql>\s')

    def clean_ps1_etc(self, command):
        return self.ps1_pattern.sub('', command)

    def parse_output(self, data, sep='\n'):
        output = []
        if not isinstance(data, bytes):
            data = data.encode('utf-8', 'ignore')

        self.stream.feed(data)
        for line in self.screen.display:
            if line.strip():
                output.append(line)
        self.screen.reset()
        return sep.join(output[0:-1])

    def parse_input(self, data):
        command = []
        if not isinstance(data, bytes):
            data = data.encode('utf-8', 'ignore')

        self.stream.feed(data)
        for line in self.screen.display:
            line = line.strip()
            if line:
                command.append(line)
        if command:
            command = command[-1]
        else:
            command = ''
        self.screen.reset()
        command = self.clean_ps1_etc(command)
        return command
