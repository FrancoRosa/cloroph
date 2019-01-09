from socket import *
import thread
import time
 
BUFF = 256
HOST = '0.0.0.0'# must be input parameter @TODO
PORT = 9998 # must be input parameter @TODO

import sys
import os
import django

sys.path.append('/root/Django/CaliAgua/myclph')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myclph.settings'
django.setup()

from measurements.models import Reservoir, ReservoirData

threadsCounter = 0;

def gen_response():
    return 'this_is_the_return_from_the_server'
 
def handler(clientsock,addr):
    global threadsCounter
    print "... client Loop"
    clientsock.send("**\n")
    clientsock.settimeout(20)
    while True:
        try:
            data = clientsock.recv(BUFF)
        except:
            print "... error on communication"
            break
        clientsock.settimeout(20*60)    
        datadate = time.strftime("%Y-%m-%d", time.localtime())
        datatime = time.strftime("%H:%M:%S", time.localtime())
        print '... %s %s: %s'%(datadate, datatime, repr(data))
        ############################################
        #Data processing:
        try:
            if ',' in data:
                data = data.split(',')
                if len(data)==10:
                    print "... received data Ok"
                    
                    imei        = data[0]
                    operator    = data[1]
                    signal      = data[2]
                    battery     = str(int(data[3])/10.0)
                    latitude    = data[4]
                    longitude   = data[5]
                    phdata      = data[6]
                    phtemperat  = data[7]
                    cldata      = data[8]
                    cltemperat  = data[9]
                r = ReservoirData(reservoir=Reservoir.objects.get(name='Sucso'),
                        date=datadate, time=datatime, 
                        latitude=latitude, longitude=longitude,
                        vBattery=battery, vPanel=0,
                        rClorine=cldata,pH=phdata,temperature=phtemperat)

                r.save()
        except:
            pass
        
        if not data: break
        if data == '':
            clientsock.close()
            break
    threadsCounter=threadsCounter-1
    print "Active Threads:", threadsCounter

if __name__=='__main__':
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)
    while True:
        print 'waiting for connection...'
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        threadsCounter=threadsCounter+1
        print "Active Threads:", threadsCounter
        thread.start_new_thread(handler, (clientsock, addr))