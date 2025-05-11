from bluetooth import *
from datetime import datetime
import sqlite3

def uuid_isStop(macAddress, cur):
    res = cur.execute(f"SELECT * FROM STOP_IDS WHERE macAddress = \"{macAddress}\"; ")
    if(res.fetchone() == None):
        return False;     
    
    return True;
        

con = sqlite3.connect("./data.db")
cur = con.cursor()

server_sock = BluetoothSocket( RFCOMM )
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
while True:                   
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
                currentDate = datetime.now().isoformat()
                                
                #Check if received MAC is from stop or from user
                if uuid_isStop(client_info[0], cur):
                    #it's a stop
                    table = "STOPPASSAGES"
                else:
                    #it's a user
                    table = "USERPASSAGES"
                    client_sock.send("{bus_uuid:" + f"\" {uuid}\"")


                cur.execute(f"INSERT INTO {table} (macAddress, datehour) VALUES (\"{client_info[0]}\", \"{currentDate}\")")
                con.commit()
            else:
                print("No match")
    except IOError:
        pass

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")


