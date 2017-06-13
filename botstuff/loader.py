import importlib
import os  
import sys
from botstuff import events, util

MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')
BOT_PACKAGES = ('duecommands','fun')
loaded_modules = []

def loader(action):
    for package in BOT_PACKAGES:
        for module_name in os.listdir('./'+package):
            if not module_name.startswith('__') and module_name.endswith(MODULE_EXTENSIONS):
                module = package+'.'+module_name.split('.')[0]
                action(module)
    util.logger.info('Bot extensions loaded with %d commands\n%s',len(events.command_event),', '.join(events.command_event.command_list()))

def load_module(module):
  
  """
  Import modules.
  """
  
  importlib.import_module(module)
  loaded_modules.append(module)
  
def reload_module(module):
  
  """
  Import modules.
  """
  
  if module in loaded_modules:
      importlib.reload(sys.modules[module])  
  
def module_refresh(module):
  
  """
  Eat fresh (TM)
  """

  if module not in loaded_modules:
      importlib.import_module(module)
      loaded_modules.append(module)
      
def load_modules():
    loader(load_module)
    
def reload_modules():
    loader(reload_module)
    
def refresh_modules():
    loader(module_refresh)
    
def get_loaded_modules():
    loaded = "Loaded:\n"
    for module in loaded_modules:
        loaded += "``"+module+"``\n"
    return loaded
