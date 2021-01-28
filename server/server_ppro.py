import finviz
import pandas as pd
import threading
from queue import Queue
import time
import requests
import pickle
import multiprocessing
import numpy as np
from server import *

def time_stamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print("Timestamp conversion error:")
		return 0

###### Update the info from PPRO. ##################
def market_scanner(queue,symbols,sync_lock):

	global sync_number
	global lock
	global bad_list
	global new_run

	count = 0
	roun = 1

	while True:
		#Deal with the last round, problematics
		for i in bad_list:
			if i[:-3] in symbols:
				symbols.remove(i[:-3])
		bad_list = []

		if new_run:
			print("Starting round: ",roun,"")
			start = time.time()
			new_run = False
			for i in symbols:
				# print(i,sync_number)
				while sync_number > 500:
					time.sleep(1)

				if i not in bad_list:
					reg = threading.Thread(target=getinfo, args=(i + ".NQ", queue), daemon=True)
					reg.start()
					count += 1
					# time.sleep(0.1)
					with sync_lock:
						sync_number += 1
			end = time.time()
			roun+=1
			print("Finished round",roun,"used:",round(end - start,2))
			time.sleep(4)
		else:
			print("waiting to finish the last run.")
			time.sleep(2)

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def register(symbol):

	global lock

	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)

		if symbol not in lock:
			lock[symbol] = False
		else:
			lock[symbol] = False

	except Exception as e:
		print("Register issue",e)

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0
#remain 50 threads at the same time. 

def getinfo(symbol,pipe):

	global bad_list
	global lock
	#global connection_error
	
	if symbol not in lock:
		lock[symbol] = False

	if not lock[symbol]:
		try:
			success= False
			lock[symbol] = True
			#######################################################################
			p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
			c= requests.get(p)

			#print(symbol+" started")
			time.sleep(1)
			p="http://localhost:8080/GetLv1?symbol="+symbol
			r= requests.get(p)
			#print(symbol+" request complete")
			#print(r.text)"

			response = r.text

			failure_count = 0
			while response =="<Response><Content>No data available symbol</Content></Response>":
				#bad_list.append(symbol)
				#try again 
				try:
					p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
					c= requests.get(p)
					# time.sleep(2)
					p="http://localhost:8080/GetLv1?symbol="+symbol
					r= requests.get(p)
					response = r.text
					failure_count += 1

					if failure_count == 3:
						lock[symbol] = False
						pipe.put(["Error",symbol])
						return False
				except:
					failure_count += 1


			time_=find_between(r.text, "MarketTime=\"", "\"")[:-4]
			open_ = float(find_between(r.text, "OpenPrice=\"", "\""))
			high = float(find_between(r.text, "HighPrice=\"", "\""))
			low = float(find_between(r.text, "LowPrice=\"", "\""))

			ts = time_stamp(time_[:5])
			#vol = int(find_between(r.text, "Volume=\"", "\""))
			prev_close = float(find_between(r.text, "ClosePrice=\"", "\""))
			price = float(find_between(r.text, "LastPrice=\"", "\""))

			if price<1:
				price = round(price,3)
			else:
				price = round(price,2)

			pipe.put(["Connected",symbol,time_,price,open_,high,low,prev_close,ts])
			lock[symbol] = False
				# p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
				# r= requests.get(p)

				#print(symbol+" complete")

		except Exception as e:
			print("ERROR on",symbol,e)
			#print(symbol,r.text)
			#print("Get info error:",symbol,e)
			#connection_error = True
			pipe.put(["Error",symbol])
			lock[symbol] = False

	#print(symbol+" finish")


# global connection_error
# connection_error = False

global bad_list
bad_list = []

#lock also serves as registry
global lock
lock = {}

sync_lock = threading.Lock()
queue = Queue()

global sync_number
sync_number = 0

global new_run
new_run = True


def ppro_server(pipe):
	global lock
	global sync_number
	global new_run

	df = pd.read_csv('nasdaq_ppro_live - nasdaq_ppro_live.csv', index_col=0)
	df['Ppro Timestamp'] = 0
	symbols = list(df.index)

	total_count = len(symbols)

	count = 0
	ms = threading.Thread(target=market_scanner,args=(queue,symbols,sync_lock,), daemon=True)
	ms.start()

	bad_count = 0

	while True:

		if count % total_count ==0:
			df["Close-price-ATR"]= np.round(np.abs(df["Prev Close P"] - df["Price"])/df["ATR"],2)
			df["High-Low-ATR"] =  np.round(np.abs(df["High"] - df["Low"])/df["ATR"],2)
			df["Open-High-ATR"]= np.round(np.abs(df["Open"] - df["High"])/df["ATR"],2)
			df["Open-Low-ATR"]= np.round(np.abs(df["Open"] - df["Low"])/df["ATR"],2)

			pipe.send(df)
			#send it over pipe
			df.to_csv("Test.csv")

			time.sleep(2)
			new_run = True
			print("Bad count total:",bad_count)
			bad_count=0

		data = queue.get()

		status = data[0]
		symbol = data[1][:-3]

		if status == "Connected":
			#update the df. ? maybe do it on thread  symbol,time,price,open_,high,low,vol,prev_close
			time_ =  data[2]
			price = data[3]
			open_ = data[4]
			high = data[5]
			low =  data[6]
			prev_close = data[7]

			timestamp = data[8]

			df.loc[symbol,['Ppro Time','Ppro Timestamp',"Price","Open","High","Low","Prev Close P"]]=[time_,timestamp,price,open_,high,low,prev_close]

		elif status =="Error":
			bad_count +=1

		count +=1 
		with sync_lock:
			sync_number -=1




if __name__ == '__main__':

	#try:

	multiprocessing.freeze_support()

	request_pipe, receive_pipe = multiprocessing.Pipe()
	server = multiprocessing.Process(target=server_start, args=(receive_pipe,),daemon=True)
	server.daemon=True
	server.start()

	#main process  run the server. s
	ppro_server(request_pipe)

# df = pd.read_csv('nasdaq.csv', index_col=0)
# df = df.set_index('Ticker')


