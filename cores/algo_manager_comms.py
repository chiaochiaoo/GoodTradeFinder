import socket
import pickle

import threading
import multiprocessing

import select
import time

import os
#### HERE I NEED SELECT. ### Dua channel. ####



def kill():

	fail = 0
	while True:
		try:
			for i in os.popen("netstat -ano|findstr 65499").read().split("\n"):
				pid=int(i[-8:])
				os.system("taskkill /f /t /pid "+str(pid))
		except:
			fail+=1
			if fail>=3:
				break


def algo_manager_commlink(pipe):

	HOST = 'localhost'  # Standard loopback interface address (localhost)
	PORT = 65491        # Port to listen on (non-privileged ports are > 1023)


	while True:

		s=  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		failed = 0
		while True:
			try:
				s.bind((HOST, PORT))
				break
			except:
				failed +=1
				kill()
				if failed >=5:
					break

		if failed>=5:
			print("algo failed to initialize")
			break

		print("Waitting for algo manager to connect")
		s.listen()
		
		conn, addr = s.accept()
		print("Algo manager connected.")
		s.setblocking(0)
		Connection = True

		while Connection:
			try:
				#if something comes from pipe.
				if pipe.poll(1):
					data = pipe.recv()
					print("New order:",data)
					data=pickle.dumps(data)
					try:
						conn.sendall(data)
						#print("sending",data)
					except Exception as e:
						print(e)
						Connection=False
						break
					
				#if client sends something 
				if Connection:
					ready = select.select([conn], [], [], 1)
					
					if ready[0]:
						data = []
						while True:
							try:
								part = conn.recv(2048)
							except:
								connection = False
								break
							#if not part: break
							data.append(part)
							if len(part) < 2048:
								#try to assemble it, if successful.jump. else, get more. 
								try:
									k = pickle.loads(b"".join(data))
									break
								except:
									pass
						#k is the confirmation from client. send it back to pipe.
						pipe.send(k)

			except Exception as e:
				Connection= False
		
	s.close()


def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

if __name__ == '__main__':

	# for i in os.popen("netstat -ano|findstr 65499").read().split("\n"):
	# 	print(i[-8:])
		#print(int(i[61:])
	server_side_comm, client_side_comm = multiprocessing.Pipe()

	
	#algo_comm_link = multiprocessing.Process(target=algo_manager_commlink, args=(client_side_comm,),daemon=True)

	#algo_comm_link = threading.Thread(target=algo_manager_commlink,args=(client_side_comm,), daemon=True)
	
	
	#algo_comm_link.daemon=True
	#algo_comm_link.start()

	# server_side_comm.send("bsbsbsbs1")
	# server_side_comm.send("bsbsbsbs2")
	# server_side_comm.send("bsbsbsbs3")
	# server_side_comm.send("bsbsbsbs4")
	# algo_comm_link.terminate()
	# algo_comm_link.join()
	algo_manager_commlink(client_side_comm)
	#algo_comm_link.start()
	print("finish")
	while True:
		a=1


