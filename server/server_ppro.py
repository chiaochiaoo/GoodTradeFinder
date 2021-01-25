import finviz
import pandas as pd
import threading
from queue import Queue
import time
import requests

#### Update the info from the Finviz ####




# def test(queue,i):
# 	queue.put(["i"])

# for i in range(1):
# 	reg = threading.Thread(target=test,args=(queue,i), daemon=True)
# 	reg.start()


def market_scanner(queue):
	threadshold = 50
	a = pd.read_csv('nasdaq.csv', index_col=0)
	# print(a)
	# a = a.set_index('Ticker')

	ticks = a.index

	#50 a second. 
	count = 0


	while True:
		for i in ticks:
			reg = threading.Thread(target=getinfo,args=(i+".NQ",queue), daemon=True)
			reg.start()
			count+=1
			if count%threadshold ==0:
				print("Sleep for 2 second")
				time.sleep(2)

###### Update the info from PPRO. ##################
def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def test_register():
	try:
		p="http://localhost:8080/Deregister?symbol=AAPL.NQ&feedtype=L1"
		r= requests.get(p)
		if "Response" in r.text:
			return False
		else:
			return True

	except Exception as e:
		return True

#def register(symbol):

	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		print(symbol,"registerd ","total:",reg_count)

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

	global lock
	global connection_error

	if symbol not in lock:
		lock[symbol] = False

	if not connection_error:

		if not lock[symbol]:
			try:
				#######################################################################

				p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
				r= requests.get(p)

				lock[symbol] = True
				p="http://localhost:8080/GetLv1?symbol="+symbol
				r= requests.get(p)

				if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
					print("No symbol found")
					black_list.append(symbol)
					pipe.put(["Unfound",symbol])
				else:

					time=find_between(r.text, "MarketTime=\"", "\"")[:-4]
					open_ = float(find_between(r.text, "OpenPrice=\"", "\""))
					high = float(find_between(r.text, "HighPrice=\"", "\""))
					low = float(find_between(r.text, "LowPrice=\"", "\""))
					vol = int(find_between(r.text, "Volume=\"", "\""))
					prev_close = float(find_between(r.text, "ClosePrice=\"", "\""))

					price = float(find_between(r.text, "LastPrice=\"", "\""))

					if price<1:
						price = round(price,3)
					else:
						price = round(price,2)


					#ts = timestamp(time[:5])

					pipe.put(["Connected",symbol,time,price,open_,high,low,vol,prev_close])

					p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
					r= requests.get(p)

				#pipe.put(output)

			except Exception as e:
				print("Get info error:",e)
				connection_error = True
				pipe.put(["Ppro Error",symbol])
				lock[symbol] = False


global connection_error
connection_error = False
global lock
lock = {}

queue = Queue()

ms = threading.Thread(target=market_scanner,args=(queue,), daemon=True)
ms.start()

while True:
    data = queue.get()
    print(data)




# a = pd.read_csv('nasdaq.csv', index_col=0)
# a = a.set_index('Ticker')


