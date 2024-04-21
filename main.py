import pty
import os
import shlex
import select
import time
from threading import Thread
import re
import pyte
from pynput import keyboard

import oled

class Terminal:
    
    def __init__(self):

        self.max_read_bytes=1024 * 20

        #spawn shell
        child_pid, self.fd = pty.fork()
        if child_pid == 0:  # Child.
            os.chdir("/home/username")
            argv = shlex.split("bash")
            env = {
                "TERM": "xterm",
                "LC_ALL": "en_GB.UTF-8",
                "COLUMNS": str(oled.CHARS_WIDTH),
                "LINES": str(oled.CHARS_HEIGHT),
            }
            os.execvpe(argv[0], argv, env)
            
        #create pyte object
        self.screen = pyte.HistoryScreen(oled.CHARS_WIDTH, oled.CHARS_HEIGHT, ratio = 1/oled.CHARS_HEIGHT)
        self.stream = pyte.Stream(self.screen)


    def listen_keyboard(self):
        
        currently_pressed = set()
        
        spec_keys = {
            'enter': '\r',
            'tab': '\t',
            'esc': '\x1b',
            'home': '\x1b[1~',
            'end': '\x1b[4~',
            'backspace': '\x7f',
            'delete': '\x1b[3~',
            'space': ' ',
            'left': '\u001b[D',
            'right': '\u001b[C',
            'up': '\u001b[A',
            'down': '\u001b[B'
        }
        
        def on_press(keycode):
            try:
                key = keycode.char
            except AttributeError:
                key = keycode.name
            currently_pressed.add(key)
            
            if not key:
                return
            
            elif key == 'page_down':
                self.screen.next_page()
                oled.update_screen(self.screen.display, self.screen.cursor.x, self.screen.cursor.y)
            elif key == 'page_up':
                self.screen.prev_page()
                oled.update_screen(self.screen.display, self.screen.cursor.x, self.screen.cursor.y)

            elif len(key) == 1:
                
                is_pressed_non_single_len_key = False
                if 'shift' in currently_pressed:
                    currently_pressed.remove('shift')
                if 'shift_r' in currently_pressed:
                    currently_pressed.remove('shift_r')
                if 'ctrl' in currently_pressed:
                    os.write(self.fd, chr(ord(key)-96).encode())
                    
                for k in currently_pressed:
                    if len(k) > 1:
                        is_pressed_non_single_len_key = True

                #not allow input while pressed non-single-len special keys (except shift)
                if not is_pressed_non_single_len_key:
                    os.write(self.fd, key.encode())
                else:
                    return
                    
            elif key in spec_keys:
                os.write(self.fd, spec_keys[key].encode())        
                
        def on_release(keycode):
            try:
                key = keycode.char
            except AttributeError:
                key = keycode.name
            if key in currently_pressed:
                currently_pressed.remove(key)
        
        while True:
            with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
                listener.join()
        return input_text

    def read_and_forward_pty_output(self):
        while True:
            if self.fd:
                timeout_sec = 0
                (data_ready, _, _) = select.select([self.fd], [], [], timeout_sec)
                if data_ready:
                    output = os.read(self.fd, self.max_read_bytes).decode(errors="ignore")
                    
                    self.stream.feed(output)
                    
                    oled.update_screen(self.screen.display, self.screen.cursor.x, self.screen.cursor.y)

    def run_shell(self):
        output_thread = Thread(target=self.read_and_forward_pty_output)
        output_thread.start()

        while True:
            self.listen_keyboard()

terminal = Terminal()
terminal.run_shell()
