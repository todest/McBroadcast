import re
import time
import socket
import struct
import select

port = 4445
bufferSize = 2048
MCAST_GRP = '224.0.2.60'
BROADCAST_IP = "255.255.255.255"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
portRegex = re.compile("((?:\d+\.){1,8}\d+:?)?(\d+)")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
s.bind(('', port))
s.setblocking(False)
while True:
    read = select.select([s], [], [s], 2)[0]
    for r in read:
        msg, peer = r.recvfrom(bufferSize)
        address = peer[0]
        after = str(msg).split("[AD]")
        groups = portRegex.search(after[1])
        serverPort = groups.group(2)
        print(re.sub(r'\[AD\].*\[/AD\]', "", "[Server: \"" +
                     msg.decode("utf-8").replace("[MOTD]", "").replace("[/MOTD]", "\", ")),
              "Address: \"" + address + ":" + str(serverPort)+'"]')
        sock.sendto(msg, (BROADCAST_IP, port))
    time.sleep(1.5)
