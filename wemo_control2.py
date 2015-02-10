#!/usr/bin/python
import cgitb
import os
import cgi
import wemo_backend
from miranda import upnp

cgitb.enable()

SWITCH_LOGFILE = "/var/log/wemo/switchlog"
key= "raspi123"

def tail(num,location):
  stdin,stdout = os.popen2("tail -n" + str(num) + " " + str(location))
  stdin.close()
  lines = stdout.readlines(); stdout.close()
  output = ""
  for x in range (0,len(lines)):
      output += lines[x] + "<br>"
  return output


def error_output():
    print "Content-Type: text/html" 
    print ""
    print "<html><head><title>LEAVE NOW</title></head>"
    print "<body>"
    print "<H1>You are not authorized. GET OUT!!!</h1>"         
    print "</body>"
    print "</html>"

def normal_output():
    header = '''Content-Type: text/html 

<html>
<head>
<title>WEMO Control</title>
<META HTTP-EQUIV="refresh" CONTENT="30">
<style>
table {
    width:100%;
}
th, td {
    padding: 20px;
    text-align: center;
}
</style>
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body>
<H1>WEMO Control Interface</H1>
<br> <table>'''

    payload = "<tr>"
    count = 1
    all_state = wemo_backend.all_of(wemo_backend.wemo_dict)
    if all_state == 0:
        payload += """<td><br><h2> All On </h2><br><a href="./wemo_control2.py?key=raspi123&allof=1"><img src="../../images/off.png"></a></td>"""
    if all_state == 1:
        payload += """<td><br><h2> All Off </h2><br><a href="./wemo_control2.py?key=raspi123&allof=0"><img src="../../images/on.png"></a></td>"""
    for wemo in wemo_backend.wemo_dict:
        if count%3 == 0 and count != 0: payload += "</tr><tr>"
        status,updated_ago = wemo_backend.wemo_dict[wemo].read()
        payload += """<td><h2>""" + str(wemo_backend.wemo_dict[wemo].longname) + """</h2>"""
        payload += "<h4> as of "+ str(int(updated_ago)) + " seconds ago</h4>"
        payload += """<a href="./wemo_control2.py?key=""" + key + """&""" 
        if status == "0":
            payload += str(wemo_backend.wemo_dict[wemo].shortname) + """=1"><img src="../../images/off.png"></a>"""
        elif status == "1":
            payload += str(wemo_backend.wemo_dict[wemo].shortname) + """=0"><img src="../../images/on.png"></a>"""
        elif status == "2":
            payload += str(wemo_backend.wemo_dict[wemo].shortname) + """=2"><img src="../../images/error.png"></a></td>"""
        count +=1
    payload += """</tr></table><br><a href="./wemo_control2.py?key=""" + key + """&logoutput=1"><h2>View Logfile</h2></a>"""
    print header
    print payload
    
input_data = cgi.FieldStorage()
if "key" not in input_data:
    error_output()
    exit()
else:
    if input_data["key"].value == key:
        for wemo in wemo_backend.wemo_dict:
            if str(wemo_backend.wemo_dict[wemo].shortname) in input_data:
                if int(input_data[wemo_backend.wemo_dict[wemo].shortname].value) == 1:
                    wemo_backend.wemo_dict[wemo].on()
                elif int(input_data[wemo_backend.wemo_dict[wemo].shortname].value) == 0:
                    wemo_backend.wemo_dict[wemo].off()
                elif int(input_data[wemo_backend.wemo_dict[wemo].shortname].value) == 2:
                    wemo_backend.wemo_dict[wemo].toggle()
            elif str("allof") in input_data:
                if int(input_data["allof"].value) == 1:
                    wemo_backend.sendall("on",wemo_backend.wemo_dict)
                elif int(input_data["allof"].value) == 0:
                    wemo_backend.sendall("off",wemo_backend.wemo_dict)

        normal_output()
        if "logoutput" in input_data:
            #Collect Logfile Output
            logging_output = "<h2>Logfile Output:</h2>" + tail(30,"/var/log/wemo/switchlog")
            print logging_output

        #Build Footer
        print "</body></html> "
    else:
        error_output()
        exit()


