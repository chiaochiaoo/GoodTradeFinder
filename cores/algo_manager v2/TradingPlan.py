from Symbol import *
from Triggers import *
from Strategy import *
from Strategy_Management import *
from constant import*
from Util_functions import *
import tkinter as tkvars
import time
import threading

# MAY THE MACHINE GOD BLESS THY AIM

class TradingPlan:

	def __init__(self,symbol:Symbol,entry_plan=None,entry_type=None,manage_plan=None,risk=None,ppro_out=None,TEST_MODE=False):

		self.symbol = symbol

		self.symbol.set_tradingplan(self)
		self.symbol_name = symbol.get_name()
		self.test_mode = TEST_MODE

		self.current_running_strategy = None
		self.entry_strategy_start = False

		self.entry_plan = None
		self.entry_type = None
		self.management_plan = None

		self.ppro_out = ppro_out

		self.expect_orders = ""
		# self.expect_long = False
		# self.expect_short = False

		self.flatten_order = False

		self.data = {}
		self.tkvars = {}

		self.tklabels= {} ##returned by UI.

		self.holdings = []
		self.current_price_level = 0
		self.price_levels = {}

		self.numeric_labels = [ACTRISK,ESTRISK,CURRENT_SHARE,TARGET_SHARE,INPUT_TARGET_SHARE,AVERAGE_PRICE,LAST_AVERAGE_PRICE,RISK_PER_SHARE,STOP_LEVEL,UNREAL,UNREAL_PSHR,REALIZED,TOTAL_REALIZED,TIMER,PXT1,PXT2,PXT3]
		self.string_labels = [MIND,STATUS,POSITION,RISK_RATIO,SIZE_IN,ENTRYPLAN,ENTYPE,MANAGEMENTPLAN]

		self.bool_labels= [AUTORANGE,AUTOMANAGE,RELOAD,SELECTED,ANCART_OVERRIDE]

		self.init_data(risk,entry_plan,entry_type,manage_plan)

	def init_data(self,risk,entry_plan,entry_type,manage_plan):

		
		for i in self.numeric_labels:
			self.data[i] = 0
			self.tkvars[i] = tk.DoubleVar(value=0)

		for i in self.string_labels:
			self.data[i] = ""
			self.tkvars[i] = tk.StringVar(value="")

		for i in self.symbol.numeric_labels:
			self.tkvars[i] = tk.DoubleVar(value=self.symbol.data[i])

		for i in self.bool_labels:
			self.data[i] = True
			self.tkvars[i] = tk.BooleanVar(value=True)

		self.data[ANCART_OVERRIDE]=False

		self.tkvars[SELECTED].set(False)
		#Non String, Non Numeric Value

		#Set some default value
		self.data[ESTRISK] = risk
		self.tkvars[ESTRISK].set(risk)
		self.tkvars[RISK_RATIO].set(str(0)+"/"+str(self.data[ESTRISK]))

		self.tkvars[ENTRYPLAN].set(entry_plan)
		self.tkvars[ENTYPE].set(entry_type)
		self.tkvars[MANAGEMENTPLAN].set(ONETOTWORISKREWARD)

		self.data[STATUS] = PENDING
		self.tkvars[STATUS].set(PENDING)

		# self.entry_plan_decoder(entry_plan,entry_type)
		# self.manage_plan_decoder(manage_plan)

	""" PPRO SECTION """

	def AR_toggle_check(self):
		"""
		This will happen whenever a trade is placed. 
		"""
		try:
			self.symbol.set_resistence(self.tkvars[RESISTENCE].get())
			self.symbol.set_support(self.tkvars[SUPPORT].get())
		except Exception as e:
			log_print(self.symbol_name,"error on sup/res input.",e)

	def AR_toggle(self):
		try:
			if self.data[POSITION] =="" and self.tkvars[AUTORANGE].get()==False:
				self.tklabels[SUPPORT]["state"] = "normal"
				self.tklabels[RESISTENCE]["state"] = "normal"
			else:
				self.AR_toggle_check()
				self.tklabels[SUPPORT]["state"] = "disabled"
				self.tklabels[RESISTENCE]["state"] = "disabled"
		except:
			pass

	def ppro_update_price(self,bid,ask,ts):

		if bid!=self.symbol.get_bid() or ask!=self.symbol.get_ask():
			self.symbol.update_price(bid,ask,ts,self.tkvars[AUTORANGE].get(),self.tkvars[STATUS].get())

			#check stop. 
			if self.data[POSITION]!="":
				self.check_pnl(bid,ask)

			#check triggers
			if self.current_running_strategy!=None:
				self.current_running_strategy.update()

		# except Exception as e:
		# 	log_print("TP issue:",e)

	def check_pnl(self,bid,ask):
		"""
		PNL, STOP TRIGGER.
		"""

		#log_print("PNL CHECK ON",self.symbol_name,self.data[POSITION])
		flatten = False
		if self.data[POSITION]==LONG:
			price = bid
			gain = round((price-self.data[AVERAGE_PRICE]),4)

			if price <= self.data[STOP_LEVEL]:
				flatten=True

		elif self.data[POSITION]==SHORT:
			price = ask
			gain = round(self.data[AVERAGE_PRICE]-price,4)
			if price >=  self.data[STOP_LEVEL]:
				flatten=True

		if self.data[CURRENT_SHARE] >0:
			self.data[UNREAL_PSHR] = gain
			self.data[UNREAL]= round(gain*self.data[CURRENT_SHARE],4)

		if flatten and self.flatten_order==False:
			self.flatten_order=True
			self.ppro_out.send(["Flatten",self.symbol_name])

		self.update_displays()

	def ppro_process_orders(self,price,shares,side):
		
		#log_print("TP processing:",self.symbol_name,price,shares,side)
		if self.data[POSITION]=="": # 1. No position.
			if self.expect_orders==side:
				self.ppro_confirm_new_order(price,shares,side)
			else:
				log_print("TP processing: unexpected orders on",self.symbol_name)
		
		else:  # 2. Have position. 

			if self.data[POSITION]==side: #same side.
				self.ppro_orders_loadup(price,shares,side)
			else: #opposite
				self.ppro_orders_loadoff(price,shares,side)

		# if self.test_mode:
		# 	log_print("TP processing:",self.data)
		self.update_displays()

	def ppro_confirm_new_order(self,price,shares,side):

		"""set the state as running, then load up"""

		log_print(self.symbol_name,"New order confirmed:",price,shares,side)
		self.mark_algo_status(RUNNING)
		self.data[POSITION]=side
		self.tkvars[POSITION].set(side)
		self.data[REALIZED] = 0
		self.flatten_order = False
		self.ppro_orders_loadup(price,shares,side)

	def ppro_orders_loadup(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		self.data[CURRENT_SHARE] = self.data[CURRENT_SHARE] + shares

		if current ==0 or self.data[CURRENT_SHARE]==0:
			self.data[AVERAGE_PRICE] = round(price,3)
		else:
			self.data[AVERAGE_PRICE]= round(((self.data[AVERAGE_PRICE]*current)+(price*shares))/self.data[CURRENT_SHARE],3)

		for i in range(shares):
			self.holdings.append(price)

		self.adjusting_risk()

		if self.data[AVERAGE_PRICE]!=self.data[LAST_AVERAGE_PRICE]:
			self.management_plan.on_loading_up()
			
			log_print(self.symbol_name," ",side,",",self.data[AVERAGE_PRICE]," at ",self.data[CURRENT_SHARE],"act risk:",self.data[ACTRISK])

		self.data[LAST_AVERAGE_PRICE] = self.data[AVERAGE_PRICE]

	def ppro_orders_loadoff(self,price,shares,side):

		current = self.data[CURRENT_SHARE]

		self.data[CURRENT_SHARE] = current-shares	
		
		gain = 0

		if self.data[POSITION] == LONG:
			for i in range(shares):
				try:
					gain += price-self.holdings.pop()
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")
		elif self.data[POSITION] == SHORT:
			for i in range(shares):
				try:
					gain += self.holdings.pop() - price	
				except:
					log_print("TP processing: Holding calculation error,holdings are empty.")	

		self.data[REALIZED]+=gain
		self.data[REALIZED]= round(self.data[REALIZED],2)

		self.adjusting_risk()

		log_print(self.symbol_name," sold:",shares," current shares:",self.data[CURRENT_SHARE],"realized:",self.data[REALIZED])

		#finish a trade if current share is 0.

		if self.data[CURRENT_SHARE] <= 0:
			
			self.clear_trade()

	def clear_trade(self):

		self.data[UNREAL] = 0
		self.data[UNREAL_PSHR] = 0
		self.data[TOTAL_REALIZED] += self.data[REALIZED]
		self.data[TOTAL_REALIZED] = round(self.data[TOTAL_REALIZED],2)
		self.data[REALIZED] = 0

		self.data[TARGET_SHARE] = 0
		#mark it done.

		#prevent manual conflit.
		self.expect_orders = ""
		##################

		self.mark_algo_status(DONE)
		self.set_mind("Trade completed.",VERYLIGHTGREEN)
		self.data[POSITION] = ""

		self.tkvars[POSITION].set("")
		self.tklabels[AUTORANGE]["state"] = "normal"
		self.current_price_level = 0
		self.current_running_strategy = None

		#if reload is on, revert it back to entry stage. 
		if self.tkvars[RELOAD].get() == True:
			log_print("TP processing:",self.symbol_name,":"," Reload activated. Trading triggers re-initialized. ")
			self.tkvars[RELOAD].set(False)
			self.start_tradingplan()
			
	def ppro_order_rejection(self):

		self.mark_algo_status(REJECTED)


	""" risk related ## """

	def adjusting_risk(self):

		if self.data[POSITION] == LONG:
			self.data[ACTRISK] = round(((self.data[AVERAGE_PRICE]-self.data[STOP_LEVEL])*self.data[CURRENT_SHARE]),2)
		else:
			self.data[ACTRISK] = round(((self.data[STOP_LEVEL]-self.data[AVERAGE_PRICE])*self.data[CURRENT_SHARE]),2)

		#diff = self.data[ACTRISK]-self.data[ESTRISK]
		ratio = (self.data[ACTRISK]/self.data[ESTRISK])-0.3#self.data[ESTRISK]/diff
		if ratio>1.2 : ratio = 1.2
		if ratio<0 : ratio = 0
		##change color and change text.

		self.tklabels[RISK_RATIO]["background"] = hexcolor_red(ratio)
		self.tkvars[RISK_RATIO].set(str(self.data[ACTRISK])+"/"+str(self.data[ESTRISK]))

		if self.data[CURRENT_SHARE] == 0:
			self.tklabels[RISK_RATIO]["background"] = DEFAULT

	def flatten_cmd(self):
		self.ppro_out.send(["Flatten",self.symbol_name])

		if self.tkvars[STATUS].get()==PENDING:
			self.cancel_algo()

	"""	UI related  """
	def update_symbol_tkvar(self):
		self.tkvars[SUPPORT].set(self.symbol.get_support())
		self.tkvars[RESISTENCE].set(self.symbol.get_resistence())

	def update_displays(self):

		self.tkvars[SIZE_IN].set(str(self.data[CURRENT_SHARE])+"/"+str(self.data[TARGET_SHARE]))
		self.tkvars[REALIZED].set(str(self.data[REALIZED]))
		self.tkvars[TOTAL_REALIZED].set(str(self.data[TOTAL_REALIZED]))
		self.tkvars[UNREAL].set(str(self.data[UNREAL]))
		self.tkvars[UNREAL_PSHR].set(str(self.data[UNREAL_PSHR]))
		self.tkvars[AVERAGE_PRICE].set(self.data[AVERAGE_PRICE])

		#check color.f9f9f9

		self.tklabels[REALIZED]["background"]

		self.tklabels[UNREAL]["background"]

		if self.data[UNREAL_PSHR]>0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGGREEN
			self.tklabels[UNREAL]["background"] = STRONGGREEN
		elif self.data[UNREAL_PSHR]<0:
			self.tklabels[UNREAL_PSHR]["background"] = STRONGRED
			self.tklabels[UNREAL]["background"] = STRONGRED
		else:
			self.tklabels[UNREAL_PSHR]["background"] = DEFAULT
			self.tklabels[UNREAL]["background"] =DEFAULT

		if self.data[REALIZED]==0:
			self.tklabels[REALIZED]["background"] = DEFAULT
		elif self.data[REALIZED]>0:
			self.tklabels[REALIZED]["background"] = STRONGGREEN
		elif self.data[REALIZED]<0:
			self.tklabels[REALIZED]["background"] = STRONGRED

		if self.data[TOTAL_REALIZED]==0:
			self.tklabels[TOTAL_REALIZED]["background"] = DEFAULT
		elif self.data[TOTAL_REALIZED]>0:
			self.tklabels[TOTAL_REALIZED]["background"] = STRONGGREEN
		elif self.data[TOTAL_REALIZED]<0:
			self.tklabels[TOTAL_REALIZED]["background"] = STRONGRED

		current_level = self.current_price_level

		if  current_level==1:
			self.tklabels[PXT1]["background"] = LIGHTYELLOW
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = DEFAULT
		elif  current_level==2:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = LIGHTYELLOW
			self.tklabels[PXT3]["background"] = DEFAULT
		elif  current_level==3:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = LIGHTYELLOW
		else:
			self.tklabels[PXT1]["background"] = DEFAULT
			self.tklabels[PXT2]["background"] = DEFAULT
			self.tklabels[PXT3]["background"] = DEFAULT	

	def mark_algo_status(self,status):

		self.data[STATUS] = status
		self.tkvars[STATUS].set(status)


		if status == DEPLOYED:
			self.input_lock(True)
			self.tklabels[STATUS]["background"] = LIGHTYELLOW

		elif status == RUNNING:
			self.tklabels[STATUS]["background"] = GREEN

		elif status == REJECTED:
			self.tklabels[STATUS]["background"] = "red"

		elif status == DONE:
			self.tklabels[STATUS]["background"] = DEEPGREEN

		elif status == PENDING:
			self.input_lock(False)
			self.tklabels[STATUS]["background"] = DEFAULT

			#if reload is on, turn it back on.
		# elif status == CANCELED:#canceled 

		# 	if self.order_tkstring[id_]["algo_status"].get() == "Pending":
		# 		self.order_tkstring[id_]["algo_status"].set(status)

	def set_mind(self,str,color=DEFAULT):

		self.tkvars[MIND].set(str)
		self.tklabels[MIND]["background"]=color

	""" DATA MANAGEMENT  """
	
	def get_risk(self):
		return self.data[ESTRISK]

	def get_data(self):
		return self.data

	""" Deployment initialization """

	def input_lock(self,lock):

		state =""
		if lock: state="disabled"
		else: state = "normal"

		self.tklabels[ENTRYPLAN]["state"] = state
		self.tklabels[ENTYPE]["state"] = state
		self.tklabels[TIMER]["state"] = state
		self.tklabels[MANAGEMENTPLAN]["state"] = state
		self.tklabels[AUTORANGE]["state"] = state

	def cancel_algo(self):
		if self.tkvars[STATUS].get()==PENDING:
			self.mark_algo_status(CANCELED)

	def cancle_deployment(self):
		if self.data[POSITION] =="" and self.data[CURRENT_SHARE]==0:
			self.mark_algo_status(PENDING)
			self.stop_tradingplan()
		else:
			log_print("cannot cancel, holding positions.")

	def deploy(self):

		if self.tkvars[STATUS].get() ==PENDING:

			try:
				entryplan=self.tkvars[ENTRYPLAN].get()
				entry_type=self.tkvars[ENTYPE].get()
				entrytimer=int(self.tkvars[TIMER].get())
				manage_plan =self.tkvars[MANAGEMENTPLAN].get()

				self.set_mind("",DEFAULT)
				self.entry_plan_decoder(entryplan, entry_type, entrytimer)
				self.manage_plan_decoder(manage_plan)

				log_print("Deploying:",self.symbol_name,self.entry_plan.get_name(),self.symbol.get_support(),self.symbol.get_resistence(),entry_type,entrytimer,self.management_plan.get_name(),"risk:",self.data[ESTRISK])
				self.AR_toggle_check()
				self.start_tradingplan()
			except Exception as e:

				log_print("Deplying Error:",self.symbol_name,e)
	
	def start_tradingplan(self):
		self.mark_algo_status(DEPLOYED)

		self.entry_plan.on_deploying()
		self.management_plan.on_deploying()
		self.current_running_strategy = self.entry_plan



	def stop_tradingplan(self):
		self.current_running_strategy = None

	""" Plan Handler """	
	def entry_plan_decoder(self,entry_plan,entry_type,entrytimer):

		if entry_type ==None or entry_type ==INSTANT:
			instant = 1 
		if entry_type ==INCREMENTAL:
			instant = 3 

		if instant >1:
			if entrytimer<5:
				entrytimer = 5

		if entry_plan == BREAKANY:
			self.set_EntryStrategy(BreakAny(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAKUP:
			self.set_EntryStrategy(BreakUp(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAKDOWN:
			self.set_EntryStrategy(BreakDown(entrytimer,instant,self.symbol,self))
		elif entry_plan == BREAISH:
			self.set_EntryStrategy(Bearish(entrytimer,instant,self.symbol,self))
		elif entry_plan == BULLISH:
			self.set_EntryStrategy(Bullish(entrytimer,instant,self.symbol,self))
		elif entry_plan == RIPSELL:
			self.set_EntryStrategy(Ripsell(entrytimer,instant,self.symbol,self))
		elif entry_plan == DIPBUY:
			self.set_EntryStrategy(Dipbuy(entrytimer,instant,self.symbol,self))
		elif entry_plan == FADEANY:
			self.set_EntryStrategy(Fadeany(entrytimer,instant,self.symbol,self))
		else:
			log_print("unkown plan")

	def manage_plan_decoder(self,manage_plan):

		if manage_plan ==NONE: self.tkvars[MANAGEMENTPLAN].set(NONE)
		if manage_plan == THREE_TARGETS:
			self.set_ManagementStrategy(ThreePriceTargets(self.symbol,self))
		if manage_plan == SMARTTRAIL:
			self.set_ManagementStrategy(SmartTrail(self.symbol,self))

		if manage_plan == ANCARTMETHOD:
			self.set_ManagementStrategy(AncartMethod(self.symbol,self))

		if manage_plan == ONETOTWORISKREWARD:
			self.set_ManagementStrategy(OneToTWORiskReward(self.symbol,self))

		if manage_plan == ONETOTWORISKREWARDOLD:
			self.set_ManagementStrategy(OneToTWORiskReward_OLD(self.symbol,self))

	def set_EntryStrategy(self,entry_plan:Strategy):
		self.entry_plan = entry_plan
		#self.entry_plan.set_symbol(self.symbol,self)

		self.data[ENTRYPLAN] = entry_plan.get_name()
		#self.tkvars[ENTRYPLAN].set(entry_plan.get_name())

	def set_ManagementStrategy(self,management_plan:Strategy):
		self.management_plan = management_plan
		self.management_plan.set_symbol(self.symbol,self)		
		self.data[MANAGEMENTPLAN] = management_plan.get_name()

	def on_finish(self,plan):
		
		if plan==self.entry_plan:
			log_print(self.symbol_name,self.entry_plan.get_name()," completed.")
			self.entry_strategy_done()
			# done = threading.Thread(target=self.entry_strategy_done, daemon=True)
			# done.start()
		elif plan==self.management_plan:
			self.management_strategy_done()
			log_print(self.symbol_name,"management strategy completed.")
		else:
			log_print("Trading Plan: UNKONW CALL FROM Strategy")

	def entry_strategy_done(self):

		self.management_plan.on_start()
		self.current_running_strategy = self.management_plan

	def management_strategy_done(self):

		pass

# if __name__ == '__main__':

# 	#TEST CASES for trigger.
# 	root = tk.Tk() 
# 	aapl = Symbol("aapl")
# 	TP = TradingPlan(aapl)
# 	aapl.set_tradingplan(TP)
# 	aapl.set_phigh(16)
# 	aapl.set_plow(15)

# 	b = BreakUp(0,False,aapl,TP)
# 	#b = BreakUp(0)
# 	TP.set_EntryStrategy(b)
# 	TP.start_EntryStrategy()

	
# 	aapl.update_price(10,10,0)
# 	aapl.update_price(11,11,1)
# 	aapl.update_price(12,12,2)
# 	aapl.update_price(13,13,3)
# 	aapl.update_price(14,14,4)
# 	aapl.update_price(15,15,5)
# 	##### DECRESE#######
# 	aapl.update_price(5,5,6)
# 	aapl.update_price(13,13,7)

# 	aapl.update_price(10,10,8)
# 	###### INCREASE #############
# 	aapl.update_price(11,11,9)
# 	aapl.update_price(12,12,10)
# 	aapl.update_price(13,13,11)
# 	aapl.update_price(14,14,12)
# 	aapl.update_price(15,15,13)
# 	aapl.update_price(16,16,14)
# 	aapl.update_price(17,17,15)
# 	aapl.update_price(18,18,16)
# 	aapl.update_price(19,19,17)


# 	root.mainloop()