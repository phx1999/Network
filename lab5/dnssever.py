from socket import *
import sys
import os
curPath = os.path.abspath(os.path.dirname("D:\python\Lib\site-packages\dnslib"))
sys.path.append(curPath)
from dnslib import DNSRecord
import time

serverName = "172.18.1.93"
serverPort = 120
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")

cache = {}
fresh_time = {}


def get_reply(question, serverName):     ##从上层获得response
    print("get from up")
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(question, (serverName, 53))
    reply, serverAddress = clientSocket.recvfrom(2048)
    return reply


while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    request = DNSRecord.parse(message)
    domain = request.questions
    Id = request.header.id
    print(domain)
    print(time.time())
    print(fresh_time.get(repr(domain)))
    if cache.get(repr(domain)) and time.time() <= fresh_time.get(repr(domain)):
        print("in cache")
        reply = cache.get(repr(domain))
        final_reply = DNSRecord.parse(reply)
        final_reply.header.id = Id               #重写id
        for i in final_reply.rr:
            i.ttl = int(fresh_time[repr(domain)] - time.time())             #更新time to live
        reply = DNSRecord.pack(final_reply)
    else:
        reply = get_reply(message, serverName)  ##  如果超时或者不存在在cache中的话  转发给上层获得response
        final_reply = DNSRecord.parse(reply)
        ttl = 300
        for i in final_reply.rr:
            if i.ttl==0:
                continue
            if i.ttl < ttl:
                ttl = i.ttl
        for i in final_reply.rr:  # 取最小的ttl
            i.ttl = ttl
        reply = DNSRecord.pack(final_reply)
        cache[repr(domain)] = reply
        print(time.time())
        print(final_reply.a.ttl)
        fresh_time[repr(domain)] = time.time() + ttl            ## 储存response和ttl

    print(fresh_time)
    serverSocket.sendto(reply, clientAddress)
    print("sent")