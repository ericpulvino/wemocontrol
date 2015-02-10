import time
import signal
import peewee
import datetime
from peewee import *
from miranda import upnp
import xml.etree.ElementTree as ET
from contextlib import contextmanager

db = SqliteDatabase('/home/pi/scripts/WEMO/database.db')

wemos = [
("192.168.1.6","driveway","Driveway"),
("192.168.1.7","kitchensink","Kitchen Sink"),
("192.168.1.8","musicroom","Music Room"),
("192.168.1.9","frontporch","Front Porch"),
("192.168.1.10","backporch","Back Porch"),
]


class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)



##################
# Objects/Classes
##################
class wemo_state(peewee.Model):
    wemo_name = peewee.CharField()
    state = peewee.CharField()
    vacation_mode = peewee.BooleanField()
    vacation_toggle_time = peewee.FloatField()
    last_update_time = peewee.FloatField()

    class Meta:
        order_by = ("wemo_name",)
        database = db


class wemo_device():
    def __init__(self,ip,shortname,longname):
        self.ip_address = ip
        self.shortname = shortname
        self.longname = longname
        self.timeout_val = 5
        self.logfile = "/var/log/wemo/switchlog"
        #self.update() #don't want to update at creation time because database may not exist yet on first execution

    def _log(self,state):
        #GENERATE TIMESTAMP
        ts = time.time()
        current_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%R')
        LOGGER = open(self.logfile, 'a')
        if state == "1":
            LOGGER.write( str(current_time) + " - " + str(self.longname)+ " is now on.\n")
        elif state == "0":
            LOGGER.write( str(current_time) + " - " + str(self.longname)+ " is now off.\n")
        elif state == "2":
            LOGGER.write( str(current_time) + " - " + str(self.longname)+ " is unknown.\n")
        LOGGER.close()

    def update(self,current_state="ABC123",read=0):

        #reads stored state
        if read == 1:
            old_state,updated_ago = self.read()

        #collects current state
        if current_state == "ABC123":
            conn = upnp()
            try:
                with time_limit(self.timeout_val):
                    resp = conn.sendSOAP(str(self.ip_address) +':49153', 'urn:Belkin:service:basicevent:1','http://'+ str(self.ip_address) + ':49153/upnp/control/basicevent1', 'GetBinaryState', {})
                tree = ET.fromstring(resp)    
                current_state = tree.find('.//BinaryState').text
                if str(current_state) != "1" and str(current_state) != "0": current_state = "2"
            except:
                print "ERROR: Update: Timed out!"
                current_state = "2"

        if read == 1:
            if old_state != current_state:
                self._log(current_state)
        #updates database with current state
        #print "DEBUG: " + self.shortname + " -- updating database with current_state as: " + str(current_state)
        q = wemo_state.update(state=current_state, last_update_time=time.time()).where(wemo_state.wemo_name == self.shortname)
        q.execute()

        return current_state

    def toggle(self,):
        #collects current state
        current_state = self.update()
        #attempts to Toggle current state
        conn = upnp()
        if current_state == "0":
            try:
                with time_limit(self.timeout_val):
                    resp = conn.sendSOAP(str(self.ip_address) +':49153', 'urn:Belkin:service:basicevent:1','http://'+ str(self.ip_address) + ':49153/upnp/control/basicevent1', 'SetBinaryState', {'BinaryState': (1, 'Boolean')})
                #new state is returned in the response...checks current state again to confirm success
                tree = ET.fromstring(resp)    
                new_state = tree.find('.//BinaryState').text
                if new_state != "1" and new_state != "0": new_state = "2"
            except:
                print "ERROR: TOGGLE Operation: Timed out!"
                new_state = "2"        
        else:
            try:
                with time_limit(self.timeout_val):
                    resp = conn.sendSOAP(str(self.ip_address) +':49153', 'urn:Belkin:service:basicevent:1','http://'+ str(self.ip_address) + ':49153/upnp/control/basicevent1', 'SetBinaryState', {'BinaryState': (0, 'Boolean')})
                #new state is returned in the response...checks current state again to confirm success
                tree = ET.fromstring(resp)    
                new_state = tree.find('.//BinaryState').text
                if new_state != "1" and new_state != "0": new_state = "2"
            except:
                print "ERROR: TOGGLE Operation: Timed out!" 
                new_state = "2"
        self._log(new_state)
        self.update(new_state)

        #returns success or failure for toggle operation
        if new_state != "1" and new_state != "0": 
            return "0"
        elif new_state != current_state: return "1"

    def read(self, also_print=0):
        result = wemo_state.select().where(wemo_state.wemo_name == self.shortname)
        for row in result:
            update_time = datetime.datetime.fromtimestamp(row.last_update_time).strftime('%m/%d at %T') 
            updated_ago = time.time() - row.last_update_time
            if also_print: print self.shortname + " is currently in state: " + row.state + ". Last Update = " + (update_time) + "(" + str(updated_ago) + " seconds ago)"
            return (row.state,updated_ago)

    def on(self,):
        #collects current state
        current_state = self.update()
        #if needed, change state to on
        if current_state == "0" or current_state == "2":
            conn = upnp()
            try:
                with time_limit(self.timeout_val):
                    resp = conn.sendSOAP(str(self.ip_address) +':49153', 'urn:Belkin:service:basicevent:1', 'http://' + str(self.ip_address) + ':49153/upnp/control/basicevent1', 'SetBinaryState', {'BinaryState': (1, 'Boolean')})
                #new state is returned in the response...checks current state again to confirm success
                tree = ET.fromstring(resp)    
                new_state = tree.find('.//BinaryState').text
                if new_state != "1" and new_state != "0": new_state = "2"
            except:
                print "ERROR: ON Operation: Timed out!"   
                new_state = "2"
            self._log(new_state)
            self.update(new_state)
        
            #confirm state change
            if new_state == "1": return "1"
            else: return "0"
        #returns success or failure
        elif current_state=="1": return "1"
        else: return "0"


    def off(self,):
        #collects current state
        current_state = self.update()
        #if needed, change state to off
        if current_state == "1" or current_state == "2":
            conn = upnp()
            try:
                with time_limit(self.timeout_val):
                    resp = conn.sendSOAP(str(self.ip_address) +':49153', 'urn:Belkin:service:basicevent:1', 'http://' + str(self.ip_address) + ':49153/upnp/control/basicevent1', 'SetBinaryState', {'BinaryState': (0, 'Boolean')})
                #new state is returned in the response...checks current state again to confirm success
                tree = ET.fromstring(resp)    
                new_state = tree.find('.//BinaryState').text
                if new_state != "1" and new_state != "0": new_state = "2"
            except:
                print "ERROR: OFF Operation: Timed out!" 
                new_state = "2"
            self._log(new_state)
            self.update(new_state)

            #confirm state change
            if new_state == "0": return "1"
            else: return "0"
        #returns success or failure
        elif current_state=="0": return "1"
        else: return "0"

def first_connection(list_of_wemos):
    wemo_state.drop_table(fail_silently=True) #Drop existing table
    wemo_state.create_table()
    for wemo in list_of_wemos:
        q = wemo_state.insert(wemo_name=wemo[1],state=0, vacation_mode=False, vacation_toggle_time=0, last_update_time=time.time())
        q.execute()  # perform the insert.

def all_of(wemo_dict):
    status = 0
    for wemo in wemo_dict:
        wemo_status,updated_ago = wemo_dict[wemo].read()
        if wemo_status == "1" or wemo_status == "2": status += 1
    if status > 0: return 1
    elif status == 0: return 0

def sendall(command,wemo_dict):
    if command == "on":
        for wemo in wemo_dict:
            wemo_dict[wemo].on()
    elif command == "off":
        for wemo in wemo_dict:
            wemo_dict[wemo].off()
    elif command == "toggle":
        for wemo in wemo_dict:
            wemo_dict[wemo].toggle()

#Connect to DB 
db.connect()

if __name__ == "__main__":
    print "Creating WEMO Database..."
    first_connection(wemos)
    print "Done."

wemo_dict = {}
for wemo in wemos:
    #print "    creating wemo entry for: " + str(wemo[1])
    wemo_dict[wemo[1]] = wemo_device(wemo[0],wemo[1],wemo[2])




#driveway = wemo_device("192.168.1.6","driveway","Driveway Light")
#kitchensink = wemo_device("192.168.1.7","kitchensink","Kitchen Sink Light")
#musicroom = wemo_device("192.168.1.8","musicroom","Music Room Light")
#frontporch = wemo_device("192.168.1.9","frontporch","Front Porch Light")
#backporch = wemo_device("192.168.1.10","backporch","Back Porch Light")

if __name__ == "__main__":
    for wemo in wemo_dict:
        print "WEMO named: \""+ str(wemo) +"\" is presently in state: \"" + str(wemo_dict[wemo].update()) + "\""
