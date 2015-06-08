import rpyc
from Tkinter import *
from itertools import combinations

verbose = True

# set up rpc
conn = rpyc.connect("172.30.40.1", 12345)

# modifier keys
mods = ('Control', 'Alt', 'Shift')

root = Tk()
prompt = 'Press any key.  Remember to keep your mouse in the cyan box. '
lab = Label(root, text=prompt, width=len(prompt), bg='cyan')
lab.pack()

def key(event):
    global conn
    msg = 'event.char is %r and event.keysym is %r' % (event.char, event.keysym)
    lab.config(text=msg)
    x = conn.root.NS_keycode(None, event.keysym)

def make_mod_key(mod):
    def mod_key(event):
        global conn
        msg = 'mod is {0}, event.char is {1} and event.keysym is {2}'.format(mod, event.char, event.keysym)
        print('MOD:', msg)
        lab.config(text=msg)
        x = conn.root.NS_keycode(mod, event.keysym)
    return mod_key

def main():

    # bind keys and modifiers + keys:
    #for mod in mods:
    #    lab.bind_all('<{0}-Key>'.format(mod), make_mod_key(mod))

    for x in xrange(len(mods) + 1):
        for c in (combinations(mods, x)):
            if c == ():
                continue
            cs = '-'.join(list(c))
            lab.bind_all('<{0}-Key>'.format(cs), make_mod_key(cs))

    #lab.bind_all('<Control-Alt-Key>', make_mod_key('Control-Alt'))
    #lab.bind_all('<Control-Shift-Key>', make_mod_key('Control-Shift'))
    #lab.bind_all('<Alt-Shift-Key>', make_mod_key('Alt-Shift'))
    #lab.bind_all('<Control-Alt-Shift-Key>', make_mod_key('Control-Alt-Shift'))

    # and unmodified key events
    lab.bind_all('<Key>', key)

    root.mainloop()

if __name__ == '__main__':
    main()
