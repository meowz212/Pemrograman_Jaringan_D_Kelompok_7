from socket import *
import socket
import threading
import time
import sys
import logging

def forward_process(data):
	url_dict = {}
	url_dict['/images/'] = ("localhost", 8889)
	url_dict['/pdf/'] = ("localhost", 8890)
	default_server = ("localhost", 8888)
	forward_response = {}
	requests = data.split("\r\n")
	baris = requests[0]

	all_headers = [n for n in requests[1:] if n != '']
	j = baris.split(" ")
	method = j[0].upper().strip()
	url_address = j[1].strip()

	for url, server in url_dict.items():

		if (url in url_address):
			forward_response['server'] = server
			forward_response['request'] = data

		if "server" not in forward_response:
			forward_response['server'] = default_server
			forward_response['request'] = data

	print(forward_response)
	return forward_response

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)


	def run(self):
		rcv=""
		while True:
			try:
				data = self.connection.recv(8192)
				data = data.decode()
				self.destination_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

				if data:
					response = forward_process(data)
					self.destination_sock.connect(response['server'])
					self.destination_sock.sendall(response['request'].encode())
					# data_balasan = self.destination_sock.recv(8192)
					# self.connection.sendall(data_balasan)
					while(True):
						data_balasan = self.destination_sock.recv(32)
						if(data_balasan == ''):
							break
						self.connection.sendall(data_balasan)
					logging.warning(data)
					logging.warning(data_balasan)

				else:
					break
			except OSError as e:
				pass
		self.connection.close()



class Server(threading.Thread):
	def __init__(self):
		self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		threading.Thread.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0', 18000))
		self.my_socket.listen(1)
		while True:
			self.connection, self.client_address = self.my_socket.accept()
			logging.warning("connection from {}".format(self.client_address))

			clt = ProcessTheClient(self.connection, self.client_address)
			clt.start()
			self.the_clients.append(clt)



def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()

