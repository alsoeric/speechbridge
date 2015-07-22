#
# Python Macro Language for Dragon NaturallySpeaking
#   (c) Copyright 1999 by Joel Gould
#   Portions (c) Copyright 1999 by Dragon Systems, Inc.
#
# This sample macro file was created for my talk to the Boston Voice Users
# group on November 9, 1999.  It is explained in my PowerPoint slides.
#
# _sample1.py
#
# This is a sample macro file with a single command.  When NatSpeak has the
# focus, say "demo sample one".  It should recognize the command and type:
#   Heard macro "sample one".
#
# This file represents the simplest possible example of a NatLink macro.
#
# See also the variant _first_sample_docstring.py in the folder DisabledGrammars of Unimacro

import natlink
from natlinkutils import *
import rpyc

verbose = True

# set up rpc
conn = rpyc.connect("172.30.40.1", 12345)
print "rpyc started"

class ThisGrammar(GrammarBase):

    gramSpec = """
        <start> exported = put {name} {item};
    """
    
    def initialize(self):
        global conn        
        print "preload gramspec"
        self.load(self.gramSpec)
        print "postload gramspec"

        #setup for what one can say.
        print "pre_call"
        (name_list, item_list) = conn.root.say_what()
        print name_list
        print item_list
        
        self.setList('name',name_list)
        self.setList('item',item_list)

        # and activate...
        self.activateAll()

    def gotResults_start(self,words,fullResults):
        print fullResults
        global conn
        a_response = conn.root.this_response(fullResults[1][0], fullResults[2][0])
        #natlink.playString('Heard macro "sample one"{enter}')
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar: thisGrammar.unload()
    thisGrammar = None
