# wemocontrol

Quick Description:
This project provides a webpage and automated interface for controlling Belkins WEMO 
light switches and plug switches.

NOTE: 
   This project does not control WEMO motion sensors or power monitors.

Dependencies:
    sudo apt-get install aptitude
    sudo aptitude install python-pip
    sudo python-pip install peewee

Setup:
1). Setup Apache to run Python Scripts
    -This may vary for your environment /w mod_python but here is some info on the process:
        https://docs.python.org/2/howto/webservers.html
2). Setup WEMO Information
    -Edit the top of your ./wemo_backend.py file to make nicknames for your WEMOs and their IP addresses.
    -(You should have already setup your WEMOs to have static IP addresses that do not change)
3). On first run, execute the ./wemo_backend.py file. 
    -This will create and initialize the backend database at the specified location.
4). Setup a Crontab to update state of various WEMOs at your interval of choosing.
    -My sample crontab is provided below.

-----------------------------
### SAMPLE CRONTAB ###
-----------------------------

# m h  dom mon dow   command
##################################
#Update WEMO States (Every Minute)
##################################
* * * * * /home/pi/scripts/WEMO/send_wemo_commands.py multiupdate

###############################
#TURN ON and Failsafes (For Power Outtage)
###############################
#00 16 * * * sunwait sun down 34.918917N 79.455301W && /home/pi/scripts/WEMO/send_wemo_commands.py frontporch.on kitchensink.on driveway.on
00 21 * * * /home/pi/scripts/WEMO/send_wemo_commands.py frontporch.on kitchensink.on driveway.on
00 18 * * * /home/pi/scripts/WEMO/send_wemo_commands.py frontporch.on kitchensink.on driveway.on backporch.on musicroom.on
00 00 * * * /home/pi/scripts/WEMO/send_wemo_commands.py backporch.on


##############################
#TURNING OFF (and failsafes)
##############################
30 1 * * * /home/pi/scripts/WEMO/send_wemo_commands.py kitchensink.off 
00 5 * * * /home/pi/scripts/WEMO/send_wemo_commands.py frontporch.off kitchensink.off driveway.off backporch.off musicroom.off
#00 4 * * * sunwait sun up -0:15:00 34.918917N 79.455301W && /home/pi/scripts/WEMO/send_wemo_commands.py frontporch.off kitchensink.off driveway.off backporch.off musicroom.off

