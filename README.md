speech bridge is a simplified tool which will inject
keysym sequences into the Linux input queue and can also execute
remote procedure calls between Linux and Windows using rpyc.

until I find the time to properly document this, here's a bit of instructions.

External module dependencies are: uinput and rpyc

https://pypi.python.org/pypi/python-uinput
http://rpyc.readthedocs.org/en/latest/

install both of those using pip.  doesn't appear to be any need to
install latest and greatest.

whatever VM technology you use, I run communications over a private VM
to host OS network.  change the IP address starting with 172 in
linux_emitter.py and win_relay.py to whatever your private VM to host
network uses.

Start Linux side first then start Windows side.  If Linux side needs
to restart for any reason, the window side will need to be restarted
as well.


Goal: 

make window side more resilient in the face of network outage
so that it restarts (slowly) if the Linux side has broken or dropped
out.  

Try to make everything on the window side autostart.

Credits:

I want to thank two people who have helped me tremendously getting
this project started.  Laura Creighton <lac@openend.se> and starc@
<starc@humboldt1.com>

Laura helped me with getting TK to behave and give me the right
keysym and keycode characters.  starc@ built the first prototype
linux_emitter.py and showed me how to use uinput.

Both of them graciously put up with this uppity crip saying "this is
perfect, it's great, it's wonderful, oh no, it's not what I want, let
me fix it, oh I see what you're doing" all in one breath and the space
of 2 minutes.