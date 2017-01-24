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
