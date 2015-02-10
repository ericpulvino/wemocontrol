#!/usr/bin/python

import sys
import wemo_backend
from time import sleep

def help_text():
    print "Usage: Argument is incorrectly formatted!"
    print "       sample usage: #script.py [wemo_name].[action]"
    print "       sample usage: #script.py backporch.off"
    print "       sample usage: #script.py multiupdate"
    print "       sample usage: #script.py sendall.on"
    print "    possible [actions] include: on,off,toggle,update,read"

for item in sys.argv:
    if item == sys.argv[0]: continue
    elif item == "update":
        for wemo in wemo_backend.wemo_dict:
            wemo_backend.wemo_dict[wemo].update(read=1)
    elif item == "multiupdate":
        for wemo in wemo_backend.wemo_dict:
            wemo_backend.wemo_dict[wemo].update(read=1)
        sleep(28)
        for wemo in wemo_backend.wemo_dict:
            wemo_backend.wemo_dict[wemo].update(read=1)
    elif item == "all_state":
        print "current state is: " + str(wemo_backend.all_of(wemo_backend.wemo_dict))

    else:
        try:
            wemo,action = item.split(".")

        except:
            help_text()
            exit(1)

        if wemo == "sendall":
            if action == "on":
                wemo_backend.sendall("on",wemo_backend.wemo_dict)
            elif action == "off":
                wemo_backend.sendall("off",wemo_backend.wemo_dict)
            elif action == "toggle":
                wemo_backend.sendall("toggle",wemo_backend.wemo_dict)
        elif action == "on":
            wemo_backend.wemo_dict[wemo].on()
        elif action == "off":
            wemo_backend.wemo_dict[wemo].off()
        elif action == "toggle":
            wemo_backend.wemo_dict[wemo].toggle()
        elif action == "update":
            wemo_backend.wemo_dict[wemo].update()
        elif action == "read":
            wemo_backend.wemo_dict[wemo].read(1)
        else:
            help_text()
