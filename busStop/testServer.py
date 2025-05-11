# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import *
import sqlite3
con = sqlite3.connect("./data.db")
cur = con.cursor()

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

try:
    while True:
        byte_data = client_sock.recv(1024)
        if len(byte_data) == 0: break
        #Converts data to string
        data = byte_data.decode('utf-8').rstrip('\n').rstrip('\r')

        if(data == "match"):
            cur.execute(f"INSERT INTO USERPASSAGES (uuid, datehour) VALUES (\"{client_info[0]}\", \"15:18\")")
            con.commit()
            res = cur.execute("SELECT direction FROM NEXTPASSAGES")
            outTuple = res.fetchall()
            client_sock.send("1 " + outTuple[0][0] + "\n2 " + outTuple[1][0] + "\n3 "+ outTuple[2][0])
        else:
            print("No match")
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")
