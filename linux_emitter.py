#!/usr/bin/python
"""
    this script utilizes python-uinput to accept
    characters and emit key events to the event stream.
    uinput - Python bindings to Linux uinput system.
"""
from __future__ import print_function
from itertools import chain, groupby, imap
import operator
# from operator import itemgetter
import uinput
# from threading import Timer
import time
from sys import stdin, stdout, stderr
from threading import Lock
import rpyc
from rpyc.utils.server import ThreadedServer
# import pprint

# $version$
version = 2.3

# set silent to False to actually emit:
silent = False
# set verbose to True to see stderr messages:
verbose = True

# keys may have 1 or more modifiers
modifier = {'Control_L': uinput.KEY_LEFTCTRL,
            'Control_R': uinput.KEY_RIGHTCTRL,
            'Shift_L': uinput.KEY_LEFTSHIFT,
            'Shift_R': uinput.KEY_RIGHTSHIFT,
            'Alt_L': uinput.KEY_LEFTALT,
            'Alt_R': uinput.KEY_RIGHTALT,
            'Meta': uinput.KEY_RIGHTMETA,
#            'Control-Alt': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT),
#            'Control-Shift': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTSHIFT),
#            'Alt-Shift': (uinput.KEY_LEFTALT, uinput.KEY_LEFTSHIFT),
#            'Control-Alt-Shift': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT, uinput.KEY_LEFTSHIFT),
}

"""
    default_event_dict maps a character string to a tuple of
    one or more input events.
    So far, only simple keys are here.
"""
# only a subset of KEY_ events are implemented.
# others remain as comments.
xdefault_event_dict = {
    'Shift_L': (uinput.KEY_LEFTSHIFT,),
    'Shift_R': (uinput.KEY_RIGHTSHIFT,),
    'Super_L': (uinput.KEY_LEFTMETA,),
    'Super_R': (uinput.KEY_RIGHTMETA,),
    'Control_L': (uinput.KEY_LEFTCTRL,),
    'Control_R': (uinput.KEY_RIGHTCTRL,),
    'Alt_L': (uinput.KEY_LEFTALT,),
    'Alt_R': (uinput.KEY_RIGHTALT,),
    'Caps_Lock': (uinput.KEY_CAPSLOCK,),
    'Menu': (uinput.KEY_MENU,),
    'Left': (uinput.KEY_LEFT,),
    'Right': (uinput.KEY_RIGHT,),
    'Up': (uinput.KEY_UP,),
    'Down': (uinput.KEY_DOWN,),
    'BackSpace': (uinput.KEY_BACKSPACE,),
    'Home': (uinput.KEY_HOME,),
    'End': (uinput.KEY_END,),
    'Insert': (uinput.KEY_INSERT,),
    'Prior': (uinput.KEY_PAGEUP,),
    'Delete': (uinput.KEY_DELETE,),
    'Next': (uinput.KEY_PAGEDOWN,),
    'grave': (uinput.KEY_GRAVE,),
    'asciitilde': (uinput.KEY_LEFTSHIFT, uinput.KEY_GRAVE),
    'exclam': (uinput.KEY_LEFTSHIFT, uinput.KEY_1),
    'at': (uinput.KEY_LEFTSHIFT, uinput.KEY_2),
    'numbersign': (uinput.KEY_LEFTSHIFT, uinput.KEY_3),
    'dollar': (uinput.KEY_LEFTSHIFT, uinput.KEY_4),
    'percent': (uinput.KEY_LEFTSHIFT, uinput.KEY_5),
    'asciicircum': (uinput.KEY_LEFTSHIFT, uinput.KEY_6),
    'ampersand': (uinput.KEY_LEFTSHIFT, uinput.KEY_7),
    'asterisk': (uinput.KEY_LEFTSHIFT, uinput.KEY_8),
    'parenleft': (uinput.KEY_LEFTSHIFT, uinput.KEY_9),
    'parenright': (uinput.KEY_LEFTSHIFT, uinput.KEY_0),
    'minus': (uinput.KEY_MINUS,),
    'underscore': (uinput.KEY_LEFTSHIFT, uinput.KEY_MINUS),
    'equal': (uinput.KEY_EQUAL,),
    'plus': (uinput.KEY_LEFTSHIFT, uinput.KEY_EQUAL,),
    'bar': (uinput.KEY_LEFTSHIFT, uinput.KEY_BACKSLASH,),
    'backslash': (uinput.KEY_BACKSLASH,),
    'question': (uinput.KEY_LEFTSHIFT, uinput.KEY_BACKSLASH,),
    'braceright': (uinput.KEY_RIGHTBRACE,),
    'bracketright': (uinput.KEY_LEFTSHIFT, uinput.KEY_RIGHTBRACE),
    'braceleft': (uinput.KEY_LEFTBRACE,),
    'bracketleft': (uinput.KEY_LEFTSHIFT, uinput.KEY_LEFTBRACE),
    'apostrophe': (uinput.KEY_APOSTROPHE,),
    'colon': (uinput.KEY_LEFTSHIFT, uinput.KEY_SEMICOLON),
    'semicolon': (uinput.KEY_SEMICOLON,),
    'slash': (uinput.KEY_SLASH,),
    'greater': (uinput.KEY_LEFTSHIFT, uinput.KEY_DOT),
    'period': (uinput.KEY_DOT,),
    'less': (uinput.KEY_LEFTSHIFT, uinput.KEY_COMMA),
    'comma': (uinput.KEY_COMMA,),
    'space': (uinput.KEY_SPACE,),
    '0': (uinput.KEY_0,),
    ')': (uinput.KEY_LEFTSHIFT, uinput.KEY_0),
    '1': (uinput.KEY_1,),
    '!': (uinput.KEY_LEFTSHIFT, uinput.KEY_1),
    '2': (uinput.KEY_2,),
    '@': (uinput.KEY_LEFTSHIFT, uinput.KEY_2),
    '3': (uinput.KEY_3,),
    '#': (uinput.KEY_LEFTSHIFT, uinput.KEY_3),
    '4': (uinput.KEY_4,),
    '$': (uinput.KEY_LEFTSHIFT, uinput.KEY_4),
    '5': (uinput.KEY_5,),
    '%': (uinput.KEY_LEFTSHIFT, uinput.KEY_5),
    '6': (uinput.KEY_6,),
    '^': (uinput.KEY_LEFTSHIFT, uinput.KEY_6),
    '7': (uinput.KEY_7,),
    '&': (uinput.KEY_LEFTSHIFT, uinput.KEY_7),
    '8': (uinput.KEY_8,),
    '*': (uinput.KEY_LEFTSHIFT, uinput.KEY_8),
    '9': (uinput.KEY_9,),
    '(': (uinput.KEY_LEFTSHIFT, uinput.KEY_9),
    'a': (uinput.KEY_A,),
    'A': (uinput.KEY_LEFTSHIFT, uinput.KEY_A),
    # KEY_AB
    # KEY_ADDRESSBOOK
    # KEY_AGAIN
    # KEY_ALS_TOGGLE
    # KEY_ALTERASE
    # KEY_ANGLE
    '\'': (uinput.KEY_APOSTROPHE,),
    '"': (uinput.KEY_LEFTSHIFT, uinput.KEY_APOSTROPHE),
    'quoteright': (uinput.KEY_LEFTSHIFT, uinput.KEY_APOSTROPHE),
    # KEY_APPSELECT
    # KEY_ARCHIVE
    # KEY_ATTENDANT_OFF
    # KEY_ATTENDANT_ON
    # KEY_ATTENDANT_TOGGLE
    # KEY_AUDIO
    # KEY_AUX
    'b': (uinput.KEY_B,),
    'B': (uinput.KEY_LEFTSHIFT, uinput.KEY_B),
    # KEY_BACK
    '\\': (uinput.KEY_BACKSLASH,),
    '|': (uinput.KEY_LEFTSHIFT, uinput.KEY_BACKSLASH),
    # '?': (uinput.KEY_LEFTSHIFT, uinput.KEY_BACKSLASH),
    '\b': (uinput.KEY_BACKSPACE,),
    # KEY_BASSBOOST
    # KEY_BATTERY
    # KEY_BLUE
    # KEY_BLUETOOTH
    # KEY_BOOKMARKS
    # KEY_BREAK
    # KEY_BRIGHTNESSDOWN
    # KEY_BRIGHTNESSUP
    # KEY_BRIGHTNESS_AUTO
    # KEY_BRIGHTNESS_CYCLE
    # KEY_BRIGHTNESS_MAX
    # KEY_BRIGHTNESS_MIN
    # KEY_BRL_DOT1
    # KEY_BRL_DOT10
    # KEY_BRL_DOT2
    # KEY_BRL_DOT3
    # KEY_BRL_DOT4
    # KEY_BRL_DOT5
    # KEY_BRL_DOT6
    # KEY_BRL_DOT7
    # KEY_BRL_DOT8
    # KEY_BRL_DOT9
    # KEY_BUTTONCONFIG
    'c': (uinput.KEY_C,),
    'C': (uinput.KEY_LEFTSHIFT, uinput.KEY_C),
    # KEY_CALC
    # KEY_CALENDAR
    # KEY_CAMERA
    # KEY_CAMERA_DOWN
    # KEY_CAMERA_FOCUS
    # KEY_CAMERA_LEFT
    # KEY_CAMERA_RIGHT
    # KEY_CAMERA_UP
    # KEY_CAMERA_ZOOMIN
    # KEY_CAMERA_ZOOMOUT
    # KEY_CANCEL
    # KEY_CAPSLOCK
    # KEY_CD
    # KEY_CHANNEL
    # KEY_CHANNELDOWN
    # KEY_CHANNELUP
    # KEY_CHAT
    # KEY_CLEAR
    # KEY_CLOSE
    # KEY_CLOSECD
    # KEY_COFFEE
    ',': (uinput.KEY_COMMA,),
    '<': (uinput.KEY_LEFTSHIFT, uinput.KEY_COMMA),
    # KEY_COMPOSE
    # KEY_COMPUTER
    # KEY_CONFIG
    # KEY_CONNECT
    # KEY_CONTEXT_MENU
    # KEY_CONTROLPANEL
    # KEY_COPY
    # KEY_CUT
    # KEY_CYCLEWINDOWS
    'd': (uinput.KEY_D,),
    'D': (uinput.KEY_LEFTSHIFT, uinput.KEY_D),
    # KEY_DASHBOARD
    # KEY_DATABASE
    'Delete': (uinput.KEY_DELETE,),
    # KEY_DELETEFILE
    # KEY_DEL_EOL
    # KEY_DEL_EOS
    # KEY_DEL_LINE
    # KEY_DIGITS
    # KEY_DIRECTION
    # KEY_DIRECTORY
    # KEY_DISPLAYTOGGLE
    # KEY_DISPLAY_OFF
    # KEY_DOCUMENTS
    # KEY_DOLLAR
    '.': (uinput.KEY_DOT,),
    '>': (uinput.KEY_LEFTSHIFT, uinput.KEY_DOT),
    # KEY_DOWN
    # KEY_DVD
    'e': (uinput.KEY_E,),
    'E': (uinput.KEY_LEFTSHIFT, uinput.KEY_E),
    # KEY_EDIT
    # KEY_EDITOR
    # KEY_EJECTCD
    # KEY_EJECTCLOSECD
    # KEY_EMAIL
    # KEY_END
    'Return': (uinput.KEY_ENTER,),

    # KEY_EPG
    '=': (uinput.KEY_EQUAL,),
    '+': (uinput.KEY_LEFTSHIFT, uinput.KEY_EQUAL,),
    'Escape': (uinput.KEY_ESC,),
    # KEY_EURO
    # KEY_EXIT
    'f': (uinput.KEY_F,),
    'F': (uinput.KEY_LEFTSHIFT, uinput.KEY_F),
    'F1': (uinput.KEY_F1,),
    'F2': (uinput.KEY_F2,),
    'F3': (uinput.KEY_F3,),
    'F4': (uinput.KEY_F4,),
    'F5': (uinput.KEY_F5,),
    'F6': (uinput.KEY_F6,),
    'F7': (uinput.KEY_F7,),
    'F8': (uinput.KEY_F8,),
    'F9': (uinput.KEY_F9,),
    'F10': (uinput.KEY_F10,),
    'F11': (uinput.KEY_F11,),
    'F12': (uinput.KEY_F12,),
    'F13': (uinput.KEY_F13,),
    'F14': (uinput.KEY_F14,),
    'F15': (uinput.KEY_F15,),
    'F16': (uinput.KEY_F16,),
    'F17': (uinput.KEY_F17,),
    'F18': (uinput.KEY_F18,),
    'F19': (uinput.KEY_F19,),
    'F20': (uinput.KEY_F20,),
    'F21': (uinput.KEY_F21,),
    'F22': (uinput.KEY_F22,),
    'F23': (uinput.KEY_F23,),
    'F24': (uinput.KEY_F24,),
    # KEY_FASTFORWARD
    # KEY_FAVORITES
    # KEY_FILE
    # KEY_FINANCE
    # KEY_FIND
    # KEY_FIRST
    # KEY_FN
    # KEY_FN_1
    # KEY_FN_2
    # KEY_FN_B
    # KEY_FN_D
    # KEY_FN_E
    # KEY_FN_ESC
    # KEY_FN_F
    # KEY_FN_F1
    # KEY_FN_F10
    # KEY_FN_F11
    # KEY_FN_F12
    # KEY_FN_F2
    # KEY_FN_F3
    # KEY_FN_F4
    # KEY_FN_F5
    # KEY_FN_F6
    # KEY_FN_F7
    # KEY_FN_F8
    # KEY_FN_F9
    # KEY_FN_S
    # KEY_FORWARD
    # KEY_FORWARDMAIL
    # KEY_FRAMEBACK
    # KEY_FRAMEFORWARD
    # KEY_FRONT
    'g': (uinput.KEY_G,),
    'G': (uinput.KEY_LEFTSHIFT, uinput.KEY_G),
    # KEY_GAMES
    # KEY_GOTO
    # KEY_GRAPHICSEDITOR
    '`': (uinput.KEY_GRAVE,),
    '~': (uinput.KEY_LEFTSHIFT, uinput.KEY_GRAVE),
    # KEY_GREEN
    'h': (uinput.KEY_H,),
    'H': (uinput.KEY_LEFTSHIFT, uinput.KEY_H),
    # KEY_HANGEUL
    # KEY_HANJA
    # KEY_HELP
    # KEY_HENKAN
    # KEY_HIRAGANA
    # KEY_HOME
    # KEY_HOMEPAGE
    # KEY_HP
    'i': (uinput.KEY_I,),
    'I': (uinput.KEY_LEFTSHIFT, uinput.KEY_I),
    # KEY_IMAGES
    # KEY_INFO
    # KEY_INSERT
    # KEY_INS_LINE
    # KEY_ISO
    'j': (uinput.KEY_J,),
    'J': (uinput.KEY_LEFTSHIFT, uinput.KEY_J),
    # KEY_JOURNAL
    'k': (uinput.KEY_K,),
    'K': (uinput.KEY_LEFTSHIFT, uinput.KEY_K),
    # KEY_KATAKANA
    # KEY_KATAKANAHIRAGANA
    # KEY_KBDILLUMDOWN
    # KEY_KBDILLUMTOGGLE
    # KEY_KBDILLUMUP
    # KEY_KBDINPUTASSIST_ACCEPT
    # KEY_KBDINPUTASSIST_CANCEL
    # KEY_KBDINPUTASSIST_NEXT
    # KEY_KBDINPUTASSIST_NEXTGROUP
    # KEY_KBDINPUTASSIST_PREV
    # KEY_KBDINPUTASSIST_PREVGROUP
    # KEY_KEYBOARD

    # these are currently unpaired Keypad events
    # KP_Home
    # KP_Up
    # KP_Prior
    # KP_Left
    # KP_Begin
    # KP_Right
    # KP_End
    # KP_Down
    # KP_Next
    # KP_Delete

    # and some Keypad events we know about.
    'KP_0': (uinput.KEY_KP0,),
    'KP_1': (uinput.KEY_KP1,),
    'KP_2': (uinput.KEY_KP2,),
    'KP_3': (uinput.KEY_KP3,),
    'KP_4': (uinput.KEY_KP4,),
    'KP_5': (uinput.KEY_KP5,),
    'KP_6': (uinput.KEY_KP6,),
    'KP_7': (uinput.KEY_KP7,),
    'KP_8': (uinput.KEY_KP8,),
    'KP_9': (uinput.KEY_KP9,),
    'KP_Multiply': (uinput.KEY_KPASTERISK,),
    # KEY_KPCOMMA
    'KP_Decimal': (uinput.KEY_KPDOT,),
    'KP_Enter': (uinput.KEY_KPENTER,),
    # KEY_KPEQUAL
    # KEY_KPJPCOMMA
    # KEY_KPLEFTPAREN
    'KP_Subtract': (uinput.KEY_KPMINUS,),
    'KP_Add': (uinput.KEY_KPPLUS,),
    # KEY_KPPLUSMINUS
    # KEY_KPRIGHTPAREN
    'KP_Divide': (uinput.KEY_KPSLASH,),
    'l': (uinput.KEY_L,),
    'L': (uinput.KEY_LEFTSHIFT, uinput.KEY_L),
    # KEY_LANGUAGE
    # KEY_LAST
    # KEY_LEFT
    # KEY_LEFTALT
    '[': (uinput.KEY_LEFTBRACE,),
    '{': (uinput.KEY_LEFTSHIFT, uinput.KEY_LEFTBRACE),
    # KEY_LEFTCTRL
    # KEY_LEFTMETA
    # KEY_LEFTSHIFT
    # KEY_LIGHTS_TOGGLE
    # KEY_LINEFEED
    # KEY_LIST
    # KEY_LOGOFF
    'm': (uinput.KEY_M,),
    # 'M': (uinput.KEY_LEFTSHIFT, uinput.KEY_M),
    # KEY_MACRO
    # KEY_MAIL
    # KEY_MAX
    # KEY_MEDIA
    # KEY_MEDIA_REPEAT
    # KEY_MEMO
    # KEY_MENU
    # KEY_MESSENGER
    # KEY_MHP
    # KEY_MICMUTE
    '-': (uinput.KEY_MINUS,),
    '_': (uinput.KEY_LEFTSHIFT, uinput.KEY_MINUS,),
    # KEY_MODE
    # KEY_MOVE
    # KEY_MP3
    # KEY_MSDOS
    # KEY_MUHENKAN
    # KEY_MUTE
    'n': (uinput.KEY_N,),
    'N': (uinput.KEY_LEFTSHIFT, uinput.KEY_N),
    # KEY_NEW
    # KEY_NEWS
    # KEY_NEXT
    # KEY_NEXTSONG
    # KEY_NUMERIC_0
    # KEY_NUMERIC_1
    # KEY_NUMERIC_2
    # KEY_NUMERIC_3
    # KEY_NUMERIC_4
    # KEY_NUMERIC_5
    # KEY_NUMERIC_6
    # KEY_NUMERIC_7
    # KEY_NUMERIC_8
    # KEY_NUMERIC_9
    # KEY_NUMERIC_POUND
    # KEY_NUMERIC_STAR
    'Num_Lock': (uinput.KEY_NUMLOCK,),
    'o': (uinput.KEY_O,),
    'O': (uinput.KEY_LEFTSHIFT, uinput.KEY_O),
    # KEY_OK
    # KEY_OPEN
    # KEY_OPTION
    'p': (uinput.KEY_P,),
    'P': (uinput.KEY_LEFTSHIFT, uinput.KEY_P),
    # KEY_PAGEDOWN
    # KEY_PAGEUP
    # KEY_PASTE
    # KEY_PAUSE
    # KEY_PAUSECD
    # KEY_PC
    # KEY_PHONE
    # KEY_PLAY
    # KEY_PLAYCD
    # KEY_PLAYER
    # KEY_PLAYPAUSE
    # KEY_POWER
    # KEY_POWER2
    # KEY_PRESENTATION
    # KEY_PREVIOUS
    # KEY_PREVIOUSSONG
    # KEY_PRINT
    # KEY_PROG1
    # Key_prog2
    # KEY_PROG3
    # KEY_PROG4
    # KEY_PROGRAM
    # KEY_PROPS
    # KEY_PVR
    'q': (uinput.KEY_Q,),
    'Q': (uinput.KEY_LEFTSHIFT, uinput.KEY_Q),
    'r': (uinput.KEY_R,),
    'R': (uinput.KEY_LEFTSHIFT, uinput.KEY_R),
    # KEY_RADIO
    # KEY_RECORD
    # KEY_RED
    # KEY_REDO
    # KEY_REFRESH
    # KEY_REPLY
    # KEY_RESERVED
    # KEY_RESTART
    # KEY_REWIND
    # KEY_RFKILL
    # KEY_RIGHT
    # KEY_RIGHTALT
    ']': (uinput.KEY_RIGHTBRACE,),
    '}': (uinput.KEY_LEFTSHIFT, uinput.KEY_RIGHTBRACE),
    # KEY_RIGHTCTRL
    # KEY_RIGHTMETA
    # KEY_RIGHTSHIFT
    # KEY_RO
    's': (uinput.KEY_S,),
    'S': (uinput.KEY_LEFTSHIFT, uinput.KEY_S),
    # KEY_SAT
    # KEY_SAT2
    # KEY_SAVE
    # KEY_SCALE
    # KEY_SCREEN
    # KEY_SCREENSAVER
    # KEY_SCROLLDOWN
    # KEY_SCROLLLOCK
    # KEY_SCROLLUP
    # KEY_SEARCH
    # KEY_SELECT
    ';': (uinput.KEY_SEMICOLON,),
    ':': (uinput.KEY_LEFTSHIFT, uinput.KEY_SEMICOLON),
    # KEY_SEND
    # KEY_SENDFILE
    # KEY_SETUP
    # KEY_SHOP
    # KEY_SHUFFLE
    '/': (uinput.KEY_SLASH,),
    '?': (uinput.KEY_LEFTSHIFT, uinput.KEY_SLASH),
    # KEY_SLEEP
    # KEY_SLOW
    # KEY_SOUND
    ' ': (uinput.KEY_SPACE,),
    # KEY_SPELLCHECK
    # KEY_SPORT
    # KEY_SPREADSHEET
    # KEY_STOP
    # KEY_STOPCD
    # KEY_SUBTITLE
    # KEY_SUSPEND
    # KEY_SWITCHVIDEOMODE
    # KEY_SYSRQ
    't': (uinput.KEY_T,),
    'T': (uinput.KEY_LEFTSHIFT, uinput.KEY_T),
    '\t': (uinput.KEY_TAB,),
    # KEY_TAPE
    # KEY_TASKMANAGER
    # KEY_TEEN
    # KEY_TEXT
    # KEY_TIME
    # KEY_TITLE
    # KEY_TOUCHPAD_OFF
    # KEY_TOUCHPAD_ON
    # KEY_TOUCHPAD_TOGGLE
    # KEY_TUNER
    # KEY_TV
    # KEY_TV2
    # KEY_TWEN
    'u': (uinput.KEY_U,),
    'U': (uinput.KEY_LEFTSHIFT, uinput.KEY_U),
    # KEY_UNDO
    # KEY_UNKNOWN
    # KEY_UP
    # KEY_UWB
    'v': (uinput.KEY_V,),
    'V': (uinput.KEY_LEFTSHIFT, uinput.KEY_V),
    # KEY_VCR
    # KEY_VCR2
    # KEY_VENDOR
    # KEY_VIDEO
    # KEY_VIDEOPHONE
    # KEY_VIDEO_NEXT
    # KEY_VIDEO_PREV
    # KEY_VOICECOMMAND
    # KEY_VOICEMAIL
    # KEY_VOLUMEDOWN
    # KEY_VOLUMEUP
    'w': (uinput.KEY_W,),
    'W': (uinput.KEY_LEFTSHIFT, uinput.KEY_W),
    # KEY_WAKEUP
    # KEY_WLAN
    # KEY_WORDPROCESSOR
    # KEY_WPS_BUTTON
    # KEY_WWAN
    # KEY_WWW
    'x': (uinput.KEY_X,),
    'X': (uinput.KEY_LEFTSHIFT, uinput.KEY_X),
    # KEY_XFER
    'y': (uinput.KEY_Y,),
    'Y': (uinput.KEY_LEFTSHIFT, uinput.KEY_Y),
    # KEY_YELLOW
    # KEY_YEN
    'z': (uinput.KEY_Z,),
    'Z': (uinput.KEY_LEFTSHIFT, uinput.KEY_Z),
    # KEY_ZENKAKUHANKAKU
    # KEY_ZOOM
    # KEY_ZOOMIN
    # KEY_ZOOMOUT
    # KEY_ZOOMRESET
}

# keys may have 1 or more modifiers
xmodifier = {
    'Control_L': (uinput.KEY_LEFTCTRL,),
    'Control_R': (uinput.KEY_RIGHTCTRL,),
    'Shift_L': (uinput.KEY_LEFTSHIFT,),
    'Shift_R': (uinput.KEY_RIGHTSHIFT,),
    'Alt_L': (uinput.KEY_LEFTALT,),
    'Alt_R': (uinput.KEY_RIGHTALT,),
    'Meta': (uinput.KEY_RIGHTMETA,),
#            'Control-Alt': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT),
#            'Control-Shift': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTSHIFT),
#            'Alt-Shift': (uinput.KEY_LEFTALT, uinput.KEY_LEFTSHIFT),
#            'Control-Alt-Shift': (uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT, uinput.KEY_LEFTSHIFT),
}


"""
    default_event_dict map the windows/tk keysyms to the linus equivelent.
    So far, only simple keys are here.
"""
# only a subset of KEY_ events are implemented.
# others remain as comments.
default_event_dict = {
    'Shift_L': uinput.KEY_LEFTSHIFT,
    'Shift_R': uinput.KEY_RIGHTSHIFT,
    'Super_L': uinput.KEY_LEFTMETA,
    'Super_R': uinput.KEY_RIGHTMETA,
    'Control_L': uinput.KEY_LEFTCTRL,
    'Control_R': uinput.KEY_RIGHTCTRL,
    'Alt_L': uinput.KEY_LEFTALT,
    'Alt_R': uinput.KEY_RIGHTALT,
    'Caps_Lock': uinput.KEY_CAPSLOCK,
    'Menu': uinput.KEY_MENU,
    'Left': uinput.KEY_LEFT,
    'Right': uinput.KEY_RIGHT,
    'Up': uinput.KEY_UP,
    'Down': uinput.KEY_DOWN,
    'backspace': uinput.KEY_BACKSPACE,
    'Home': uinput.KEY_HOME,
    'End': uinput.KEY_END,
    'Insert': uinput.KEY_INSERT,
    'Prior': uinput.KEY_PAGEUP,
    'Delete': uinput.KEY_DELETE,
    'Next': uinput.KEY_PAGEDOWN,
    'grave': uinput.KEY_GRAVE,
    'equal': uinput.KEY_EQUAL,
    'backslash': uinput.KEY_BACKSLASH,
    'braceright': uinput.KEY_RIGHTBRACE,
    'braceleft': uinput.KEY_LEFTBRACE,
    'apostrophe': uinput.KEY_APOSTROPHE,
    'semicolon': uinput.KEY_SEMICOLON,
    'slash': uinput.KEY_SLASH,
    'period': uinput.KEY_DOT,
    'comma': uinput.KEY_COMMA,
    'space': uinput.KEY_SPACE,
    '0': uinput.KEY_0,
    '1': uinput.KEY_1,
    '2': uinput.KEY_2,
    '3': uinput.KEY_3,
    '4': uinput.KEY_4,
    '5': uinput.KEY_5,
    '6': uinput.KEY_6,
    '7': uinput.KEY_7,
    '8': uinput.KEY_8,
    '9': uinput.KEY_9,
    'a': uinput.KEY_A,
    # KEY_AB
    # KEY_ADDRESSBOOK
    # KEY_AGAIN
    # KEY_ALS_TOGGLE
    # KEY_ALTERASE
    # KEY_ANGLE
    '\'': uinput.KEY_APOSTROPHE,
    # KEY_APPSELECT
    # KEY_ARCHIVE
    # KEY_ATTENDANT_OFF
    # KEY_ATTENDANT_ON
    # KEY_ATTENDANT_TOGGLE
    # KEY_AUDIO
    # KEY_AUX
    'b': uinput.KEY_B,
    # KEY_BACK
    '\\': uinput.KEY_BACKSLASH,
    '\b': uinput.KEY_BACKSPACE,
    # KEY_BASSBOOST
    # KEY_BATTERY
    # KEY_BLUE
    # KEY_BLUETOOTH
    # KEY_BOOKMARKS
    # KEY_BREAK
    # KEY_BRIGHTNESSDOWN
    # KEY_BRIGHTNESSUP
    # KEY_BRIGHTNESS_AUTO
    # KEY_BRIGHTNESS_CYCLE
    # KEY_BRIGHTNESS_MAX
    # KEY_BRIGHTNESS_MIN
    # KEY_BRL_DOT1
    # KEY_BRL_DOT10
    # KEY_BRL_DOT2
    # KEY_BRL_DOT3
    # KEY_BRL_DOT4
    # KEY_BRL_DOT5
    # KEY_BRL_DOT6
    # KEY_BRL_DOT7
    # KEY_BRL_DOT8
    # KEY_BRL_DOT9
    # KEY_BUTTONCONFIG
    'c': uinput.KEY_C,
    # KEY_CALC
    # KEY_CALENDAR
    # KEY_CAMERA
    # KEY_CAMERA_DOWN
    # KEY_CAMERA_FOCUS
    # KEY_CAMERA_LEFT
    # KEY_CAMERA_RIGHT
    # KEY_CAMERA_UP
    # KEY_CAMERA_ZOOMIN
    # KEY_CAMERA_ZOOMOUT
    # KEY_CANCEL
    # KEY_CAPSLOCK
    # KEY_CD
    # KEY_CHANNEL
    # KEY_CHANNELDOWN
    # KEY_CHANNELUP
    # KEY_CHAT
    # KEY_CLEAR
    # KEY_CLOSE
    # KEY_CLOSECD
    # KEY_COFFEE
    ',': uinput.KEY_COMMA,
    # KEY_COMPOSE
    # KEY_COMPUTER
    # KEY_CONFIG
    # KEY_CONNECT
    # KEY_CONTEXT_MENU
    # KEY_CONTROLPANEL
    # KEY_COPY
    # KEY_CUT
    # KEY_CYCLEWINDOWS
    'd': uinput.KEY_D,
    # KEY_DASHBOARD
    # KEY_DATABASE
    'Delete': uinput.KEY_DELETE,
    # KEY_DELETEFILE
    # KEY_DEL_EOL
    # KEY_DEL_EOS
    # KEY_DEL_LINE
    # KEY_DIGITS
    # KEY_DIRECTION
    # KEY_DIRECTORY
    # KEY_DISPLAYTOGGLE
    # KEY_DISPLAY_OFF
    # KEY_DOCUMENTS
    # KEY_DOLLAR
    '.': uinput.KEY_DOT,
    # KEY_DOWN
    # KEY_DVD
    'e': uinput.KEY_E,
    # KEY_EDIT
    # KEY_EDITOR
    # KEY_EJECTCD
    # KEY_EJECTCLOSECD
    # KEY_EMAIL
    # KEY_END
    'Return': uinput.KEY_ENTER,

    # KEY_EPG
    '=': uinput.KEY_EQUAL,
    'Escape': uinput.KEY_ESC,
    # KEY_EURO
    # KEY_EXIT
    'f': uinput.KEY_F,
    'F1': uinput.KEY_F1,
    'F2': uinput.KEY_F2,
    'F3': uinput.KEY_F3,
    'F4': uinput.KEY_F4,
    'F5': uinput.KEY_F5,
    'F6': uinput.KEY_F6,
    'F7': uinput.KEY_F7,
    'F8': uinput.KEY_F8,
    'F9': uinput.KEY_F9,
    'F10': uinput.KEY_F10,
    'F11': uinput.KEY_F11,
    'F12': uinput.KEY_F12,
    'F13': uinput.KEY_F13,
    'F14': uinput.KEY_F14,
    'F15': uinput.KEY_F15,
    'F16': uinput.KEY_F16,
    'F17': uinput.KEY_F17,
    'F18': uinput.KEY_F18,
    'F19': uinput.KEY_F19,
    'F20': uinput.KEY_F20,
    'F21': uinput.KEY_F21,
    'F22': uinput.KEY_F22,
    'F23': uinput.KEY_F23,
    'F24': uinput.KEY_F24,
    # KEY_FASTFORWARD
    # KEY_FAVORITES
    # KEY_FILE
    # KEY_FINANCE
    # KEY_FIND
    # KEY_FIRST
    # KEY_FN
    # KEY_FN_1
    # KEY_FN_2
    # KEY_FN_B
    # KEY_FN_D
    # KEY_FN_E
    # KEY_FN_ESC
    # KEY_FN_F
    # KEY_FN_F1
    # KEY_FN_F10
    # KEY_FN_F11
    # KEY_FN_F12
    # KEY_FN_F2
    # KEY_FN_F3
    # KEY_FN_F4
    # KEY_FN_F5
    # KEY_FN_F6
    # KEY_FN_F7
    # KEY_FN_F8
    # KEY_FN_F9
    # KEY_FN_S
    # KEY_FORWARD
    # KEY_FORWARDMAIL
    # KEY_FRAMEBACK
    # KEY_FRAMEFORWARD
    # KEY_FRONT
    'g': uinput.KEY_G,
    # KEY_GAMES
    # KEY_GOTO
    # KEY_GRAPHICSEDITOR
    '`': uinput.KEY_GRAVE,
    # KEY_GREEN
    'h': uinput.KEY_H,
    # KEY_HANGEUL
    # KEY_HANJA
    # KEY_HELP
    # KEY_HENKAN
    # KEY_HIRAGANA
    # KEY_HOME
    # KEY_HOMEPAGE
    # KEY_HP
    'i': uinput.KEY_I,
    # KEY_IMAGES
    # KEY_INFO
    # KEY_INSERT
    # KEY_INS_LINE
    # KEY_ISO
    'j': uinput.KEY_J,
    # KEY_JOURNAL
    'k': uinput.KEY_K,
    # KEY_KATAKANA
    # KEY_KATAKANAHIRAGANA
    # KEY_KBDILLUMDOWN
    # KEY_KBDILLUMTOGGLE
    # KEY_KBDILLUMUP
    # KEY_KBDINPUTASSIST_ACCEPT
    # KEY_KBDINPUTASSIST_CANCEL
    # KEY_KBDINPUTASSIST_NEXT
    # KEY_KBDINPUTASSIST_NEXTGROUP
    # KEY_KBDINPUTASSIST_PREV
    # KEY_KBDINPUTASSIST_PREVGROUP
    # KEY_KEYBOARD

    # these are currently unpaired Keypad events
    # KP_Home
    # KP_Up
    # KP_Prior
    # KP_Left
    # KP_Begin
    # KP_Right
    # KP_End
    # KP_Down
    # KP_Next
    # KP_Delete

    # and some Keypad events we know about.
    'KP_0': uinput.KEY_KP0,
    'KP_1': uinput.KEY_KP1,
    'KP_2': uinput.KEY_KP2,
    'KP_3': uinput.KEY_KP3,
    'KP_4': uinput.KEY_KP4,
    'KP_5': uinput.KEY_KP5,
    'KP_6': uinput.KEY_KP6,
    'KP_7': uinput.KEY_KP7,
    'KP_8': uinput.KEY_KP8,
    'KP_9': uinput.KEY_KP9,
    'KP_Multiply': uinput.KEY_KPASTERISK,
    # KEY_KPCOMMA
    'KP_Decimal': uinput.KEY_KPDOT,
    'KP_Enter': uinput.KEY_KPENTER,
    # KEY_KPEQUAL
    # KEY_KPJPCOMMA
    # KEY_KPLEFTPAREN
    'KP_Subtract': uinput.KEY_KPMINUS,
    'KP_Add': uinput.KEY_KPPLUS,
    # KEY_KPPLUSMINUS
    # KEY_KPRIGHTPAREN
    'KP_Divide': uinput.KEY_KPSLASH,
    'l': uinput.KEY_L,
    # KEY_LANGUAGE
    # KEY_LAST
    # KEY_LEFT
    # KEY_LEFTALT
    '[': uinput.KEY_LEFTBRACE,
    # KEY_LEFTCTRL
    # KEY_LEFTMETA
    # KEY_LEFTSHIFT
    # KEY_LIGHTS_TOGGLE
    # KEY_LINEFEED
    # KEY_LIST
    # KEY_LOGOFF
    'm': uinput.KEY_M,
    # KEY_MACRO
    # KEY_MAIL
    # KEY_MAX
    # KEY_MEDIA
    # KEY_MEDIA_REPEAT
    # KEY_MEMO
    # KEY_MENU
    # KEY_MESSENGER
    # KEY_MHP
    # KEY_MICMUTE
    '-': uinput.KEY_MINUS,
    # KEY_MODE
    # KEY_MOVE
    # KEY_MP3
    # KEY_MSDOS
    # KEY_MUHENKAN
    # KEY_MUTE
    'n': uinput.KEY_N,
    # KEY_NEW
    # KEY_NEWS
    # KEY_NEXT
    # KEY_NEXTSONG
    # KEY_NUMERIC_0
    # KEY_NUMERIC_1
    # KEY_NUMERIC_2
    # KEY_NUMERIC_3
    # KEY_NUMERIC_4
    # KEY_NUMERIC_5
    # KEY_NUMERIC_6
    # KEY_NUMERIC_7
    # KEY_NUMERIC_8
    # KEY_NUMERIC_9
    # KEY_NUMERIC_POUND
    # KEY_NUMERIC_STAR
    'Num_Lock': uinput.KEY_NUMLOCK,
    'o': uinput.KEY_O,
    # KEY_OK
    # KEY_OPEN
    # KEY_OPTION
    'p': uinput.KEY_P,
    # KEY_PAGEDOWN
    # KEY_PAGEUP
    # KEY_PASTE
    # KEY_PAUSE
    # KEY_PAUSECD
    # KEY_PC
    # KEY_PHONE
    # KEY_PLAY
    # KEY_PLAYCD
    # KEY_PLAYER
    # KEY_PLAYPAUSE
    # KEY_POWER
    # KEY_POWER2
    # KEY_PRESENTATION
    # KEY_PREVIOUS
    # KEY_PREVIOUSSONG
    # KEY_PRINT
    # KEY_PROG1
    # KEY_PROG2
    # KEY_PROG3
    # KEY_PROG4
    # KEY_PROGRAM
    # KEY_PROPS
    # KEY_PVR
    'q': uinput.KEY_Q,
    'r': uinput.KEY_R,
    # KEY_RADIO
    # KEY_RECORD
    # KEY_RED
    # KEY_REDO
    # KEY_REFRESH
    # KEY_REPLY
    # KEY_RESERVED
    # KEY_RESTART
    # KEY_REWIND
    # KEY_RFKILL
    # KEY_RIGHT
    # KEY_RIGHTALT
    ']': uinput.KEY_RIGHTBRACE,
    # KEY_RIGHTCTRL
    # KEY_RIGHTMETA
    # KEY_RIGHTSHIFT
    # KEY_RO
    's': uinput.KEY_S,
    # KEY_SAT
    # KEY_SAT2
    # KEY_SAVE
    # KEY_SCALE
    # KEY_SCREEN
    # KEY_SCREENSAVER
    # KEY_SCROLLDOWN
    # KEY_SCROLLLOCK
    # KEY_SCROLLUP
    # KEY_SEARCH
    # KEY_SELECT
    ';': uinput.KEY_SEMICOLON,
    # KEY_SEND
    # KEY_SENDFILE
    # KEY_SETUP
    # KEY_SHOP
    # KEY_SHUFFLE
    '/': uinput.KEY_SLASH,
    # KEY_SLEEP
    # KEY_SLOW
    # KEY_SOUND
    ' ': uinput.KEY_SPACE,
    # KEY_SPELLCHECK
    # KEY_SPORT
    # KEY_SPREADSHEET
    # KEY_STOP
    # KEY_STOPCD
    # KEY_SUBTITLE
    # KEY_SUSPEND
    # KEY_SWITCHVIDEOMODE
    # KEY_SYSRQ
    't': uinput.KEY_T,
    '\t': uinput.KEY_TAB,
    # KEY_TAPE
    # KEY_TASKMANAGER
    # KEY_TEEN
    # KEY_TEXT
    # KEY_TIME
    # KEY_TITLE
    # KEY_TOUCHPAD_OFF
    # KEY_TOUCHPAD_ON
    # KEY_TOUCHPAD_TOGGLE
    # KEY_TUNER
    # KEY_TV
    # KEY_TV2
    # KEY_TWEN
    'u': uinput.KEY_U,
    # KEY_UNDO
    # KEY_UNKNOWN
    # KEY_UP
    # KEY_UWB
    'v': uinput.KEY_V,
    # KEY_VCR
    # KEY_VCR2
    # KEY_VENDOR
    # KEY_VIDEO
    # KEY_VIDEOPHONE
    # KEY_VIDEO_NEXT
    # KEY_VIDEO_PREV
    # KEY_VOICECOMMAND
    # KEY_VOICEMAIL
    # KEY_VOLUMEDOWN
    # KEY_VOLUMEUP
    'w': uinput.KEY_W,
    # KEY_WAKEUP
    # KEY_WLAN
    # KEY_WORDPROCESSOR
    # KEY_WPS_BUTTON
    # KEY_WWAN
    # KEY_WWW
    'x': uinput.KEY_X,
    # KEY_XFER
    'y': uinput.KEY_Y,
    # KEY_YELLOW
    # KEY_YEN
    'z': uinput.KEY_Z,
    # KEY_ZENKAKUHANKAKU
    # KEY_ZOOM
    # KEY_ZOOMIN
    # KEY_ZOOMOUT
    # KEY_ZOOMRESET

    # unshifter chars
    'asciitilde': uinput.KEY_GRAVE,
    'exclam': uinput.KEY_1,
    'at': uinput.KEY_2,
    'numbersign': uinput.KEY_3,
    'dollar': uinput.KEY_4,
    'percent': uinput.KEY_5,
    'asciicircum': uinput.KEY_6,
    'ampersand': uinput.KEY_7,
    'asterisk': uinput.KEY_8,
    'parenleft': uinput.KEY_9,
    'parenright': uinput.KEY_0,
    'underscore': uinput.KEY_MINUS,
    'plus': uinput.KEY_EQUAL,
    'bar': uinput.KEY_BACKSLASH,
    'question': uinput.KEY_BACKSLASH,
    'bracketright': uinput.KEY_RIGHTBRACE,
    'bracketleft': uinput.KEY_LEFTBRACE,
    'colon': uinput.KEY_SEMICOLON,
    'greater': uinput.KEY_DOT,
    'less': uinput.KEY_COMMA,

}


def sort_uniq(sequence):
    """
    return an iterator of uniquely sorted items.
    """
    return imap(
        operator.itemgetter(0),
        groupby(sorted(sequence)))


class Emitter():
    """
    class of emitters, each with it's own device and events.
    """

    def __init__(self,
                 name=None,
                 event_dict=default_event_dict,
                 initial_delay=5,
                 emit_delay=0.01,
                 loop_forever=False,
                 loop_limit=14000):
        self.name = name
        self.initial_delay = initial_delay
        self.emit_delay = emit_delay
        self.event_dict = event_dict
        self.loop_forever = loop_forever
        self.loop_limit = loop_limit
        self.emit_lock = Lock()

        # collect all events, and sort them uniquely
        # (things like shift can be repeated a lot)
        events = []
        for k, v in event_dict.iteritems():
            #print(k,v)
            events.append(v)
        self.events = sort_uniq(events)
        #if verbose:
        #    print('Events:', list(self.events), file=stderr)

        if name is None:
            self.device = uinput.Device(sort_uniq(events))
        else:
            self.device = uinput.Device(sort_uniq(events), name=name)
        """
         arguments for Device():
         |  `events`  - a sequence of event capability descriptors
         |
         |  `name`    - name displayed in /proc/bus/input/devices
         |
         |  `bustype` - bus type identifier, see linux/input.h
         |
         |  `vendor`  - vendor identifier
         |
         |  `product` - product identifier
         |
         |  `version` - version identifier
        """
    def xlate_mods(self,mod):
        mod_list = []
        print(mod)
        for i in mod:
            # convert mods
            print(modifier[i])
            mod_list.append(modifier[i])
        return mod_list
    """
        emit data (a keycode) to device as input events.
    """
    def emit_keycode(self, mod, keysym):
        with self.emit_lock:
            if verbose:
                print('emit 0:', keysym, file=stderr)

            e = self.event_dict.get(keysym, None)
            mod_list = self.xlate_mods(mod)
            if e is not None:
                if mod_list:

                    mod_list.append(e)

                    if verbose:
                        print('emit 2:', keysym, e, type(e), mod_list, file=stderr)
                    if not silent:
                        self.device.emit_combo(mod_list)
                else:
                    if verbose:
                        print('emit 1:', keysym, e, type(e), mod_list, file=stderr)
                    if not silent:
                        self.device.emit_click(list(e))
            else:
                print('\nkeycode |{0}| not found.'.format(keysym), file=stderr)

    def xemit_keycode(self, mod, keysym):
        with self.emit_lock:
            e = self.event_dict.get(keysym, None)
            modkey = modifier.get(mod, None)
            if e is not None:
                if modkey is None:
                    if len(e) == 1:
                        if verbose:
                            print('emit 1:', keysym, file=stderr)
                        if not silent:
                            self.device.emit_click(e[0])
                    elif len(e) == 2:
                        if verbose:
                            print('emit 2:', keysym, file=stderr)
                        if not silent:
                            self.device.emit_combo(e)
                    else:
                        print(
                            '\nwrong tuple size (not 1 or 2) for event for',
                            '|{0}|.'.format(keysym), file=stderr)
                else:
                    if verbose:
                        print('emitting {0} + {1}'.format(mod, keysym), file=stderr)
                    if not silent:
                        # unpack tuple, prepend modifier, repack as tuple
                        self.device.emit_combo(tuple(chain(modifier[mod], keysym)))
            else:
                print('\nkeycode |{0}| not found.'.format(keysym), file=stderr)


class EmitterService(rpyc.Service):
    emitter = None

    def on_connect(self):
        """
        code that runs when a connection is created
        (to init the serivce, if needed)
        """
        if verbose:
            print('Connection!', file=stderr)
        time.sleep(1)
        if self.emitter is None:
            if verbose:
                print('creating emitter...', file=stderr)
            self.emitter = Emitter(
                    name='emitter',
                    event_dict=default_event_dict,
                    initial_delay=0,
                    emit_delay=0.01,
                    loop_forever=False,
                    loop_limit=14000)

    def on_disconnect(self):
        """
        code that runs when the connection has already closed
        (to finalize the service, if needed)
        """
        pass

    # this is an exposed method
    def exposed_NS_keysym(self, mod, keycode):
        ims = u'keycode {0:s}'.format(keycode)
        print ("got call")
        #if verbose:
        #    print('IMS: {0} + {1}'.format(mod, ims), file=stderr)
        print ("pre emit %s"%verbose)    
        self.emitter.emit_keycode(mod, keycode)

if __name__ == '__main__':
    t = ThreadedServer(EmitterService, '172.30.40.1', port = 12345)
    t.start()
