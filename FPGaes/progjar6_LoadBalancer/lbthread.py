from socket import *
import socket
import threading
import time
import sys
import logging

class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('localhost',9001))
		self.servers.append(('localhost',9002))
		self.servers.append(('localhost',9003))
		self.servers.append(('localhost',9004))
		self.servers.append(('localhost',9005))
		self.current=0

	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address, destserver):
		self.connection = connection
		self.address = address
		self.destserver = destserver
		threading.Thread.__init__(self)

	def run(self):
		rcv = ""
		while True:
			try:
				data = self.connection.recv(8192)
				data = data.decode()
				self.dest_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if data:
					server = self.destserver
					logging.warning("koneksi diteruskan ke {}".format(server))
					self.dest_sock.connect(server)
					self.dest_sock.sendall(data.encode())
					# while (True):
					recvdata = self.dest_sock.recv(8192)
					# 	if (recvdata == ''):
					# 		break
					self.connection.sendall(recvdata)
					# logging.warning(data)
					# logging.warning(recvdata)
					break
				else:
					break
			except OSError as e:
				pass
		self.connection.close()



class Server(threading.Thread):
	def __init__(self):
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.bservers = BackendList()
		threading.Thread.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0', 666))
		self.my_socket.listen(5)

		while True:
			self.connection, self.client_address = self.my_socket.accept()
			logging.warning("connection from {}".format(self.client_address))

			clt = ProcessTheClient(self.connection, self.client_address, self.bservers.getserver())
			clt.start()

def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()

