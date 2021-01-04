import tkinter as tk                     
from tkinter import ttk 
from pannel import *
from Symbol_data_manager import *


def to_number(str):

	try:
		x = round(float(str),2)
		return x 

	except Exception as e:
		print("to_num",e)
		return 0.00


class all_alerts(pannel):
	def __init__(self,frame):
		super().__init__(frame)

		self.labels = ["Ticker","Time","Alert","Dismiss"]
		self.width = [8,10,24,10]
		self.labels_creator(self.frame)

		self.alert_base = []

	#if the type and the time match, then don't add. 

	def dismiss_alerts(self,key):

		for i in self.tickers_labels[key]:
			i.destroy()

		self.rebind(self.canvas,self.frame)

	#vals = symbol,time ,alert type
	def add_alerts(self,vals):

		l = self.label_count 

		symbol = vals[0]
		
		if set(vals) not in self.alert_base:

			key = str(vals)
			self.tickers_labels[key] = []
			for i in range(len(vals)):
				
				self.tickers_labels[key].append(tk.Label(self.frame ,text=vals[i],width=self.width[i]))
				self.label_default_configure(self.tickers_labels[key][i])
				self.tickers_labels[key][i].grid(row= l+2, column=i,padx=0)

			i+=1
			self.tickers_labels[key].append(tk.Button(self.frame ,width=self.width[i],command = lambda k=key: self.dismiss_alerts(k)))
			self.label_default_configure(self.tickers_labels[key][i])
			self.tickers_labels[key][i].grid(row= l+2, column=i,padx=0)


			self.label_count +=1
			self.alert_base.append(set(vals))
			self.rebind(self.canvas,self.frame)

		self.rebind(self.canvas,self.frame)

class alert(pannel):

	def __init__(self,frame,data:Symbol_data_manager,alert_pannel:all_alerts):

		super().__init__(frame)

		self.alert_pannel=alert_pannel
		self.data = data

		self.alerts = {}

		#init the labels. 

	#any alert will need a threshold. deviation. std. 
	def add_symbol(self,symbol,format,alert_positions,alerts,data_ready):

		#init the alert value
		if symbol not in self.alerts:
				self.alerts[symbol] = {}

		for i in alert_positions:
			self.alerts[symbol][alerts[i][2][5]] = 0

		l = self.label_count

		self.tickers_labels[symbol] = []
		i = symbol

		for j in range(len(format)):

			if j==0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			elif j==1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

			#when it is alert label creation, create a trace set for value position 
			elif j in alert_positions:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				#unpack value_position,alert_position,alertvals
				value_position = alerts[j][0]
				alert_position = alerts[j][1]
				alert_vals = alerts[j][2]
				format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def add_symbol_breakout(self,symbol,format,alert_positions,alerts,data_ready):

		#init the alert value
		if symbol not in self.alerts:
				self.alerts[symbol] = {}

		for i in alert_positions:
			self.alerts[symbol][alerts[i][2][5]] = 0

		l = self.label_count

		self.tickers_labels[symbol] = []
		i = symbol

		for j in range(len(format)):

			if j==0:
				self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			elif j==1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

			#text filed for hmm,,,entry, 
			elif j ==2 or j ==3:
				self.tickers_labels[i].append(tk.Entry(self.frame ,textvariable=format[j],width=self.width[j]))
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
			#when it is alert label creation, create a trace set for value position 
			elif j in alert_positions:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
				#unpack value_position,alert_position,alertvals
				value_position = alerts[j][0]
				alert_position = alerts[j][1]
				alert_vals = alerts[j][2]
				format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))

			elif j>1:
				self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
				self.label_default_configure(self.tickers_labels[i][j])
				self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

		#self.ticker_count +=1
		self.label_count +=1

		self.rebind(self.canvas,self.frame)

	def delete_symbol(self,symbol):

		for i in self.tickers_labels[symbol]:
			i.destroy()

		self.tickers_labels.pop(symbol,None)

		self.rebind(self.canvas,self.frame)


	def set_latest_alert(self,symbol,alert,time):

		self.data.symbol_last_alert[symbol].set(alert)
		self.data.symbol_last_alert_time[symbol].set(time)

	#alert vals: cur, mean, std.
	def alert(self,eval_string,eval_label,alerts_vals,ready,status):

		#check how many std it is. `

		#attention, only do the calculation when the database is set. 

		if ready.get() == True and status.get() =="Connected":

			symbol= alerts_vals[0]
			time= alerts_vals[1].get()[:5]
			alert_type = alerts_vals[5]
			ts = timestamp(time)

			if alert_type=="breakout":

				### ASSUME NUMBER ONLY.
				cur_price= round(alerts_vals[2].get(),3)
				support= to_number(alerts_vals[3].get())
				resistance =  to_number(alerts_vals[4].get())

				

				if support != 0.00 and resistance != 0.00:
					print(support,resistance)

					if cur_price<support and self.alerts[symbol][alert_type]!=0:

						self.alerts[symbol][alert_type] = 0

						alert_str = "Support "+alert_type
						eval_label["background"]="yellow"

						eval_string.set(alert_str)

						self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

					elif cur_price>resistance and self.alerts[symbol][alert_type]!=1 :
					
						self.alerts[symbol][alert_type] = 1

						alert_str = "Resistance "+alert_type
						eval_label["background"]="yellow"

						eval_string.set(alert_str)

						self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

			else:
				
				cur_price= round(alerts_vals[2].get(),3)
				mean= round(alerts_vals[3].get(),3)
				std=  round(alerts_vals[4].get(),3)

				#on certain alert_type, the math can be different. 


				if std != 0:
					cur = round((cur_price-mean)/std,3)
					eval_string.set(str(cur)+" from mean")
				else:
					cur = 0
					eval_string.set("Unable to process std 0")

				#color. 

				if cur <0.5:
					eval_label["background"]="white"

				elif cur>0.5 and cur<1:
					
					alert_str = "Moderate "+alert_type
					eval_label["background"]="#97FEA8"

					if ts>570 and self.alerts[symbol][alert_type] < 0.5:
						self.alerts[symbol][alert_type] = 0.5
						self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)

				elif cur>1 and cur<2 and self.alerts[symbol][alert_type] < 1:
					self.alerts[symbol][alert_type] = 1
					alert_str = "High "+alert_type
					eval_label["background"]="yellow"
					if ts>570:
						#only set when there is higher severity. 
						self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)
				elif cur>2 and self.alerts[symbol][alert_type] < 2:

					self.alerts[symbol][alert_type] = 2
					### Send the alert to alert pannel.
					alert_str = "Very high "+alert_type
					eval_label["background"]="red"
					if ts>570:
						self.alert_pannel.add_alerts([symbol,time,alert_str])
						self.set_latest_alert(symbol, alert_str, time)





class highlow(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur High","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_range[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_range_val[symbol]
		hist_std = self.data.symbol_data_range_std[symbol]
		hist_range= self.data.symbol_data_range_range[symbol]
		eva= self.data.symbol_data_range_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Range"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_high,cur_low,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.

class openhigh(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur High","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openhigh[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_high = self.data.symbol_price_high[symbol]
		hist_avg= self.data.symbol_data_openhigh_val[symbol]
		hist_std = self.data.symbol_data_openhigh_std[symbol]
		hist_range= self.data.symbol_data_openhigh_range[symbol]

		eva= self.data.symbol_data_openhigh_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-High"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_open,cur_high,hist_avg,hist_std,hist_range,eva]


		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.

class openlow(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","Cur Open","Cur Low","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,7,7,9,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		cur_range =self.data.symbol_price_openlow[symbol]
		cur_open = self.data.symbol_price_open[symbol]
		cur_low = self.data.symbol_price_low[symbol]
		hist_avg= self.data.symbol_data_openlow_val[symbol]
		hist_std = self.data.symbol_data_openlow_std[symbol]
		hist_range= self.data.symbol_data_openlow_range[symbol]

		eva= self.data.symbol_data_openlow_eval[symbol]
		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 8
		alert_type = "Intraday Open-Low"

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		labels = [symbol,status,cur_range,cur_open,cur_low,hist_avg,hist_std,hist_range,eva]


		#any alert will need a threshold. deviation. std. 

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class firstfive(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","H. Avg","H. Std","H. Range","Cur Vol","H.Vol Avg","H.Vol Std","H.Vol Range","Evaluation:Range","Evaluation:Volume"]
		self.width = [8,10,7,7,7,7,7,7,7,12,14,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?
		cur_range =self.data.first_5_min_range[symbol]
		cur_vol = self.data.first_5_min_volume[symbol]

		hist_avg= self.data.symbol_data_first5_val[symbol]
		hist_std = self.data.symbol_data_first5_std[symbol]
		hist_range= self.data.symbol_data_first5_range[symbol]

		hist_v_avg= self.data.symbol_data_first5_vol_val[symbol]
		hist_v_std = self.data.symbol_data_first5_vol_std[symbol]
		hist_v_range= self.data.symbol_data_first5_vol_range[symbol]

		eva= self.data.symbol_data_first5_range_eval[symbol]

		eva2 = self.data.symbol_data_first5_vol_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]


		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,cur_vol,hist_v_avg,hist_v_std,hist_v_range,eva,eva2]

		value_position = 2
		alert_position = 10
		alert_type = "Opening Rg"
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type]
		#cur, mean, std. symbol, time. 
		

		value_position2 = 6
		alert_position2 = 11

		alert_type2 = "Opening Vol"
		alertvals2= [symbol,time,cur_vol,hist_v_avg,hist_v_std,alert_type2]


		alert_positions = [alert_position,alert_position2]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		alerts[alert_position2] = [value_position2,alert_position2,alertvals2]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremrange(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Range","H. Avg","H. Std","H. Range","Evaluation"]
		self.width = [8,10,7,7,7,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?
		cur_range =self.data.last_5_min_range[symbol]

		hist_avg= self.data.symbol_data_normal5_val[symbol]
		hist_std = self.data.symbol_data_normal5_std[symbol]
		hist_range= self.data.symbol_data_normal5_range[symbol]

		eva= self.data.symbol_data_normal5_range_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 6
		alert_type = "Intraday Range"
		alert_time = 0
		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_range,hist_avg,hist_std,alert_type,alert_time]
		labels = [symbol,status,cur_range,hist_avg,hist_std,hist_range,eva]

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.


class extremevolume(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Cur Vol(k)","H. Avg(k)","H. Std(k)","H. Range","Evaluation"]
		self.width = [8,10,15,7,7,15,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?

		cur_vol = self.data.last_5_min_volume[symbol]

		hist_avg= self.data.symbol_data_normal5_vol_val[symbol]
		hist_std = self.data.symbol_data_normal5_vol_std[symbol]
		hist_range= self.data.symbol_data_normal5_vol_range[symbol]

		eva= self.data.symbol_data_normal5_vol_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 2
		alert_position = 6
		alert_type = "Intraday Open-Low"

		alert_time = 0

		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_vol,hist_avg,hist_std,alert_type,alert_time]
		labels = [symbol,status,cur_vol,hist_avg,hist_std,hist_range,eva]

		#any alert will need a threshold. deviation. std. or type.

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.



class breakout(alert):

	def __init__(self,frame,data:Symbol_data_manager,alert_panel:all_alerts):

		super().__init__(frame,data,alert_panel)

		self.labels = ["Ticker","Status","Support","Resistance ","Cur Price","Evaluation"]
		self.width = [8,10,10,10,10,15]
		self.labels_creator(self.frame)

	def add_symbol(self,symbol):

		status = self.data.symbol_status[symbol]
		#?

		cur_price = self.data.symbol_price[symbol]

		support = self.data.symbol_data_support[symbol]
		resistance  = self.data.symbol_data_resistance[symbol]

		eva= self.data.symbol_data_breakout_eval[symbol]

		time = self.data.symbol_update_time[symbol]

		data_ready = self.data.data_ready[symbol]

		value_position = 4
		alert_position = 5
		alert_type = "breakout"

		alert_time = 0


		#cur, mean, std. symbol, time. 
		alertvals= [symbol,time,cur_price,support,resistance ,alert_type]
		labels = [symbol,status,support,resistance ,cur_price,eva]

		#any alert will need a threshold. deviation. std. or type.

		alert_positions = [alert_position]

		alerts = {}
		alerts[alert_position] = [value_position,alert_position,alertvals]
		#any alert will need a threshold. deviation. std. 

		#self,symbol,format,width,val_position,alert_position,alert_vals
		super().add_symbol_breakout(symbol,labels,alert_positions,alerts,data_ready)

	#find a way to bound the special checking value to. hmm. every update.
	# def add_breakout_symbol(self,symbol,format,alert_positions,alerts,data_ready):

	# 	#init the alert value
	# 	if symbol not in self.alerts:
	# 			self.alerts[symbol] = {}

	# 	for i in alert_positions:
	# 		self.alerts[symbol][alerts[i][2][5]] = 0

	# 	l = self.label_count

	# 	self.tickers_labels[symbol] = []
	# 	i = symbol

	# 	for j in range(len(format)):

	# 		if j==0:
	# 			self.tickers_labels[i].append(tk.Label(self.frame ,text=format[j],width=self.width[j]))
	# 			self.label_default_configure(self.tickers_labels[i][j])
	# 			self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
	# 		elif j==1:
	# 			self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
	# 			self.label_default_configure(self.tickers_labels[i][j])
	# 			self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
	# 			format[j].trace('w', lambda *_, text=format[j],label=self.tickers_labels[i][j]: self.status_change_color(text,label))

	# 		#when it is alert label creation, create a trace set for value position 
	# 		elif j in alert_positions:
	# 			self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
	# 			self.label_default_configure(self.tickers_labels[i][j])
	# 			self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)
	# 			#unpack value_position,alert_position,alertvals
	# 			value_position = alerts[j][0]
	# 			alert_position = alerts[j][1]
	# 			alert_vals = alerts[j][2]
	# 			format[value_position].trace('w', lambda *_, eval_string=format[j],label=self.tickers_labels[i][j],alertsvals=alert_vals,ready=data_ready,status=format[1]: self.alert(eval_string,label,alertsvals,ready,status))

	# 		elif j>1:
	# 			self.tickers_labels[i].append(tk.Label(self.frame ,textvariable=format[j],width=self.width[j]))
	# 			self.label_default_configure(self.tickers_labels[i][j])
	# 			self.tickers_labels[i][j].grid(row= l+2, column=j,padx=0)

	# 	#self.ticker_count +=1
	# 	self.label_count +=1

	# 	self.rebind(self.canvas,self.frame)

	# def alert(self,eval_string,eval_label,alerts_vals,ready,status):

	# 	#check how many std it is. `

	# 	#attention, only do the calculation when the database is set. 

	# 	if ready.get() == True and status.get() =="Connected":

	# 		symbol= alerts_vals[0]
	# 		time= alerts_vals[1].get()[:5]
			
	# 		cur_price= round(alerts_vals[2].get(),3)
	# 		mean= round(alerts_vals[3].get(),3)
	# 		std=  round(alerts_vals[4].get(),3)
	# 		alert_type = alerts_vals[5]

	# 		ts = timestamp(time)

	# 		#on certain alert_type, the math can be different. 


	# 		if std != 0:
	# 			cur = round((cur_price-mean)/std,3)
	# 			eval_string.set(str(cur)+" from mean")
	# 		else:
	# 			cur = 0
	# 			eval_string.set("Unable to process std 0")

	# 		#color. 

	# 		if cur <0.5:
	# 			eval_label["background"]="white"

	# 		elif cur>0.5 and cur<1:
				
	# 			alert_str = "Moderate "+alert_type
	# 			eval_label["background"]="#97FEA8"

	# 			if ts>570 and self.alerts[symbol][alert_type] < 0.5:
	# 				self.alerts[symbol][alert_type] = 0.5
	# 				self.alert_pannel.add_alerts([symbol,time,alert_str])
	# 				self.set_latest_alert(symbol, alert_str, time)

	# 		elif cur>1 and cur<2 and self.alerts[symbol][alert_type] < 1:
	# 			self.alerts[symbol][alert_type] = 1
	# 			alert_str = "High "+alert_type
	# 			eval_label["background"]="yellow"
	# 			if ts>570:
	# 				#only set when there is higher severity. 
	# 				self.alert_pannel.add_alerts([symbol,time,alert_str])
	# 				self.set_latest_alert(symbol, alert_str, time)
	# 		elif cur>2 and self.alerts[symbol][alert_type] < 2:

	# 			self.alerts[symbol][alert_type] = 2
	# 			### Send the alert to alert pannel.
	# 			alert_str = "Very high "+alert_type
	# 			eval_label["background"]="red"
	# 			if ts>570:
	# 				self.alert_pannel.add_alerts([symbol,time,alert_str])
	# 				self.set_latest_alert(symbol, alert_str, time)