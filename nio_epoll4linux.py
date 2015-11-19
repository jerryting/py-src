# -*- coding: utf-8 -*-
"""
@author: dj@ixinyou.com
@version: v1
@copyright:2014@xinyou Corp


@since: 2014-07-25
@summary: 
    non-block io server with linux epoll, single epoll object process select.EPOLLIN & select.EPOLLOUT
    tip: may use multiple epoll object to poll socket channels in multiple-core machine
"""

import select
import socket
import struct

class socket_serv(object):
    def __init__(self):
        
        self.__POLL_INTERVAL_IN_SECONDS_ = 0.001
        self.FD_DIC = {}
        self.FD_BYTES_LEN_DIC = {}
        self.DEFAULT_BYTES_LEN = 2
        pass
    def init_socket_server(self,ipAddr, port):
        # AF_INET FAMILY
        try:
            self.socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socketServer.setblocking(0)
            self.socketServer.bind((ipAddr, port))
            self.socketServer.listen(10)  # max queued connection
            self.epoll = select.epoll()
            self.epoll.register(self.socketServer.fileno(), select.EPOLLIN | select.EPOLLET)  # epoll edge-trigger behavior
            return self.socketServer, self.epoll
        except Exception, e:
            print e
    
    def run_nioserv(self):
        try:
            while True:
                events = self.epoll.poll(self.__POLL_INTERVAL_IN_SECONDS_)
                for fd, event in events:
                    if fd == self.socketServer.fileno() :  # accept
                        conn, addr = self.socketServer.accept()
                        conn.setblocking(0)
                        clientfd = conn.fileno()
                        self.epoll.register(clientfd, select.EPOLLIN | select.EPOLLET)
                        self.FD_DIC[clientfd] = conn
                        self.FD_BYTES_LEN_DIC[fd] = self.DEFAULT_BYTES_LEN
                        self.sync_message_traveler.init_message_queue(clientfd)
                        print addr, ' enter server channel'
                    elif event & select.EPOLLIN:  # readable
                        recvData = self.read_from_channel(fd)
                        self.sync_message_traveler.travel(fd,recvData)
                    elif event & select.EPOLLOUT:  # writeable
                        self.write_to_channel(fd, 'recved')
                        pass
                    elif event & select.EPOLLHUP:
                        self.close_channel(fd)
        except Exception, e:
            print e
        finally:
            self.epoll.unregister(self.socketServer.fileno())
            self.epoll.close()
            self.socketServer.close()
    #
    def close_channel(self,fd):
        try:
            self.epoll.unregister(fd)
            self.FD_DIC[fd].close()
            del self.FD_DIC[fd]
            self.sync_message_traveler.del_queue(fd)
        except Exception, e:
            print e
    #
    def read_from_channel(self,fd):
        recvedData = ''
        try:
            while True:
                data = self.FD_DIC[fd].recv(self.FD_BYTES_LEN_DIC[fd])
#                 recvedData += data
                if len(data) <= 0:  #
                    self.close_channel(fd)
                    break
                try:
                    unpackData = struct.unpack('<H',data)#little-endian
                    
                    nextLen = unpackData[0]
                    if nextLen > 2:
                        self.FD_BYTES_LEN_DIC[fd]
                except struct:
                    self.FD_BYTES_LEN_DIC[fd] = self.DEFAULT_BYTES_LEN
        except socket.error, e:
            pass  #
        except Exception, e1:
            print e1
        return recvedData
    
    def write_to_channel(self,fd, sendData):
        try:
    #                 while True:
            self.FD_DIC[fd].send(sendData)
        except socket.error, e:
            print e
        pass
    
    # set message router(sync)
    def set_sync_callback(self,smtr):
        self.sync_message_traveler = smtr

# if __name__ == '__main__':
#     server, epoll = init_socket_server('0.0.0.0', 999)
#     mt = message_travel.message_traveler()
#     set_sync_callback(mt)
#     run_nioserv(server, epoll)