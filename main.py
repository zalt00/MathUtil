# -*- coding:Utf-8 -*-

from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtWidgets, uic
import plugins
import re, sys
import traceback

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main_window.ui', self)
        
        self._plugins = {}
        self._sequences = []
        self._shortcuts = {}
        
        self.commands = {'insert_key': self.insert_key, 'execute_current_line': self.execute_current_line}
        
        self._raw_display = True
        
        self.action_clear.triggered.connect(self.clear_console)
        self.action_raw_display.triggered.connect(lambda: setattr(self, '_raw_display', True))
        self.action_precompiled_display.triggered.connect(lambda: setattr(self, '_raw_display', False))
        
        self.load_plugins()
        
        self._locals = {}
        self._globals = {}
        
        self._html_source = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:11pt; font-weight:400; font-style:normal;">
<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">*TEXT*</p></body></html>'''
        self._additional_html_text = ''
        self.display('> ', end='')
        
        self.show()
    
    def clear_console(self):
        self._additional_html_text = ''
        self.display('> ', end='')
    
    def execute_current_line(self):
        base_line = self.line_edit.text()
        line = self._precompile_line(base_line)
        execution, value = self._execute_line(line)
        if self._raw_display:
            self.display(base_line)
        else:
            self.display(line)
        if value is not None:
            if execution != 0:
                self.display('Error: ', color='#fcba03', end='')
                self.display(str(value), color='#fa6176')
            else:
                self.display('Out: ', color='#fcba03', end='')
                self.display(str(value))
                
        self.display('> ', end='')
        
        cursor = self.text_browser.textCursor()
        cursor.setPosition(len(self.text_browser.toPlainText()) - 1)
        self.text_browser.setTextCursor(cursor)
        self.text_browser.ensureCursorVisible()
    
    def load_plugins(self):
        with open('plugins.txt') as file:
            txt = file.read()
            
        for line in txt.splitlines():
            if line and not line.startswith('//'):
                self.add_plugin(line, plugins.get_plugin(line)())
    
    def _precompile_line(self, line):
        for function in self._sequences:
            line = function(line, self._locals, self._globals)
        return line
    
    def _execute_line(self, line):
        try:
            try:
                return 0, eval(line, self._globals, self._locals)
            except SyntaxError:
                pass
            exec(line, self._globals, self._locals)
            return 0, None
        except Exception:
            return -1, traceback.format_exc().replace('\n', '<br>')
            
    def display(self, msg, color='#000000', end='<br>'):
        self._additional_html_text += f'<span style=" color: {color};">{msg}</span>{end}'
        self.text_browser.setHtml(self._html_source.replace('*TEXT*', self._additional_html_text))
        
    def add_shortcut(self, str_sequence, command):
        shortcut = QShortcut(QKeySequence(str_sequence), self)
        shortcut.activated.connect(command)
        self._shortcuts[str_sequence] = shortcut
    
    def add_sequence(self, function):
        self._sequences.append(function)
    
    def add_plugin(self, name, plugin):
        self._plugins[name] = plugin
        plugin.add_to(self)
        
    def insert_key(self, key):
        self.line_edit.insert(key)
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
