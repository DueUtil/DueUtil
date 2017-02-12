import importlib
import os  
from botstuff import events;

MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')
BOT_PACKAGES = ('duecommands','fun')

def load_modules():
  
  """
  Import all command modules.
  """
  
  for package in BOT_PACKAGES:
      for module_name in os.listdir('./'+package):
          if not module_name.startswith('__') and module_name.endswith(MODULE_EXTENSIONS):
              importlib.import_module(package+'.'+module_name.split('.')[0])
  
  print('Bot extensions loaded with '+str(len(events.command_event))+' commands');
load_modules();

def unload_module():
  
  """
  Unloads a module & removes it's commands
  """
  
def reload_module():
  
  """
  Reloads a module
  """
