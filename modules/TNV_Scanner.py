import tkinter as tk                     
from tkinter import ttk 
import threading
import pandas as pd
import time

#from pannel import *
#from modules.pannel import *

from tkinter import *


def ts_to_min(ts):
	ts = int(ts)
	m = ts//60
	s = ts%60

	return str(m)+":"+str(s)

class TNV_Scanner():

	def __init__(self,root,NT):

		
		self.root = root

		self.NT = NT


		#self.NT_update_time = tk.StringVar(value='Last updated')
		#self.NT_update_time.set('Last updated')

		self.NT_stat = ttk.Label(self.root, text="Last update: ")
		self.NT_stat.place(x=10, y=10, height=25, width=200)

		self.TNV_TAB = ttk.Notebook(self.root)
		self.TNV_TAB.place(x=0,rely=0.05,relheight=1,width=640)

		self.vb_frame = tk.Canvas(self.TNV_TAB)
		self.or_frame = tk.Canvas(self.TNV_TAB)
		self.ob_frame = tk.Canvas(self.TNV_TAB)
		self.pb_frame = tk.Canvas(self.TNV_TAB)


		self.TNV_TAB.add(self.vb_frame, text ='Volatility Break')
		self.TNV_TAB.add(self.or_frame, text ='Open Reversal')
		self.TNV_TAB.add(self.ob_frame, text ='Open Break')
		self.TNV_TAB.add(self.pb_frame, text ='Premarket Pick')

		# self.breakout_frame = ttk.LabelFrame(self.root,text="Volatility Breakout")
		# self.breakout_frame.place(x=0, rely=0.05, relheight=1, relwidth=0.95)

		# self.reversal_frame = ttk.LabelFrame(self.root,text="Reversal")
		# self.reversal_frame.place(x=0, rely=0.36, relheight=0.268, relwidth=0.95)

		# self.momentum_frame = ttk.LabelFrame(self.root,text="Momentum")
		# self.momentum_frame.place(x=0, rely=0.59, relheight=0.268, relwidth=0.95)

		# self.NT_scanner_canvas = tk.Canvas(self.all)
		# self.NT_scanner_canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)#relx=0, rely=0, relheight=1, relwidth=1)
		# self.scroll = tk.Scrollbar(self.all)
		# self.scroll.config(orient=tk.VERTICAL, command=self.NT_scanner_canvas.yview)
		# self.scroll.pack(side=tk.RIGHT,fill="y")
		# self.NT_scanner_canvas.configure(yscrollcommand=self.scroll.set)
		# self.NT_scanner_frame = tk.Frame(self.NT_scanner_canvas)
		# self.NT_scanner_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
		# self.NT_scanner_canvas.create_window(0, 0, window=self.NT_scanner_frame, anchor=tk.NW)

		self.volatility_scanner = Volatility_break(self.vb_frame,NT)
		self.open_reversal = Open_Reversal(self.or_frame,NT)
		self.open_break = Volatility_break(self.ob_frame,NT)
		#self.update_entry()

	def update_entry(self,data):
		timestamp = data[1]
		self.NT_stat["text"] = "Last update: "+timestamp
		for key,item in data[0].items():
			if key == "Volitality_Break":
				self.volatility_scanner.update_entry(item)
			elif key == "Open_Reseral":
				self.open_reversal.update_entry(item)


class Volatility_break():
	def __init__(self,root,NT):

		self.buttons = []
		self.entries = []
		self.l = 1
		self.labels_width = [9,6,5,5,5,5,6,6,6,6,6,6,8,6]
		self.NT = NT
		self.labels = ["Symbol","Vol","Rel.V","SCORE","5M","SC%","SO%","Listed","Since","Last","Ignore","Add"]
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1

	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data


		df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rel vol']
				roc5 = row['5ROCP']
				roc10 = row['10ROCP']
				roc15 = row['15ROCP']
				score = row['score']
				sc = row['SC']
				so = row['SO']

				since = row['since']
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,score,roc5,sc,so,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction:",e)

class Open_Reversal():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,7,5,6,6,6,6,6,6,8,6]
		self.labels = ["Symbol","Vol","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Ignore","Add"]
		self.root = root
		self.recreate_labels(self.root)


		#self.update_entry([pd.read_csv("test2.csv",index_col=0)])

	def recreate_labels(self,frame):

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1


	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data
		#timestamp = data[1]

		#self.NT_stat["text"] = "Last update: "+timestamp

		df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)

				#["Symbol","Vol","Rel.V","Side","Re.SCORE","SC%","Listed","Since","Ignore","Add"]
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rel vol']
				side = row['reversalside']
				rscore = row['reversal_score']
				sc = row['SC']

				since = ts_to_min(row['reversal_timer'])


				############ add since, and been to the thing #############

				if self.NT != None:
					if rank in self.NT.nasdaq_trader_symbols_ranking:
						listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
					else:
						listed = "No"
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,side,rscore,sc,listed,since]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction:",e)

class Open_Break():
	def __init__(self,root,NT):
		self.buttons = []
		self.entries = []
		self.l = 1
		self.NT = NT
		self.labels_width = [9,6,5,7,5,5,6,6,6,6,8,6]
		self.labels = ["Symbol","Vol","Rel.V","Br.SCORE","5M","SO%","SC%","Listed","Since","Last","Ignore","Add"]
		self.root = root
		self.recreate_labels(self.root)

	def recreate_labels(self,frame):

		self.labels_position = {}
		self.labels_position["Rank"]=0
		self.labels_position["Symbol"]=1
		self.labels_position["Market"]=2
		self.labels_position["Price"]=3
		self.labels_position["Since"]=4
		self.labels_position["Been"]=5
		self.labels_position["SC%"]=6
		self.labels_position["SO%"]=7
		self.labels_position["L5R%"]=8
		self.labels_position["Status"]=9
		self.labels_position["Add"]=10

		self.market_sort = [0,1,2]#{'NQ':0,'NY':1,'AM':2}

		self.status_code = {}
		self.status_num = 0

		for i in range(len(self.labels)): #Rows
			self.b = tk.Button(self.root, text=self.labels[i],width=self.labels_width[i])#,command=self.rank
			self.b.configure(activebackground="#f9f9f9")
			self.b.configure(activeforeground="black")
			self.b.configure(background="#d9d9d9")
			self.b.configure(disabledforeground="#a3a3a3")
			self.b.configure(relief="ridge")
			self.b.configure(foreground="#000000")
			self.b.configure(highlightbackground="#d9d9d9")
			self.b.configure(highlightcolor="black")
			self.b.grid(row=self.l, column=i)
			self.buttons.append(self.b)

		self.l+=1
		self.create_entry()

	def create_entry(self):

		for k in range(0,50):

			self.entries.append([])

			for i in range(len(self.labels)): #Rows
				self.b = tk.Label(self.root, text=" ",width=self.labels_width[i])#,command=self.rank
				self.b.grid(row=self.l, column=i)
				self.entries[k].append(self.b)
			self.l+=1



	def update_entry(self,data):

		#at most 8.
		# ["Symbol","Vol","Rel.V","5M","10M","15M","SCORE","SC%","SO%","Listed","Ignore","Add"]

		df = data[0]
		timestamp = data[1]

		self.NT_stat["text"] = "Last update: "+timestamp

		df.to_csv("tttt.csv")
		entry = 0

		try:
			for index, row in df.iterrows():
				#print(row)
				rank = index
				vol = row['Avg VolumeSTR']
				relv = row['rel vol']
				roc5 = row['5ROCP']
				roc10 = row['10ROCP']
				roc15 = row['15ROCP']
				score = row['score']
				sc = row['SC']
				so = row['SO']

				since = row['since']
				last = row['last']

				############ add since, and been to the thing #############
				if rank in self.NT.nasdaq_trader_symbols_ranking:
					listed = str(self.NT.nasdaq_trader_symbols_ranking[rank])
				else:
					listed = "No"
				#print(self.NT.nasdaq_trader_symbols)
				if 1: #score>0:	

					lst = [rank,vol,relv,score,roc5,sc,so,listed,since,last]

					for i in range(len(lst)):
						self.entries[entry][i]["text"] = lst[i]
					entry+=1
					if entry ==50:
						break

			while entry<50:
				#print("ok")
				for i in range(10):
					self.entries[entry][i]["text"] = ""
				entry+=1
		except Exception as e:
			print("TNV scanner construction:",e)

if __name__ == '__main__':

	root = tk.Tk() 
	root.title("GoodTrade v489") 
	root.geometry("640x840")

	TNV_Scanner(root,None)

	root.mainloop()



			
	# 		info = [rank,avgv,relv,roc5,roc10,roc15,score,sc,so]
	# 		self.nasdaq.append([])

# # # # df=df.sort_values(by="rank",ascending=False)

# print(df)
# i=0
# for item,row in df.iterrows():
# 	#print(item,row)
# 	df.loc[item,"rank"] =i
# 	i+=1 
# print(df)
# df.loc[df["rank"]==2,"rank5"]=5


# print(df.loc[df["status"]=='New'])
# print(df)


# df=df.sort_values(by=["rank","status"],ascending=False)

# print(df)

