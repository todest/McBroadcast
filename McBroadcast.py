import re
import time
import socket
import struct
import select
import psutil

port = 4445
bufferSize = 2048
MCAST_GRP = '224.0.2.60'
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

BROADCAST_IP = []
black_list = ['127', '169', '172']
mask = [0, 0, 0, 255]
for name, info in psutil.net_if_addrs().items():
    isup = False
    for tName, tInfo in psutil.net_if_stats().items():
        if name == tName:
            isup = tInfo.isup
            break
    for addr in info:
        if socket.AddressFamily.AF_INET != addr.family:
            continue
        ipv4 = addr.address.split('.')
        for i in range(len(ipv4)):
            ipv4[i] = str(int(ipv4[i]) | mask[i])
        if ipv4[0] in black_list or not isup:
            continue
        BROADCAST_IP.append('.'.join(ipv4))

print("Start Listening and Broadcasting...")

while True:
    read = select.select([s], [], [s], 2)[0]
    for r in read:
        msg, peer = r.recvfrom(bufferSize)
        address = peer[0]
        after = str(msg).split("[AD]")
        groups = portRegex.search(after[1])
        serverPort = groups.group(2)
        print(re.sub(r'\[AD\].*\[/AD\]', "", "\n[Server: \"" +
                     msg.decode("utf-8").replace("[MOTD]", "").replace("[/MOTD]", "\", ")),
              "Address: \"" + address + ":" + str(serverPort) + '"]')
        for ip in BROADCAST_IP:
            print("Broadcasting To: " + ip)
            sock.sendto(msg, (ip, port))
        time.sleep(1.5)
