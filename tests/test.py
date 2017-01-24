import data_and_classes;
import commands;



class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)

    """
    def __call__(self, ctx,*args, **kwargs):
        for f in self:
            f(ctx,*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)

e = Event();
        
e.append(commands.myinfo);

data_and_classes.player_join(1,"bob");
data_and_classes.player_join(2,"poo");

e(2,"myinfo");
