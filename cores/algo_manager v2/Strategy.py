from constant import *
from Symbol import *
from Triggers import *
import sys, inspect
# "Omnissiah, Omnissiah.

# From the Bleakness of the mind
# Omnissiah save us
# From the lies of the Antipath
# Circuit preserve us
# From the Rage of the Beast
# Iron protect us
# From the temptations of the Fleshlord
# Silica cleanse us
# From the Ravages of the Destroyer
# Anima Shield us

# Machine God Set Us Free
# Omnissiah, Omnissiah."

class Strategy: 

	"""
	ABSTRACT CLASS. the beginning of a sequence, containing one or more triggers.

	function:

	update : for each trigger.
		   -  Can be used for updating itself too (when overwrite.) 
	initialize : 
	"""
	def __init__(self,name,symbol:Symbol,tradingplan):

		self.strategy_name = name
		self.current_triggers = set()
		self.initial_triggers = set()
		self.symbol=None
		self.tradingplan =None
		self.ppro_out = None
		self.timer = 0
		self.all_triggers = []

		self.risk = 0

		self.set_symbol(symbol,tradingplan)

	def get_name(self):
		return self.strategy_name

	def add_initial_triggers(self,trigger):
		self.current_triggers.add(trigger)
		self.initial_triggers.add(trigger)
		trigger.set_symbol(self.symbol, self.tradingplan, self.ppro_out)


	def set_symbol(self,symbol:Symbol,tradingplan):
		self.symbol=symbol
		self.tradingplan = tradingplan
		self.strategy_name = self.symbol.get_name()+" "+self.strategy_name
		self.ppro_out = self.tradingplan.ppro_out
		self.risk = self.tradingplan.get_risk()

	def restart(self):

		self.current_triggers = set()
		for i in self.initial_triggers:
			self.current_triggers.add(i)

	def update(self):

		if len(self.current_triggers)>0:
			check = False
			for i in self.current_triggers:
				if self.symbol!=None:
					check = False
					if i.check_conditions():
						check = True
					if check:
						break
			if check:
				self.current_triggers = i.get_next_triggers() #replace the triggers. 
				#print(self.current_triggers)
				for i in self.current_triggers:
					i.set_symbol(self.symbol,self.tradingplan,self.ppro_out)

				if len(self.current_triggers)==0: #if there is no trigger, call the finish even.t
					self.on_finish()

		else:
			print("Strategy: nothing to trigger.")

	def on_finish(self):
		print(self.strategy_name+" completed")
		self.tradingplan.on_finish(self)	
		self.restart()

	def adjust_target_price(self):
		pass

class BreakUp(Strategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)

		self.add_initial_triggers(buyTrigger)

class BreakDown(Strategy): #the parameters contains? dk. yet .  #Can make single entry, or multiple entry. 
	def __init__(self,timer,repeat,symbol,tradingplan):
		super().__init__("Break up",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(buyTrigger)

class BreakAny(Strategy):
	def __init__(self,timer,repeat,symbol,tradingplan):

		super().__init__("Break Any",symbol,tradingplan)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out
		buyTrigger = Purchase_trigger([[SYMBOL_DATA,ASK,">",SYMBOL_DATA,RESISTENCE]],SUPPORT,self.risk,"break up",timer,repeat,LONG,self.ppro_out)
		sellTrigger = Purchase_trigger([[SYMBOL_DATA,BID,"<",SYMBOL_DATA,SUPPORT]],RESISTENCE,self.risk,"break down",timer,repeat,SHORT,self.ppro_out)

		self.add_initial_triggers(buyTrigger)
		self.add_initial_triggers(sellTrigger)


class ThreePriceTargets(Strategy):

	def __init__(self,symbol,tradingplan):

		super().__init__("Three price targets",symbol,tradingplan)

		manaTrigger = Three_price_trigger("manage",self.ppro_out)

		self.add_initial_triggers(manaTrigger)
		#description,trigger_timer:int,trigger_limit=1
		#conditions,stop,risk,description,trigger_timer,trigger_limit,pos,ppro_out


	def adjust_target_price(self): #call this whenever the break at price changes. 

		
		price = self.tradingplan.data[AVERAGE_PRICE]

		coefficient = 0.05

		good = False

		print(self.tradingplan.data[POSITION])
		if self.tradingplan.data[POSITION]==LONG:
			ohv = self.symbol.data[OHAVG]
			ohs =  self.symbol.data[OHSTD]
			#print(self.data_list[id_],type(ohv),ohs,type(price))
			if ohv!=0:
				#self.tradingplan[id_][0] = price
				self.tradingplan.data[PXT1] = round(price+ohv*0.2*coefficient,2)
				self.tradingplan.data[PXT2] = round(price+ohv*0.5*coefficient,2)
				self.tradingplan.data[PXT3] =	round(price+ohv*0.8*coefficient,2)
				good = True
		elif self.tradingplan.data[POSITION]==SHORT:
			olv = self.symbol.data[OLAVG]
			ols = self.symbol.data[OLSTD]
			if olv!=0:
				#self.price_levels[id_][0] = price
				self.tradingplan.data[PXT1] = round(price-olv*0.2*coefficient,2)
				self.tradingplan.data[PXT2] = round(price-olv*0.5*coefficient,2)
				self.tradingplan.data[PXT3] = round(price-olv*0.8*coefficient,2)
				good = True
				
		#set the price levels. 
		#print(id_,"updating price levels.",price,self.price_levels[id_][1],self.price_levels[id_][2],self.price_levels[id_][3])
		if good:
			self.tradingplan.tkvars[AUTOMANAGE].set(True)
			self.tradingplan.tkvars[PXT1].set(self.tradingplan.data[PXT1])
			self.tradingplan.tkvars[PXT2].set(self.tradingplan.data[PXT2])
			self.tradingplan.tkvars[PXT3].set(self.tradingplan.data[PXT3])
		else:
			self.tradingplan.tkvars[AUTOMANAGE].set(False)


		#print(self.tradingplan.data[PXT1],self.tradingplan.data[PXT2],self.tradingplan.data[PXT3])

# clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

# print(clsmembers)

# for i in clsmembers:
# 	print(i)