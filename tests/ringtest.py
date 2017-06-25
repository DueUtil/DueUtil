from dueutil.game.helpers.misc import Ring

ring = Ring(10)

for x in range(0,20):
    print(x,ring)
    ring.append("Test%d"%x)
    print(x,ring)
