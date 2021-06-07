from constant import *
from Util_functions import *

class AbstractTrigger:

	"""
	All trigger class basically have functons of.

	1. check_conditions.
	2. Triggers events.
	3. Set next triggers
	4. Return next triggers. 

	"""
	def __init__(self,description,conditions,trigger_timer:int,trigger_limit,mind_string=None):

		#self.symbol = symbol
		#bigger, or less than. 
		self.symbol = None
		self.symbol_name = None
		self.symbol_data = None
		self.description = description

		self.mind = None
		self.mind_label = None
		#How long it need sto trigger it.
		self.trigger_timer = trigger_timer

		self.activation = True
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0

		#How many times it can be triggered. 
		self.trigger_count = 0
		self.trigger_limit = trigger_limit


		self.mind_string = mind_string

		if conditions!=None:
			self.conditions = conditions 
		else:
			self.conditions = []

		self.next_triggers = set()

	def add_conditions(subject1,d_type1,subject2,d_type2,type_):
		self.conditions.append([subject1,d_type1,subject2,d_type2,type_])

	def decode_conditions(self,i):

		#log_print(i)
		#['symbol_data', 'ask', '>', 'symbol_data', 'phigh']
		s1 =i[0]
		t1= i[1]
		type_ = i[2]
		s2= i[3]
		t2= i[4]
		
		s1_=None
		s2_=None

		if s1 == SYMBOL_DATA:
			s1_ = self.symbol_data
		elif s1 == TP_DATA:
			s1_ = self.tp_data
		else:
			log_print("Trigger decoding error on ",s1,self.description)

		if s2 == SYMBOL_DATA:
			s2_ = self.symbol_data
		elif s2 == TP_DATA:
			s2_ = self.tp_data
		else:
			log_print("Trigger decoding error on ",s2,self.description)

		#log_print(s1_,s2_,t1,t2,type_)
		return s1_,s2_,t1,t2,type_

	""" return True if a trade is succesful.(in the entry range). else False"""
	def pre_deploying_check(self):

		eval = True

		for i in self.conditions:
			s1,s2,t1,t2,type_= self.decode_conditions(i)
			if type_ ==">":
				if not s1[t1] > s2[t2]:
					eval = False	
			elif type_ =="<":
				if not s1[t1] < s2[t2]:
					eval = False
			#print(s1[t1],type_,s2[t2],eval)
		return eval

	def deactivate(self):
		self.activation = False

	def check_conditions(self):
		
		eval = True
		"""
		1. Check if all conditions are met.
		2. If so, take note of time. If time trigger is 0, immediatly trigger event. 
		3. If time trigger is above 0. Check if it is already triggered. 
		"""
		if self.activation:
			for i in self.conditions:
				s1,s2,t1,t2,type_= self.decode_conditions(i)
				if type_ ==">":
					if not s1[t1] > s2[t2]:
						eval = False	
				elif type_ =="<":
					if not s1[t1] < s2[t2]:
						eval = False

			if eval ==True:

				if self.trigger_timer == 0:
					return self.is_trigger()
				else:
					if not self.triggered:
						self.triggered = True
						self.trigger_time = self.symbol.get_time() 
						self.trigger_duration = 0
						self.set_mind(str(int(self.trigger_timer)) +" s to trigger")
					else:
						self.trigger_duration = self.symbol.get_time() - self.trigger_time
						self.set_mind(str(int(self.trigger_timer - self.trigger_duration)) +" s to trigger")
						if self.trigger_duration >= self.trigger_timer:
							return self.is_trigger()

			else:
				if self.triggered:
					self.set_mind("Trigger breaks. reset.")
				self.reset()
		# except Exception as e:
		# 	log_print("Trigger error on ",self.description,e)

		return False

	def update_trigger_duration(self):

		if self.triggered == False: #first time trigger

			self.triggered = True
			self.trigger_time = self.symbol.get_time() 
			self.trigger_duration = 0

		else: #second tie trigger. update trigger duation
			self.trigger_duration = self.symbol.get_time() - self.trigger_time

		return self.is_trigger()

	def is_trigger(self):

		self.trigger_count+=1
		self.trigger_event()
		if self.trigger_count == self.trigger_limit:
			self.trigger_count = 0
			self.activation = False
			return True
		else:
			self.reset()
			return False 	

	def trigger_event(self):  #OVERRIDEn n 

		if self.mind_string!=None:
			self.set_mind(self.mind_string) 
		try:
			log_print("Trigger:",self.description,"on", self.symbol.get_name(),"at time", self.symbol.get_time())
		except:
			log_print("Trigger:",self.description)
		### REPLACE the current trategy with current states. (when repeate is met.)

	def set_symbol(self,symbol,tradingplan,ppro_out):
		self.symbol = symbol
		self.symbol_name = symbol.get_name()
		self.symbol_data = self.symbol.get_data()
		self.ppro_out = ppro_out

		self.tradingplan = tradingplan 
		self.tp_data = self.tradingplan.get_data()

		#log_print(self.symbol_name,self.description,self.trigger_timer,self.trigger_limit)

		self.set_mind_object()

	def set_mind(self,str,color=DEFAULT):

		if self.mind==None:
			self.set_mind_object()
		if self.mind!=None:
			self.mind.set(str)
			self.mind_label["background"]=color

	def clear_mind(self):
		self.set_mind(" ",DEFAULT)

	def set_mind_object(self):
		try:
			self.mind = self.tradingplan.tkvars[MIND]
			self.mind_label = self.tradingplan.tklabels[MIND]
		except:
			pass

	def add_next_trigger(self,next_trigger):
		self.next_triggers.add(next_trigger)

	def get_next_triggers(self):
		return self.next_triggers

	def get_trigger_state(self):
		""" if true: still useful 
		    if false: already used """
		return self.activation

	def log_print(self):
		log_print("Trigger",self.description)

	def reactivate(self):
		self.activation = True
		self.trigger_count = 0

	def reset(self):
		self.triggered = False
		self.trigger_time = 0
		self.trigger_duration = 0
		
		#self.clear_mind()
	def total_reset(self):
		self.reactivate()
		self.reset()

#self,subject1,type_,subject2,trigger_timer:int,description,trigger_limit=1

class Purchase_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out):
		super().__init__(description,conditions,trigger_timer,trigger_limit)

		#log_print("purchase_trigger,",self.trigger_timer,self.trigger_limit)
		self.pos = pos

		self.entry = conditions[0][4]

		self.stop = stop
		self.ppro_out =ppro_out
		self.risk = risk 
		#self.conditions = conditions 

		self.entry_text =""
		self.trigger_text = ""

		self.entry_price = 0
		self.stop_price = 0

		checker = False
		for i in conditions:
			if len(i)!=5:
				checker = True
				break

		if checker:
			log_print("Trigger problem on purchase_trigger,conditions:",conditions)
	#add the actual stuff here.


	def trigger_event(self):

		"""
		HERE I NEED TO SEPERATE BY CASES.
		IF IT IS OVERRIDDEN.
		THEN, 1. PUNCH IN DIRECTLY BY # AMOUNT OF SHARES
			  2. DON"T OVERRIDE STOP VALUE.(ANCARTMANAGE WILL DO IT)
		IF NOT, PROCEED AS USUAL. 
		"""

		if self.tradingplan.tkvars[MANAGEMENTPLAN].get() == ANCARTMETHOD:

			share = int(self.tradingplan.data[TARGET_SHARE]/self.trigger_limit)

			if self.pos!="":
				self.tradingplan.expect_orders = self.pos
				if self.trigger_count!= self.trigger_limit:
					self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
				else:
					self.set_mind("Entry: Complete",GREEN)
			if self.pos == LONG:

				self.tradingplan.data[STOP_LEVEL]= round(self.symbol_data[BID]-self.tradingplan.data[RISK_PER_SHARE],2)
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])
				if share>0:
					self.ppro_out.send(["Buy",self.symbol_name,share,self.description])
			elif self.pos ==SHORT:

				self.tradingplan.data[STOP_LEVEL]= round(self.symbol_data[ASK]+self.tradingplan.data[RISK_PER_SHARE],2)
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])

				if share>0:
					self.ppro_out.send(["Sell",self.symbol_name,share,self.description])
			else:
				log_print("unidentified side. ")

		else:
			share = self.shares_calculator()

			self.entry_price = self.symbol_data[self.entry]
			
			log_print(self.symbol_name,"Trigger: ",self.pos,share,"stop :",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

			if self.pos!="":
				self.tradingplan.expect_orders = self.pos
				if self.trigger_count!= self.trigger_limit:
					self.set_mind("Entry: "+str(self.trigger_count)+"/"+str(self.trigger_limit),DEFAULT)
				else:
					self.set_mind("Entry: Complete",GREEN)

			if self.pos == LONG:

				self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

				self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
				#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

				#self.tradingplan.expect_orders = True
				#log_print("Trigger: Purchase: ",self.symbol_name,self.pos,share,"at",self.symbol.get_time())
			
				if share>0:
					self.ppro_out.send(["Buy",self.symbol_name,share,self.description])
					
			elif self.pos ==SHORT:

				self.tradingplan.data[STOP_LEVEL]=self.stop_price#self.symbol_data[self.stop]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.stop_price)

				self.tradingplan.data[BREAKPRICE]=self.entry_price#self.symbol_data[self.stop]
				#self.tradingplan.tkvars[BREAKPRICE].set(self.entry_price)

				if share>0:
					self.ppro_out.send(["Sell",self.symbol_name,share,self.description])
			else:
				log_print("unidentified side. ")


		self.tradingplan.update_displays()

	def shares_calculator(self):

		#Now i need trigger limit into consideration.

		# if self.pos ==LONG:
		# 	risk_per_share =  abs(self.symbol_data[self.stop]-self.symbol_data[ASK])
		# else:
		# 	risk_per_share =  abs(self.symbol_data[self.stop]-self.symbol_data[BID])

		# if risk_per_share == 0:
		# 	risk_per_share = 0.1

		if self.pos ==LONG:
			risk_per_share = abs(self.symbol_data[ASK]-self.symbol_data[self.stop])

			self.stop_price = self.symbol_data[self.stop]

			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006
				self.stop_price = round(self.symbol_data[BID] - risk_per_share,2)

		elif self.pos ==SHORT:
			risk_per_share = abs(self.symbol_data[self.stop]-self.symbol_data[BID])
			self.stop_price = self.symbol_data[self.stop]
			if risk_per_share < self.symbol_data[ASK]*0.0006:
				log_print(self.symbol_name,": stop too close:",round(risk_per_share,2)," adjusted to",str(round(self.symbol_data[ASK]*0.0006,2)))
				risk_per_share = self.symbol_data[ASK]*0.0006
				self.stop_price = round(self.symbol_data[ASK] + risk_per_share,2)

		if self.symbol_data[ASK]>100 and risk_per_share <0.12:
			risk_per_share = 0.12

		if self.symbol_data[ASK]<100 and self.symbol_data[ASK]>5 and risk_per_share <0.1:
			risk_per_share = 0.1

		if self.symbol_data[ASK]<5 and risk_per_share <0.02:
			risk_per_share = 0.02

		shares = int((self.risk)/risk_per_share)

		if self.tradingplan.data[TARGET_SHARE]==0:
			self.tradingplan.data[TARGET_SHARE]=shares

		return int(shares/self.trigger_limit)


class Three_price_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				#half way.
				half_way = round((self.tradingplan.data[STOP_LEVEL] + self.tradingplan.data[AVERAGE_PRICE])/2,2)
				self.tradingplan.data[STOP_LEVEL]=half_way
				self.tradingplan.tkvars[STOP_LEVEL].set(half_way)

			if self.tradingplan.current_price_level == 2:
				self.ppro_out.send([action,self.symbol_name,share,self.description])
				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()

class TwoToOneTriggerOLD(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				#half way.
				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])

			if self.tradingplan.current_price_level == 2:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL]= self.tradingplan.data[PXT1]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[PXT1])

				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()



""" The new trigger only adjust the stops. 
"""
class TwoToOneTrigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,strategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=9)

		self.strategy =strategy
		self.conditions = [] 

		self.second_oders = {}
		self.third_orders = {}

	def set_orders(self,second,third):
		self.second_oders = second
		self.third_orders = third

	def check_conditions(self):

		level = ""

		if self.strategy.orders_level ==1: level= TRIGGER_PRICE_1
		elif self.strategy.orders_level ==2: level= TRIGGER_PRICE_2
		elif self.strategy.orders_level ==3: level= TRIGGER_PRICE_3
		elif self.strategy.orders_level ==4: level= TRIGGER_PRICE_4
		elif self.strategy.orders_level ==5: level= TRIGGER_PRICE_5
		elif self.strategy.orders_level ==6: level= TRIGGER_PRICE_6
		elif self.strategy.orders_level ==7: level= TRIGGER_PRICE_7
		elif self.strategy.orders_level ==8: level= TRIGGER_PRICE_8
		elif self.strategy.orders_level ==9: level= TRIGGER_PRICE_9

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:

		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())

		#add the actual stuff here.

	def trigger_event(self):

		if self.strategy.orders_level == 1:
			
			#BREAK EVEN
			self.tradingplan.data[STOP_LEVEL]=round((self.tradingplan.data[STOP_LEVEL]*3+self.tradingplan.data[AVERAGE_PRICE])/4,2)
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])
			self.set_mind("75% risk",GREEN)
		if self.strategy.orders_level == 2:
			
			#BREAK EVEN
			self.tradingplan.data[STOP_LEVEL]=round((self.tradingplan.data[STOP_LEVEL]*2+self.tradingplan.data[AVERAGE_PRICE])/3,2)
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])
			self.set_mind("Half risk",GREEN)

		if self.strategy.orders_level == 3:
			
			#BREAK EVEN
			self.tradingplan.data[STOP_LEVEL]=round(self.tradingplan.data[AVERAGE_PRICE],2)
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
			self.set_mind("Break even",GREEN)

		if self.strategy.orders_level == 4:
			self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 2
			self.set_mind("Covered No."+str(1)+" lot.",GREEN)

		if self.strategy.orders_level == 5:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[TRIGGER_PRICE_3]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[TRIGGER_PRICE_3])
			
		if self.strategy.orders_level == 6:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.current_price_level = 3
			self.set_mind("Covered No."+str(2)+" lot.",GREEN)
			self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[TRIGGER_PRICE_4]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[TRIGGER_PRICE_4])

		if self.strategy.orders_level == 7:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[TRIGGER_PRICE_5]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[TRIGGER_PRICE_5])

		if self.strategy.orders_level == 8:
			self.strategy.deploy_n_batch_torpedoes(self.strategy.orders_level)
			self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[TRIGGER_PRICE_6]
			self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[TRIGGER_PRICE_6])

		# log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])
		self.strategy.orders_level +=1
		self.tradingplan.adjusting_risk()
		self.tradingplan.update_displays()



class ANCART_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,ppro_out):
		super().__init__(description,None,trigger_timer=0,trigger_limit=3)

		self.ppro_out =ppro_out
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2
		if self.tradingplan.current_price_level ==3: level= PXT3

		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())
	#add the actual stuff here.
	def trigger_event(self):

		share = min(self.tradingplan.data[TARGET_SHARE]//3,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:
				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL] = self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])

			if self.tradingplan.current_price_level == 2:

				self.ppro_out.send([action,self.symbol_name,share,self.description])

				self.tradingplan.data[STOP_LEVEL] = self.tradingplan.data[PXT1]

				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[STOP_LEVEL])
				#move the stop to break even.

			if self.tradingplan.current_price_level == 3:
				self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		log_print(self.symbol_name," Hit price target", self.tradingplan.current_price_level,"New Stop:",self.tradingplan.data[STOP_LEVEL])

		i
		self.set_mind("Covered No."+str(self.tradingplan.current_price_level)+" lot.",GREEN)
		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()


class SmartTrailing_trigger(AbstractTrigger):
	#Special type of trigger, overwrites action part. everything else is generic.
	def __init__(self,description,SmartTrailStrategy):
		super().__init__(description,None,trigger_timer=0,trigger_limit=2)

		self.SmartTrail =SmartTrailStrategy
		self.conditions = [] 

	def check_conditions(self):

		level = ""
		if self.tradingplan.current_price_level ==1: level= PXT1
		if self.tradingplan.current_price_level ==2: level= PXT2

		#i need to think of a way to let it forever stays at level 3. 
		if self.tradingplan.current_price_level ==3: level= PXT3


		if self.tradingplan.data[POSITION] == LONG:
			self.conditions = [[SYMBOL_DATA,ASK,">",TP_DATA,level]]
		elif self.tradingplan.data[POSITION] == SHORT:
			self.conditions = [[SYMBOL_DATA,BID,"<",TP_DATA,level]]

		#if self.tradingplan.data[POSITION]!="" and self.tradingplan.data[CURRENT_SHARE]>0:
		if self.tradingplan.data[POSITION]!="":
			return(super().check_conditions())


	#add the actual stuff here.
	def trigger_event(self):

		#share = min(self.tradingplan.data[TARGET_SHARE]//4,self.tradingplan.data[CURRENT_SHARE])

		self.pos = self.tradingplan.data[POSITION]
		#log_print("Trigger: Purchase PPRO EVENT: ",self.symbol_name,s,share,"at","stop:",self.stop,self.symbol_data[self.stop],self.symbol.get_time())

		####################  SIDE.  ########################################
		action = ""
		if self.pos ==LONG:
			action = SELL
		elif self.pos ==SHORT:
			action = BUY

		if action !="":
			if self.tradingplan.current_price_level == 1:

				#just change the STOP!!!!
				#half way.
				half_way = round((self.tradingplan.data[STOP_LEVEL] + self.tradingplan.data[AVERAGE_PRICE])/2,2)
				self.tradingplan.data[STOP_LEVEL]=half_way
				self.tradingplan.tkvars[STOP_LEVEL].set(half_way)

				self.tradingplan.adjusting_risk()
				log_print(self.symbol_name,"Reduce to 0.50 risk.")
				self.set_mind("50% risk",GREEN)


			if self.tradingplan.current_price_level == 2:

				#once it's level 2, it stays here. 

				self.tradingplan.data[STOP_LEVEL]=self.tradingplan.data[AVERAGE_PRICE]
				self.tradingplan.tkvars[STOP_LEVEL].set(self.tradingplan.data[AVERAGE_PRICE])
				self.SmartTrail.distance = abs(self.tradingplan.data[PXT2]-self.tradingplan.data[STOP_LEVEL])
				self.tradingplan.adjusting_risk()
				#self.set_mind("risk-free",GREEN)
				log_print(self.symbol_name,"Break even initiated.")
				#move the stop to break even.

			#if self.tradingplan.current_price_level == 3:
				#self.ppro_out.send([action,self.symbol_name,self.tradingplan.data[CURRENT_SHARE],"manage "])

				#move the stop to first price level. 
		else:
			log_print("unidentified side. ")

		self.tradingplan.current_price_level+=1
		self.tradingplan.update_displays()
# s = SingleEntry(ASK,">",PREMARKETHIGH,0,"BUY BREAK UP")
# s.trigger_event()