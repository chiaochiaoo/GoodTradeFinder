import requests
import multiprocessing
import threading
import time
import json
from datetime import datetime
from datetime import date
import os.path
from modules.Symbol_data_manager import *
from modules.ppro_process_manager_client import *


global reg_count
reg_count = 0

global lock
lock = {}

global black_list
global reg_list
global data
global data_historical
black_list = []
reg_list = []
data = {}
data_historical = {}

global connection_error

global yahoo_same_time
yahoo_same_time = 0


TEST = False
##################################################################
####  pipe in, symbol. if symbol not reg, reg. if reg, dereg  ####
####  main loop. for each reg, thread out and return.		  ####
####  send the updates back to the client.					  ####
##################################################################

open_high_range ="open_high_range"
open_high_val ="open_high_val"
open_high_std ="open_high_std"

open_low_range ="open_low_range"
open_low_val ="open_low_val"
open_low_std ="open_low_std"

high_low_range ="high_low_range"
high_low_val ="high_low_val"
high_low_std ="high_low_std"

first_5_range ="first_5_range"
first_5_val ="first_5_val"
first_5_std ="first_5_std"

first_5_vol_range ="first_5_vol_range"
first_5_vol_val ="first_5_vol_val"
first_5_vol_std ="first_5_vol_std"

normal_5_range ="normal_5_range"
normal_5_val ="normal_5_val"
normal_5_std ="normal_5_std"

normal_5_vol_range ="normal_5_vol_range"
normal_5_vol_val ="normal_5_vol_val"
normal_5_vol_std ="normal_5_vol_std"

prev_close_range ="prev_close_range"
prev_close_val ="prev_close_val"
prev_close_std ="prev_close_std"

symbol_data_ATR ="symbol_data_ATR"


open_high_eval_alert = "open_high_eval_alert"
open_high_eval_value = "open_high_eval_value"

open_low_eval_alert = "open_low_eval_alert"
open_low_eval_value = "open_low_eval_value"

high_low_alert = "high_low_alert"
high_low_eval = "high_low_eval"

first_5_eval = "first_5_eval"
first_5_alert ="first_5_alert"
first_5_vol_eval ="first_5_vol_eval"
first_5_vol_alert = "first_5_vol_alert"

normal_5_eval = "normal_5_eval"
normal_5_alert =  "normal_5_alert"

normal_5_vol_eval = "normal_5_vol_eval"
normal_5_vol_alert =  "normal_5_vol_alert"

prev_eval = "prev_eval"
prev_alert = "prev_alert"


def round_up(i):

	if i<1:
		return round(i,4)
	else:
		return round(i,2)


def fetch_yahoo(symbol):

	url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-chart"

	querystring = {"region":"US","interval":"1m","symbol":symbol,"range":"1d"}

	headers = {
		'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
		'x-rapidapi-key': "0da8e9b784msh9001cc4bfc4e7e7p1c6d94jsna54c1aa52dbf"
		}

	response = requests.request("GET", url, headers=headers, params=querystring)
	res = json.loads(response.text)

	#print(res)
	ts =[]
	#print(res['chart']['result'][0]['indicators']['quote'][0])
	for i in res['chart']['result'][0]['timestamp']:
		ts.append(datetime.fromtimestamp(i).strftime('%H:%M'))

	#print(ts)
	#if it has 09:30. 
	high,low,m_high,m_low,f5,f5v = 0,0,0,0,0,0
	if "09:30" in ts:

		start_ = ['05:00', '05:01', '05:02', '05:03', '05:04', '05:05']
		start_index = 0
		for j in start_:
			if j in ts:
				start_index = ts.index(j)
				break


		start = ts.index("09:30")

		
		high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][start_index:start])
		low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][start_index:start])

		high = np.max(high[high != np.array(None)])
		low = np.min(low[low != np.array(None)])


		m_high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][start:])
		m_low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][start:])

		m_high = round_up(np.max(m_high[m_high != np.array(None)]))
		m_low = round_up(np.min(m_low[m_low != np.array(None)]))

		if "09:30" in ts:

			f5_high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"][start+1:start+6])
			f5_low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"][start+1:start+6])

			f5_high = round_up(np.max(f5_high[f5_high != np.array(None)]))
			f5_low = round_up(np.min(f5_low[f5_low != np.array(None)]))

			f5_v = np.array(res['chart']['result'][0]['indicators']['quote'][0]["volume"][start+1:start+6])
			
			f5 = round_up(f5_high-f5_low) 

			f5v = int(np.sum(f5_v[f5_v != np.array(None)])/1000)
	else:
		high = np.array(res['chart']['result'][0]['indicators']['quote'][0]["high"])
		low = np.array(res['chart']['result'][0]['indicators']['quote'][0]["low"])

		high = round_up(np.max(high[high != np.array(None)]))
		low = round_up(np.min(low[low != np.array(None)]))
		m_high=high
		m_low=low



	return high,low,m_high,m_low,f5,f5v


# secondary sources.

def fetch_kibot(symbol):


	postbody = "http://api.kibot.com/?action=history&symbol="+symbol+"&interval=1&period=1&regularsession=0&user=sajali26@hotmail.com&password=guupu4upu"
	r= request(postbody, symbol)

def test_register():
	try:
		p="http://localhost:8080/Deregister?symbol=AAPL.NQ&feedtype=L1"
		r= requests.get(p)
		print(r.status_code)
		#print(r)
		if r.status_code==200:
			return False
		else:
			return True

	except Exception as e:
		return True
	#Invalid Request

def register(symbol):

	global reg_count
	global reg_list
	global lock

	try:
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=L1"
		#p ="http://localhost:8080/GetSnapshot?symbol="+symbol+"&feedtype=L1"
		r= requests.get(p)
		p="http://localhost:8080/Register?symbol="+symbol+"&feedtype=TOS"
		#p ="http://localhost:8080/GetSnapshot?symbol="+symbol+"&feedtype=TOS"
		r= requests.get(p)

		reg_count+=1
		#print(symbol,"registerd ","total:",reg_count)

		if symbol not in reg_list:
			reg_list.append(symbol)

		if symbol not in lock:
			lock[symbol] = False
		else:
			lock[symbol] = False

		#append it to the list.
	except Exception as e:
		#means cannot connect.
		print("Register error,",e)

		#it could be database not linked 

def deregister(symbol):
	global reg_count
	global reg_list
	#try:
	p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=L1"
	r= requests.get(p)
	p="http://localhost:8080/Deregister?symbol="+symbol+"&feedtype=TOS"
	r= requests.get(p)
	reg_count-=1
	#print(symbol,"deregister","total:",reg_count)
	reg_list.remove(symbol)

	# except Exception as e:
	# 	print("Dereg",symbol,e)

def thread_waiting_mechanism():
	#print(threading.active_count())
	while threading.active_count()>30:
		#print("wait")
		time.sleep(1)

def multi_processing_price(pipe_receive):


	global black_list
	global reg_list
	global connection_error

	try:

		k = 0

		connection_error = True

		while True:

			# k+=1
			# if k%5 == 0:
			# 	current_time = datetime.now().strftime("%M:%S")
			# 	msg = "Server functional."+current_time
			# 	pipe_receive.send(["message",msg])

			while connection_error:
				connection_error = test_register()

				if connection_error:
					pipe_receive.send(["message","Conection failed. try again in 3 sec."])

				else:
					pipe_receive.send(["message","Connection established."])

					for i in reg_list:
						thread_waiting_mechanism()
						reg = threading.Thread(target=register,args=(i,), daemon=True)
						reg.start()

				time.sleep(3)

			#check new symbols. 
			reg = []
			dereg = []
			long_ = []
			short_ = []

			while pipe_receive.poll():
				rec = pipe_receive.recv()
				rec = rec.split("_")
				order,symbol = rec[0],rec[1]
				if order == "reg":
					reg.append(symbol)
				elif order == "dereg":
					dereg.append(symbol)
				elif order == "long":
					long_.append(symbol)
				elif order == "short":
					short_.append(symbol)

			#bulk cmds. reg these symbols. 
			for i in reg:
				if i not in black_list:
					thread_waiting_mechanism()
					reg = threading.Thread(target=register,args=(i,), daemon=True)
					reg.start()

			for i in dereg:
				thread_waiting_mechanism()
				dereg = threading.Thread(target=deregister,args=(i,), daemon=True)
				dereg.start()

			for i in long_:
				l = threading.Thread(target=buy_market_order,args=(i,10), daemon=True)
				l.start()

			for i in short_:
				s = threading.Thread(target=sell_market_order,args=(i,10), daemon=True)
				s.start()

			#try to register again the ones that have ppro errors. 
			#bulk cmds. get updates on these symbols. on finish, send it back to client. 
			for i in reg_list:

				#if prev thread didn't die, kill it and start a new one. 
				#print("sending",i)
				if i not in black_list:
					thread_waiting_mechanism()
					info = threading.Thread(target=getinfo,args=(i,pipe_receive,), daemon=True)
					info.start()

			# if k%5 == 0:
			# 	print("Registed list:",len(reg_list),"T:",threading.active_count())
			k+=1
			time.sleep(1)

			


			#send each dictionary. 
			#pipe_receive.send(data)
	except Exception as e:
		print("error:",e)
		#pipe_receive.send(["message",e])

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def timestamp(s):

	p = s.split(":")
	try:
		x = int(p[0])*60+int(p[1])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0
#IF STILL THE SAME TIME, TRY TO reregister?

#call the thing at 9:30 and start from there. 

#this high low is from ppro.
def init(symbol,price,ppro_high,ppro_low,timestamp):

	global data
	global yahoo_same_time

	#PH,PL,H,L
	range_data=[]


	data[symbol] = {}
	d = data[symbol]

	if timestamp <571:
		d["phigh"] = ppro_high
		d["plow"] = ppro_low
		d["high"] = ppro_high
		d["low"] = ppro_low
		d["f5r"] = 0
		d["f5v"] = 0
		d["already_opened"] = False
	else:
		retry_times = 30
		success = False
		while not success:
			try:
				if TEST:
					range_data=[price,price,price,price,0,0]
				else:
					range_data=fetch_yahoo(symbol[:-3])
				success = True
				#print("yahoo success on ",symbol)
			except:
				yahoo_same_time-=1
				retry_times -=1 
				range_data=[price,price,price,price,0,0]
				time.sleep(3)
				#print("yahoo not success on ",symbol,"re try")
				if retry_times ==0:success = True

		#return high,low,m_high,m_low,f5,f5v
		d["phigh"] = range_data[0]
		d["plow"] =range_data[1]
		d["high"] = range_data[2]
		d["low"] = range_data[3]
		d["f5r"] = range_data[4]
		d["f5v"] = range_data[5]
		d["already_opened"] = True

	#print(symbol,d["phigh"],d["plow"],d["high"],d["low"])

	d["price"]=price
	d["timestamp"] =0
	d["send_timestamp"] = 0
	d["time"] = ""

	d["timestamps"] = []
	d["highs"] = []
	d["lows"] = []
	d["vols"]=[]

	#here I need to access the data from database. 

	d["range"] = 0
	d["last_5_range"] = 0
	d["last_5_range_percentage"] = 0

	d["prev_close"] = 0
	d["prev_close_gap"] = 0
	d["prev_close_percentage"] = 0

	d["open_current_range"] = 0
	d["open_percentage"] = 0

	d["volume"] = 0
	#only after open
	d["open"] = 0
	d["oh"] = 0
	d["ol"] = 0

	d["status"] = ""

	d["pos_range"] = 0.5

	#keys = list(d.keys())
	d["last_send"] = {}
	# for i in keys:
	# 	d["last_send"][i] = d[i]

	d["historical_data_loaded"] = False

	d[open_high_range] = 0
	d[open_high_val] = 0
	d[open_high_std]= 0

	d[open_low_range] = 0
	d[open_low_val] = 0
	d[open_low_std] = 0

	d[high_low_range] = 0
	d[high_low_val] = 0
	d[high_low_std] = 0

	d[first_5_range] = 0
	d[first_5_val] = 0
	d[first_5_std] = 0

	d[first_5_vol_range] = 0
	d[first_5_vol_val] = 0
	d[first_5_vol_std] = 0

	d[normal_5_range] = 0
	d[normal_5_val] = 0
	d[normal_5_std] = 0

	d[normal_5_vol_range] = 0
	d[normal_5_vol_val] = 0
	d[normal_5_vol_std] = 0

	d[prev_close_range] = 0
	d[prev_close_val] = 0
	d[prev_close_std] = 0

	################## ALERTS ########################
	d[open_high_eval_alert] = 0
	d[open_high_eval_value] = "0"

	d[open_low_eval_alert] = 0
	d[open_low_eval_value] = "0"

	d[high_low_alert] = 0
	d[high_low_eval] = "0"

	d[first_5_eval] = "0"
	d[first_5_alert] = 0
	d[first_5_vol_eval] = "0"
	d[first_5_vol_alert] = 0

	d[normal_5_eval] = "0"
	d[normal_5_alert] = 0

	d[normal_5_vol_eval] = "0"
	d[normal_5_vol_alert] = 0

	d[prev_eval] = "0"
	d[prev_alert] = 0

def load_historical_data(symbol):
	global data
	d = data[symbol]

	if d["historical_data_loaded"] == False:
		file = "data/"+symbol+"_"+date.today().strftime("%m%d")+".txt"

		if os.path.isfile(file):
			#print(symbol,"process loading from db.")
			with open(file) as json_file:
				da = json.load(json_file)
			#print(da)
			for key,item in da.items():
				d[key] = item 

			d["historical_data_loaded"] = True
			print(symbol,"loaded successful")


def historical_eval(symbol):

	global data
	d = data[symbol]

	if d["historical_data_loaded"]:
		#normal ones
		if d["open_current_range"]>0:
			d[open_high_eval_alert] = round((d["open_current_range"]-d[open_high_val])/d[open_high_std],1)
			d[open_high_eval_value] = "Cur:"+str(d[open_high_eval_alert])+","+"Max:"+str( round((d["oh"]-d[open_high_val])/d[open_high_std],1))

			d[open_low_eval_alert] =  0
			d[open_low_eval_value] = "Cur:"+str(d[open_low_eval_alert])+","+"Max:"+str( round((d["ol"]-d[open_low_val])/d[open_low_std],1))
		else:
			d[open_high_eval_alert] = 0
			d[open_high_eval_value] = "Cur:"+str(d[open_high_eval_alert])+","+"Max:"+str( round((d["oh"]-d[open_high_val])/d[open_high_std],1))

			d[open_low_eval_alert] =  round((-d["open_current_range"]-d[open_high_val])/d[open_high_std],1)
			d[open_low_eval_value] = "Cur:"+str(d[open_low_eval_alert])+","+"Max:"+str( round((d["ol"]-d[open_low_val])/d[open_low_std],1))

		try:
			d[high_low_alert] =  round((d["range"]-d[high_low_val])/d[high_low_std],1)
		except:
			d[high_low_alert] = 0
		d[high_low_eval] = str(d[high_low_alert])

		try:
			d[first_5_alert] = round((d["f5r"]-d[first_5_val])/d[first_5_std],1)
		except:
			d[first_5_alert] = 0
		d[first_5_eval] = str(d[first_5_alert])
		
		try:
			d[first_5_vol_alert] =  round((d["f5v"]-d[first_5_vol_val])/d[first_5_vol_std],1)
		except:
			d[first_5_vol_alert] =0
		d[first_5_vol_eval] =str(d[first_5_vol_alert])
		
		try:
			d[normal_5_alert] = round((d["last_5_range"]-d[normal_5_val])/d[normal_5_std],1)
		except:
			d[normal_5_alert] = 0
		d[normal_5_eval] = str(d[normal_5_alert])
		
		try:
			d[normal_5_vol_alert] =  round((d["vol"]-d[normal_5_vol_val])/d[normal_5_vol_std],1)
		except:
			d[normal_5_vol_alert] =0
		d[normal_5_vol_eval] =  str(d[normal_5_vol_alert])
		
		try:
			d[prev_alert] = round(abs(d["prev_close_gap"]-d[prev_close_val])/d[prev_close_std],1)
		except:
			d[prev_alert] = 0
		d[prev_eval] = str(d[prev_alert])

		#ones with current vals. 
		# d[open_high_range] = 0
		# d[open_high_val] = 0
		# d[open_high_std]= 0

		# d[open_low_range] = 0
		# d[open_low_val] = 0
		# d[open_low_std] = 0

		# d[high_low_range] = 0
		# d[high_low_val] = 0
		# d[high_low_std] = 0

		# d[first_5_range] = 0
		# d[first_5_val] = 0
		# d[first_5_std] = 0

		# d[first_5_vol_range] = 0
		# d[first_5_vol_val] = 0
		# d[first_5_vol_std] = 0

		# d[normal_5_range] = 0
		# d[normal_5_val] = 0
		# d[normal_5_std] = 0

		# d[normal_5_vol_range] = 0
		# d[normal_5_vol_val] = 0
		# d[normal_5_vol_std] = 0

		# d[prev_close_range] = 0
		# d[prev_close_val] = 0
		# d[prev_close_std] = 0


def process_and_send(lst,pipe):

	global lock
	status,symbol,time,timestamp,price,high,low,open_,vol,prev_close  = lst[0],lst[1],lst[2],lst[3],lst[4],lst[5],lst[6],lst[7],lst[8],lst[9]

	global data

	if symbol not in data:
		init(symbol,price,high,low,timestamp)

	#here;s the false print check. 0.005
	d = data[symbol]

	now = datetime.now()

	ts = now.hour*3600 + now.minute*60 + now.second
	t = str(now.minute) +":" + str(now.second)
	rec = timestamp_seconds(time)
	ms = now.hour*60 + now.minute
	latency = ts-rec

	#if abs(price-d["price"])/d["price"] < 0.02:

	d = data[symbol]

	d["timestamp"] = timestamp
	d["time"] = time
	d["price"] = price
	d["open"] = open_
	d["prev_close"] = prev_close

	#else:
	#here I set them. 

	if price > d["high"]:
		d["high"] = price

	if price < d["low"] or d["low"]==0:
		d["low"] = price			

	if timestamp <570:
		d["phigh"] = d["high"]
		d["plow"] = d["low"]

	d["range"] = round(d["high"] - d["low"],3)
	#print("check",d["range"],d["high"],d["low"],d["phigh"],d["plow"])

	if timestamp <570:
		d["open"] = 0
		d["oh"] = 0
		d["ol"] = 0
		d["open_percentage"] = 0
	else:
		if d["already_opened"] == False:  #one time check.
			d["high"] = price
			d["low"] = price
			d["already_opened"] = True

		d["oh"] = round(d["high"] - open_,3)
		d["ol"] = round(open_ - d["low"],3)
		if open_!=0:
			d["open_current_range"] = round((price-open_),2)
			d["open_percentage"] =  round(((price-open_)*100/open_),2)
		else:
			d["open_percentage"] = 0
			d["open_current_range"] = 0


	d["prev_close_gap"] = round(price-prev_close,3)

	# now update the datalists.
	if timestamp not in d["timestamps"]:
		if len(d["timestamps"])==0:
			d["timestamps"].append(timestamp-1)
		else:
			d["timestamps"].append(timestamp)
		d["highs"].append(price)
		d["lows"].append(price)
		d["vols"].append(vol)
	else:
		if price >= d["highs"][-1]:
			d["highs"][-1] = price
		if price <= d["lows"][-1]:
			d["lows"][-1] = price
		d["vols"][-1] = vol

	#print(d["timetamps"],d["highs"],d["lows"],d["vols"])
	#last 5 range
	d["last_5_range"] = round_up(max(d["highs"][-5:]) - min(d["lows"][-5:]))
	# last 5 volume
	index = min(len(d["vols"]), 5)
	d["vol"] = round((d["vols"][-1] - d["vols"][-index])/1000,2)

	if timestamp>569 and timestamp <575:
		d["f5r"] = d["last_5_range"]
		d["f5v"] = d["vol"]


	#check if the data is lagged. Premarket. Real. Aftermarket.
	register_again = False
	#normal
	if ms<570 or ms>960:
		if latency >120:
			status = "Lagged"
			register_again = False
	#premarket
	else:
		if latency >240:
			status = "Lagged"
			register_again = True


	### POSITION READ ###

	if (d["high"]-d["low"])/(d["low"]+0.000001) <0.02:
		d["pos_range"] = 0.5
	else:
		d["pos_range"] = round((price-d["low"])/(d["high"]-d["low"]+0.0001),2)

	d["status"] = ""



	if d["pos_range"]>=0.99:
		d["status"]="New High"
		status_given = True

	if d["pos_range"]<=0.01:
		d["status"]="New Low"

	if d["pos_range"]<0.99 and d["pos_range"]>=0.90:
		d["status"]="Near High"

	if d["pos_range"]>0.01 and d["pos_range"]<=0.1:
		d["status"]="Near Low"

	if d["pos_range"]>0.1 and d["pos_range"]<0.25:
		d["status"]="Trading Low"

	if d["pos_range"]<0.9 and d["pos_range"]>0.75:
		d["status"]="Trading High"

	#################################################
	#if d["pos_range"]<0.96 and d["pos_range"]>0.4:
	###############################################

	if len(d["highs"])>5:
		change_high = d["highs"][-1] - d["highs"][-5]
		change_low = d["lows"][-1] - d["lows"][-5]

		if d["pos_range"]<=0.1 and d["pos_range"]>0.03 and change_high>0 and change_low>0:
			d["status"]="Low Reversing"

		if d["pos_range"]>=0.9 and d["pos_range"]<=0.97 and change_high<0 and change_low<0:
			d["status"]="High Reversing"

	############ RANGE CHEKER #########################
	if timestamp <570:
		d["open_percentage"] = range_eval(d["highs"],d["lows"])
	################################################


	if prev_close!=0:
		d["prev_close_percentage"] = round(d["prev_close_gap"]*100/(prev_close+0.0000000001),2)
	else:
		d["prev_close_percentage"] = 0
	d["last_5_range_percentage"] = round(d["last_5_range"]*100/(price+0.00000001),2)


	#### Historical Eval ####
	load_historical_data(symbol)
	historical_eval(symbol)
	update_list={}

	send_list={}
	if d["send_timestamp"]== timestamp: #this minute it has just updated.

		update_list[symbol_price] = price
		update_list[symbol_update_time] = time
		update_list[minute_timestamp_val] = timestamp
		update_list[symbol_percentage_last_5] = d["last_5_range_percentage"]
		update_list[symbol_position_status] = d["status"]
		update_list[symbol_price_high] = d["high"]
		update_list[symbol_price_low] = d["low"]
		
	else:
		d["send_timestamp"] = timestamp
		update_list[symbol_price] = price
		update_list[symbol_update_time] = time
		update_list[minute_timestamp_val] = timestamp
		update_list[symbol_price_high] = d["high"]
		update_list[symbol_price_low] = d["low"]
		update_list[symbol_price_premarket_high] = d["phigh"]
		update_list[symbol_price_premarket_low] = d["plow"]
		update_list[symbol_price_range] = d["range"]
		update_list[last_5_min_range] = d["last_5_range"]
		update_list[last_5_min_volume] = d["vol"]
		update_list[symbol_price_open] = d["open"]
		update_list[symbol_price_openhigh] = d["oh"]
		update_list[symbol_price_openlow] = d["ol"]
		update_list[symbol_price_opennow] = d["open_current_range"]
		update_list[first_5_min_range] = d["f5r"]
		update_list[first_5_min_volume] = d["f5v"]
		update_list[symbol_price_prevclose] = d["prev_close"]
		update_list[symbol_price_prevclose_to_now] = d["prev_close_gap"]
		update_list[symbol_percentage_since_close] = d["prev_close_percentage"]
		update_list[symbol_percentage_since_open] = d["open_percentage"]
		update_list[symbol_percentage_last_5] = d["last_5_range_percentage"]
		update_list[symbol_position_status] = d["status"]


		update_list[open_high_eval_alert] = d[open_high_eval_alert] 
		update_list[open_high_eval_value] = d[open_high_eval_value]

		update_list[open_low_eval_alert] = d[open_low_eval_alert] 
		update_list[open_low_eval_value] = d[open_low_eval_value] 

		update_list[high_low_alert] = d[high_low_alert] 
		update_list[high_low_eval] = d[high_low_eval] 

		update_list[first_5_eval] = d[first_5_eval]
		update_list[first_5_alert] = d[first_5_alert] 
		update_list[first_5_vol_eval] = d[first_5_vol_eval] 
		update_list[first_5_vol_alert] = d[first_5_vol_alert] 

		update_list[normal_5_eval] = d[normal_5_eval] 
		update_list[normal_5_alert] = d[normal_5_alert] 

		update_list[normal_5_vol_eval] = d[normal_5_vol_eval]
		update_list[normal_5_vol_alert] = d[normal_5_vol_alert] 
		update_list[prev_eval] = d[prev_eval] 
		update_list[prev_alert] = d[prev_alert] 
						
	#check the list. del if repeate.
	for key,item in update_list.items():

		if key not in d["last_send"]:
			d["last_send"][key] = item
			send_list[key] = item
		else:
			if update_list[key] != d["last_send"][key]:
				d["last_send"][key] = item
				send_list[key] = item


	if len(send_list)>1:
		pipe.send([status,symbol,send_list])
	



	# pipe.send([status,symbol,price,time,timestamp,d["high"],d["low"],d["phigh"],d["plow"],\
	# 	d["range"],d["last_5_range"],d["vol"],d["open"],d["oh"],d["ol"],d["open_current_range"],
	# 	d["f5r"],d["f5v"],d["prev_close"],d["prev_close_gap"],d["prev_close_percentage"],d["open_percentage"],d["last_5_range_percentage"],d["status"]])


	# pipe.send([status,symbol,price,time,timestamp,d["high"],d["low"],d["phigh"],d["plow"],\
	# 	d["range"],d["last_5_range"],d["vol"],d["open"],d["oh"],d["ol"],d["open_current_range"],
	# 	d["f5r"],d["f5v"],d["prev_close"],d["prev_close_gap"],d["prev_close_percentage"],d["open_percentage"],d["last_5_range_percentage"],d["status"]])

	#print("sent",symbol)

	if register_again:
		register(symbol)

	lock[symbol] = False

def range_eval(highs,lows):

	#look back 30 minutes. report the one with least amount of change.

	a=highs[-90:]
	b=lows[-90:]

	count_a=0
	init = a[0]
	for i in a:
		if i>init:
			init = i
			count_a+=1

	count_b=0
	init = b[0]
	for i in b:
		if i<init:
			init = i
			count_b+=1

	diff = abs(count_a-count_b)

	total = min(90,len(highs))
	return round(1-diff/total,2)


def getinfo(symbol,pipe):

	global black_list

	global connection_error

	if not connection_error:

		if not lock[symbol]:
			try:
				lock[symbol] = True
				p="http://localhost:8080/GetLv1?symbol="+symbol
				r= requests.get(p,timeout=2)

				if(r.text =='<Response><Content>No data available symbol</Content></Response>'):
					print("No symbol found")
					# black_list.append(symbol)
					# pipe.send(["Unfound",symbol])
					lock[symbol] = False

				elif 'symbol should be registered first' in r.text:
					register(symbol)
				else:

					time=find_between(r.text, "MarketTime=\"", "\"")[:-4]

					open_ = float(find_between(r.text, "OpenPrice=\"", "\""))

					high = float(find_between(r.text, "HighPrice=\"", "\""))
					low = float(find_between(r.text, "LowPrice=\"", "\""))

					vol = int(find_between(r.text, "Volume=\"", "\""))
					prev_close = float(find_between(r.text, "ClosePrice=\"", "\""))

					Bidprice= float(find_between(r.text, "BidPrice=\"", "\""))
					Askprice= float(find_between(r.text, "AskPrice=\"", "\""))
					price = round((Bidprice+Askprice)/2,4)

					#price = float(find_between(r.text, "LastPrice=\"", "\""))

					if price<1:
						price = round(price,3)
					else:
						price = round(price,2)

					#print(time,Bidprice,Askprice,open_,high,low,vol,price)
					ts = timestamp(time[:5])

					try:
						process_and_send(["Connected",symbol,time,ts,price,high,low,open_,vol,prev_close],pipe)
					except Exception as e:
						print("PPro Process error",e)
						lock[symbol] = False
			#pipe.send(output)

			except Exception as e:
				print("Get info error:",e)
				connection_error = True
				pipe.send(["Ppro Error",symbol])
				lock[symbol] = False

		# else:
		# 	print(symbol,"blocked call")




# i may need to come up with a new strucutre.
# now its like. iterate through each symbols. and wait for some seconds. do it again.

# new structure:
# Access the 

# turn someone into a single process. 

#  > link:
#  > link:

# Want: all the information are processed locally. only update is sent. 


# if __name__ == '__main__':

# 	multiprocessing.freeze_support()
# 	request_pipe, receive_pipe = multiprocessing.Pipe()
# 	p = multiprocessing.Process(target=multi_processing_price, args=(receive_pipe,),daemon=True)
# 	p.daemon=True
# 	p.start()

# 	t = ppro_process_manager(request_pipe)
# 	t.register("AAPL.NQ")

# 	# request_pipe.send("AAPL.NQ")
# 	# request_pipe.send("AMD.NQ")

# 	while True:
# 		print(request_pipe.recv())

# high,low,m_high,m_low,f5,f5v
#print(fetch_yahoo("GLD"))

# a=[8.42, 8.61, 9.27, 9.07, 8.71, 9.0, 8.95, 8.84, 8.8, 8.79, 8.82, 8.88, 8.85, 8.8, 8.72, 8.66, 8.53, 8.5, 8.53, 8.46, 8.41, 8.4, 8.39, 8.49, 8.49, 8.48, 8.49, 8.59, 8.65, 8.59, 8.59, 8.58, 8.56, 8.48, 8.46, 8.44, 8.38, 8.28, 8.4, 8.39, 8.33, 8.4, 8.37, 8.4, 8.3, 8.29, 8.3, 8.31, 8.36, 8.34, 8.37, 8.38, 8.35, 8.31, 8.32, 8.32, 8.32, 8.3, 8.27, 8.27, 8.2, 8.23, 8.1, 7.95, 7.98, 7.98, 7.98, 7.93, 7.9, 7.86, 7.86, 7.9, 7.94, 8.1, 8.1, 8.1, 8.08, 8.07, 8.03, 7.95, 7.9, 7.91, 7.9, 8.0, 8.03, 8.14, 8.21, 8.12, 8.08, 8.1, 8.09, 8.05, 8.02, 8.02, 8.0, 7.96, 7.9, 7.93, 7.95, 7.92, 7.97, 7.92, 7.91, 7.95, 7.93, 7.95, 7.98, 8.0, 8.0, 8.08, 8.08, 8.08, 8.07, 8.06, 8.04, 8.05, 8.04, 8.04, 8.02, 8.03, 8.03, 8.02, 8.0, 8.0, 8.03, 8.03, 8.03, 8.03, 8.04, 8.04, 8.07, 8.1, 8.15, 8.18, 8.2, 8.2, 8.18, 8.18, 8.18, 8.2, 8.2, 8.18, 8.18, 8.19, 8.17, 8.15, 8.14, 8.14, 8.18, 8.15, 8.16, 8.18, 8.18, 8.18, 8.18, 8.18, 8.18, 8.18, 8.22, 8.22, 8.28, 8.33, 8.35, 8.3, 8.27, 8.32, 8.35, 8.34, 8.3, 8.22, 8.25, 8.27, 8.27, 8.27, 8.25, 8.26, 8.21, 8.2, 8.17, 8.18, 8.2, 8.19, 8.19, 8.17, 8.07, 8.05, 8.05, 8.08, 8.12, 8.14, 8.14, 8.14, 8.16, 8.15, 8.17, 8.19, 8.19, 8.19, 8.18, 8.16, 8.18, 8.22, 8.23, 8.2, 8.19, 8.18, 8.19, 8.21, 8.21, 8.19, 8.19, 8.2, 8.19, 8.19, 8.18, 8.18, 8.14, 8.15, 8.15, 8.15, 8.08, 8.06, 8.06, 8.02, 8.03, 8.05, 8.06, 8.05, 8.08, 8.07, 8.08, 8.08, 8.11, 8.13, 8.15, 8.16, 8.17, 8.17, 8.17, 8.2499, 8.17, 8.17, 8.17, 8.18, 8.16, 8.13, 8.13, 8.12, 8.13, 8.13, 8.13, 8.14, 8.13, 8.13, 8.13, 8.13, 8.11, 8.12, 8.12, 8.13, 8.13, 8.14, 8.13, 8.14, 8.15, 8.15, 8.15, 8.15, 8.15, 8.16, 8.15, 8.15, 8.16, 8.16, 8.16, 8.16, 8.16, 8.17, 8.18, 8.19, 8.23, 8.3, 8.3, 8.29, 8.29, 8.29, 8.28, 8.28, 8.29, 8.29, 8.26, 8.26, 8.26, 8.24, 8.24, 8.3, 8.3, 8.3, 8.3, 8.3, 8.29, 8.28, 8.24, 8.22, 8.17, 8.1999, 8.2, 8.19, 8.17, 8.16, 8.12, 8.13, 8.13, 8.12, 8.11, 8.11, 8.14, 8.16, 8.21, 8.21, 8.25, 8.24, 8.23, 8.27, 8.27, 8.27, 8.37, 8.38, 8.380000114440918, 7.830100059509277, 8.0, 8.0, 8.039999961853027, 8.0, 7.940000057220459, 7.889900207519531, 7.699999809265137, 7.699999809265137, 8.010000228881836, 7.979899883270264, 7.949999809265137, 8.0, 8.050000190734863, 8.03499984741211, 8.026000022888184, 8.0, 8.0, 8.020000457763672, 8.039999961853027, 8.034799575805664, 8.086999893188477, 8.0649995803833, 8.079999923706055, 8.079999923706055, 8.140000343322754, 8.18910026550293, 8.210000038146973, 8.25, 8.350000381469727, 8.350000381469727, 8.5, 8.5, 8.5, 8.470000267028809, 8.489999771118164, 8.489999771118164, 8.449999809265137, 8.444700241088867, 8.34000015258789, 8.23009967803955, 8.180000305175781, 8.1451997756958, 8.140000343322754, 8.109999656677246, 8.050000190734863, 8.025899887084961, 8.079999923706055, 8.100000381469727, 8.100000381469727, 8.050000190734863, 8.009400367736816, 7.901599884033203, 7.752200126647949, 7.690000057220459, 7.690000057220459, 7.949999809265137, 8.079999923706055, 8.050000190734863, 7.96999979019165, 7.909999847412109, 7.800000190734863, 7.824999809265137, 7.860000133514404, 7.820000171661377, 7.820000171661377, 7.819399833679199, 7.807000160217285, 7.75, 7.721099853515625, 7.730000019073486, 7.760000228881836, 7.760000228881836, 7.730000019073486, 7.621099948883057, 7.550000190734863, 7.510000228881836, 7.449999809265137, 7.420000076293945, 7.519999980926514, 7.589000225067139, 7.599999904632568, 7.75, 7.829699993133545, 7.849999904632568, 7.840000152587891, 7.849999904632568, 7.860000133514404, 7.849999904632568, None, 7.820000171661377]

# a=np.array(a)
# a=a[a != np.array(None)]

# a.sort()
# print(a)
# on one hand, takes in new symbol and register. other hand, get current. ? 

# for every itertaions:
# 1. check if pipe/queue is empty.
	 #if not, register/deregister these symbols. 
# 2. For each of these register symbols,fetch the updates for it! 
# request_pipe, receive_pipe = multiprocessing.Pipe()
# multi_processing_price(receive_pipe)