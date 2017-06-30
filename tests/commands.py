import data_and_classes as d;

def command(**command_rules):
    def wrap(command_func):
        def wrapped_command(ctx, *args,**kwargs):
            if(ctx == command_rules.get('only_for',"No")):
                command_func(ctx,*args,**kwargs);
                return True;
            else:
                print("You can't use that command! "+str(ctx));
                return False;
        return wrapped_command;
    return wrap;

@command(only_for=1)
def myinfo(ctx,*args,**kwargs):
    if args[0] == 'myinfo':
      print("myinfo command");
      print(d.Player.find_p(ctx).name);
      
def info(*args,**kwargs):
    if args[0] == 'info':
      print("info command");
      
