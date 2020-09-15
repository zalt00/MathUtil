# -*- coding:Utf-8 -*-


template = """
# -*- coding:Utf-8 -*-

from .plugin_base_class import Plugin


class {0}(Plugin):
    def __init__(self):
        super().__init__()

"""

if __name__ == '__main__':
    plugin_name = input('file name: ')
    class_name = input('class name: ')
    
    print()
    
    print('Editing __init__.py...')
    with open('plugins/__init__.py', 'a', encoding='utf8') as file:
        file.write(f'from .{plugin_name} import {class_name}')
    print('Done.\n')
    
    print('Editing plugins.txt...')    
    with open('plugins.txt', 'a', encoding='utf8') as file:
        file.write(f'// {class_name}')
    print('Done.\n')
    
    print('Creating file...')
    with open(f'plugins/{plugin_name}.py', 'w', encoding='utf8') as file:
        file.write(template.format(class_name))
    print('Done.\n')
        
    input('Plugin succesfully created, press enter to quit.')
    
