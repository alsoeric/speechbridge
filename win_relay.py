import rpyc
from Tkinter import *
from itertools import combinations

verbose = True

# set up rpc
conn = rpyc.connect("172.30.40.1", 12345)

# modifier keys
mods = ('Control', 'Alt', 'Shift')

# remember last mod state
mod_state = []

root = Tk()
prompt = 'Press any key.  Remember to keep your mouse in the cyan box. '
lab = Label(root, text=prompt, width=len(prompt), bg='cyan')
lab.pack()

def is_modifier(keysym):
    """ is the keysym a modifier char"""
    for symbase in mods:
        if symbase in keysym:
            return True
    return False

def key_press(event):
    global conn
    global mod_state

    keysym = event.keysym

    # fix random missing keysyms
    if keysym == "??" and event.char == "@":
        keysym =  "at"
        mod_state.append("Shift_L")

        print "convert ?? to at"

    if is_modifier(keysym):
        mod_state.append(keysym)
        print "got modifier  %s " % keysym
    else:
        # not modifier? send last modifiers and key
        # force char to lower
        lc_keysym = keysym.lower()
        x = conn.root.NS_keysym(mod_state, lc_keysym)
        # clear last know modifier state

    msg = 'event.char is %r %s, event.keycode is %x, event.keysym is %r' % (event.char, event.char.encode("hex"), event.keycode, keysym)
    lab.config(text=msg)

def key_release(event):
        if is_modifier(event.keysym):
                mod_state.remove(event.keysym)

def main():
    # and unmodified key events
    lab.bind_all('<KeyPress>', key_press)
    lab.bind_all('<KeyRelease>', key_release)

    root.mainloop()

if __name__ == '__main__':
    main()
