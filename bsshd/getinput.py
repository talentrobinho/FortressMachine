#!/usr/bin/env /usr/local/python279/bin/python
#-*- coding: UTF-8 -*-

DoGSSAPIKeyExchange = True
def wrap_with_line_feed(s, before=0, after=1):
    '''
        格式化输出
    '''
    return '\r\n' * before + s + '\r\n' * after

class GetInput(object):
    ''' 获取用户在堡垒机伪终端的输入

        BACKSPACE_CHAR: 定义的退格键列表，通过按退格键删除输入的字符
        ENTER_CHAR： 定义的回车键、换行键列表
    '''
    BACKSPACE_CHAR = {b'\x08': b'\x08\x1b[K', b'\x7f': b'\x08\x1b[K'}
    ENTER_CHAR = [b'\r', b'\n', b'\r\n']
    UNSUPPORTED_CHAR = {b'\x15': 'Ctrl-U', b'\x0c': 'Ctrl-L',
                        b'\x05': 'Ctrl-E'}
    CLEAR_CHAR = b'\x1b[H\x1b[2J'
    BELL_CHAR = b'\x07'

    def __init__(self, chan, user):
        '''
            初始化相关变量

            Args：
                chan：与客户端的channel
                user：登陆的用户名
        '''
        self.client_channel = chan
        self.prompt = user + '> '


    def get_input(self, prompt=None):
        '''
            show ascii: ord(str)
            Args:
                prompt: 命令行提示符

            Returns:
                返回用户输入的字符串
        '''
        input_data = []

        ''' 命令行提示符的输出 '''
        if not prompt is None:
            self.client_channel.send(wrap_with_line_feed(prompt, before=1, after=0))
        else:
            self.client_channel.send(wrap_with_line_feed(self.prompt, before=1, after=0))

        ''' 捕获用户的输入行为 '''
        while True:
            ''' 读取用户的输入字符 '''
            data = self.client_channel.recv(1024)
            ''' 用户输入退格键，删除屏幕字符 '''
            if data in self.BACKSPACE_CHAR:
                # If input words less than 0, should send 'BELL'
                if len(input_data) > 0:
                    data = self.BACKSPACE_CHAR[data]
                    input_data.pop()
                else:
                    data = self.BELL_CHAR
                self.client_channel.send(data)
                continue

            ''' 用户输入的字符是以ESC键开头或者是 [确认失败，换页，请求] 字符，则返回用户终端空字符'''
            if data.startswith(b'\x1b') or data in self.UNSUPPORTED_CHAR:
                self.client_channel.send('')
                continue

            # handle shell expect
            multi_char_with_enter = False
            if len(data) > 1 and data[-1] in self.ENTER_CHAR:
                if prompt is None:
                    self.client_channel.send(data)
                input_data.append(data[:-1])
                multi_char_with_enter = True

            # If user type ENTER we should get user input
            if data in self.ENTER_CHAR or multi_char_with_enter:
                self.client_channel.send('')
                return b''.join(input_data).strip()
            else:
                if prompt is None:
                    self.client_channel.send(data)
                input_data.append(data)
