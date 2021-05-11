def hexcolor_green_to_red(level):

	if level>0:
		code = int(510*(level))
		#print(code,"_")
		if code >255:
			first_part = code-255
			return "#FF"+hex_to_string(255-first_part)+"00"
		else:
			return "#FF"+"FF"+hex_to_string(255-code)

	else:
		code = int(255*(abs(level)))
		first_part = 255-code

		return "#"+hex_to_string(first_part)+"FF"+hex_to_string(first_part)

def timestamp_seconds(s):

	p = s.split(":")
	try:
		x = int(p[0])*3600+int(p[1])*60+int(p[2])
		return x
	except Exception as e:
		print("Timestamp conversion error:",e)
		return 0

def find_between(data, first, last):
	try:
		start = data.index(first) + len(first)
		end = data.index(last, start)
		return data[start:end]
	except ValueError:
		return data

def hex_to_string(int):
	a = hex(int)[-2:]
	a = a.replace("x","0")

	return a

#1-5 is good 
def hexcolor_red(level):
	code = int(510*(level))
	print(code,"_")
	if code >255:
		first_part = code-255
		return "#FF"+hex_to_string(255-first_part)+"00"
	else:
		return "#FF"+"FF"+hex_to_string(255-code)

#COLOR CODING TEST
if __name__ == '__main__':

	import tkinter as tk
	root = tk.Tk() 

	for i in range(0,13):

		tk.Label(text="",background=hexcolor_red(i/10),width=10).grid(column=i,row=1)

	root.mainloop()