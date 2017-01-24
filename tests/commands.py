import data_and_classes as d;


def myinfo(ctx,*args,**kwargs):
    if args[0] == 'myinfo':
      print("myinfo command");
      print(d.Player.find_p(ctx).name);
      
def info(*args,**kwargs):
    if args[0] == 'info':
      print("info command");
      
