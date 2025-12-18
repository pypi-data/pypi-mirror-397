import numpy as np
import time
import random
import shelve
import os

recent = []
recent1 = []
cloud = []
a = 1
b = 78
c = 23
users = []
codes = []
points = []

		
fg_colors = {
	"black": "\033[90m",
	"red": "\033[91m",
	"green": "\033[92m",
	"yellow": "\033[93m",
	"blue": "\033[94m",
	"magenta": "\033[95m",
	"cyan": "\033[96m",
	"white": "\033[97m"
}

bg_colors = {
	"black": "\033[100m",
	"red": "\033[101m",
	"green": "\033[102m",
	"yellow": "\033[103m",
	"blue": "\033[104m",
	"magenta": "\033[105m",
	"cyan": "\033[106m",
	"white": "\033[107m"
}



storage_path = os.path.join(os.path.dirname(__file__), "data.db")

def load_data():
	with shelve.open(storage_path) as db:
		users = db.get("users", [])
		points = db.get("points", [])
		codes = db.get("codes", [])
	return users, points, codes


def save_data(users, points, codes):
	with shelve.open(storage_path, "c") as db:
		db["users"] = users
		db["points"] = points
		db["codes"] = codes


users, points, codes = load_data()

def colour(text, fg="white", bold=False, bg=None):
	prefix = ""
	if bold:
		prefix += "\033[1m"
	prefix += fg_colors.get(fg.lower(), "\033[97m")
	if bg:
		prefix += bg_colors.get(bg.lower(), "")
	return f"{prefix}{text}\033[0m"

nums = np.zeros((3,3))
board = np.full((3,3),'#')
board_original = board.copy()
col = np.full((3,3),'orange')
bg = np.full((3,3),'cyan')
output_board = board
num1 = 0
num2 = 0

print(colour('MarStar','green',bold = True,bg = None))
print(colour('----------------------------------------','red',bold = True,bg = None))
time.sleep(3)
print(colour('MarStar,ultimate game platform.','magenta',bold = True,bg = 'cyan'))
print(colour('----------------------------------------','yellow',bold = True,bg = None))
time.sleep(3)
print(colour('Developed by Marcy.','cyan',bold = True,bg = None))
print(colour('----------------------------------------','magenta',bold = True,bg = None))
time.sleep(3)
print(colour('Developer:           Marcy            ','green',bold = True,bg = 'magenta'))
txt = """
marstar.guide() : For check the guide of this game.


Tic-Tac-Toe:

	How to find position:
			  y y y y y
	
	 
			  0    1   2
		x	0['#','#','#']
		x
		x	1['#','#','#']
		x
		x	2['#','#','#']
			
		You can use find the position this way,and the form is (x,y),WARNING:x is the first,then y!The number of x and y is the position above,have fun :)
		
	How to use functions:
		marstar.clear() : For clear all the character on the board.
		marstar.x(x,y) : Use it follow the rule in the <How to find position> part,put your position inside,then 'X' will be on that position on board.
		marstar.o(x,y) : Use it follow the rule in the <How to find position> part,put your position inside,then 'O' will be on that position on board.
		marstar.ai() : DO NOT PUT ANYTHING INSIDE,this function is the AI player function,it will fill the board using 'A' and race with you.
		How easy this game is!
	Game rules:
		1.If your piece fill a line(every line is okay,but first it have to be a line),then you win!
			['#','#','X']
			['#','X','#']
			['X','#','#']
		See?In this case playerX won!
		2.Your first placed piece will disapear everytime when there are three same piece on board!So that allowed you to play forever!
		Okay,that is all,HAVE FUN :)

Murphy:

	All the available operators:
		*  /  ^  !  %  -  +  #
		[mutiply,devided,power,factorial,mod,subtract,plus,int]
	Game rule:
		When game just started two player will all get a same original number and a same target number,you have to connect original number to the special game number you get everytime(random),to get the target number.Just this simple.

User functions:
	marstar.register() : For register a new account,permanently.
	marstar.login() : For login and check your userprofile.
	marstar.profile() : Check user info.
	marstar.reset_password() : To reset your password.




Enjoy the fun of ultimate game platform MarStar!
	
	Developer: Marcy"""
time.sleep(2)
print(colour('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------','magenta',bold = True,bg = None))
print(colour(txt,'cyan',bold = True,bg = None))	
time.sleep(1)
print(colour('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------','green',bold = True,bg = None))
print(colour('Email address:        huazii@gmail.com  ,any advice for this game can be send to this address! -Marcy','magenta',bold = True,bg = 'cyan'))
time.sleep(1)

print(colour('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------','yellow',bold = True,bg = None))
print(colour('Enjoy the fun of this ultimate game platform!','magenta',bold = True,bg = 'cyan'))
time.sleep(1)
print(colour('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------','cyan',bold = True,bg = None))
print(colour('Developer:           Marcy            ','green',bold = True,bg = 'magenta'))
time.sleep(2)
print(colour("if you want to play Tic-Tac-Toe game,why don't you start by type 'marstar.ai()'?Or if you want to play Murphy game,why don't you start by type 'marstar.murphy'?",'white',bold = True,bg = None))

def col():
	global board
	cols = ['magenta','green','yellow','cyan','white','red','blue']
	pos = random.randrange(7)
	outputs = colour(board,cols[pos],bold = True,bg = None)
	return outputs

def register():
	global codes
	global users
	global points
	account_name = input('Username:    ')
	while account_name in users and account_name != 'q':
		account_name = input('Sorry,this name been taken,please change one or quit(q):    ')
		if account_name == 'q':
			print('QUITTED')
			break
	if account_name != 'q':
		users.append(account_name)
		password = input('Password(password length >= 6 characters):    ')
		while len(list(password)) < 6:
			password = input('Password length is too short,please choose another one(password length >= 6 characters):    ')
		codes.append(password)
		marstar_codes = users.index(account_name)
		points.append(0)
		save_data(users,points,codes)
		print('Successfully created account!')
		time.sleep(1)
		print(f"Your userprofile:    username={account_name}    password={password}    MarStar code={marstar_codes}     game points=0    remember these,{account_name}.")


def login():
	global codes
	global users
	global points
	username = input('Username:    ')
	if username not in users:
		print(f"Username {username} doesn't exist,please use type marstar.register() to register an account or check your spelling.")
	else:
		passcode = input('Enter your password:    ')
		if codes[users.index(username)] == passcode:
			print(f"Welcome back,{username}")
		else:
			request = input('Wrong password,forgot your password?(y/n):    ')
			if request == 'y':
				mscode = input('Enter your MarStar code:    ')
				if mscode == users.index(username):
					new_password = input('Enter your new password:    ')
					users.pop(users.index(username))
					codes.pop(users.index(username))
					points.append(points[users.index(username)])
					points.pop(users.index(username))
					users.append(username)
					codes.append(new_password)
					ms_codes = users.index(username)
					save_date(users,points,codes)
					print(f"New password={new_password}    username={username}    MarStar code={ms_codes}    game points={points[-1]}    remember these please,{username}.")
			else:
				print('Wrong password,use marstar.register() to register an account first.')
				return


def profile():
	global codes
	global users
	global points
	user_name = input('Enter your username here to view your userprofile:    ')
	if username in users:
		password = input('Enter your password here to view your userprofile:    ')
		if codes[users.index(username)] == password:
			print(f"Username={users[users.index(username)]}    MarStar code={users.index(username)}    game points={points[users.index(username)]}    remember these please,{users[users.index(username)]}.")
		else:
			print('Wrong password,use marstar.reset_password() function to reset your password.')
	else:
		user_name = input('User does not exist,perhaps you wants to use marstar.register() function to register an account?y/n:    ')
		if user_name == 'y':
			print('Use marstar.register() to register an new account.')
		else:
			user_name = input('Enter your username here to view your userprofile:    ')
			t = 0
			while username not in users and t < 3:
				t += 1
				user_name = input('Enter yoru username here to view your userprofile:    ')
				if t == 3 and username not in users:
					print('Wrong username,please use marstar.register() to register an account.')
					break
				if username in users:
					password = input('Enter your password here to login to your account.')
					if codes[users.index(username)] == password:
						print(f"Username={users[users.index(username)]}    MarStar code={users.index(username)}    game points={points[users.index(username)]}   remember these please,{users[users.index(username)]}.")
						break
					else:
						print('Wrong password,use marstar.reset_password() function to reset your password.')
						break			
						

def reset_password():
	global codes
	global users
	global points
	username = input('Enter your username here to reset your password:    ')
	if username in users:
		marstarcode = input('Enter your MarStar code here to verify that is you:    ')
		if users[marstarcode] == username:
			new_password = input('Enter your new password:    ')
			codes[marstarcode] = new_password
			print(f"Username={username}    password={new_password}    game ponts={points[users.index(username)]}    MarStar code={users.index(username)}    remember these please,{username}.")
		else:
			print('Wrong MarStar code,use marstar.register() to register a new account.')
	else:
		print('Username does not exist,please use marstar.register() to register a new account')
		
		
def reset_data():
	global codes
	global users
	global points
	print('Warning:this will clean up all the data in this game,this function can only use by the main developers of MarStar,if you are not the main developer of MarStar,DO NOT CONTINUE,EVEN TRYING.')
	time.sleep(1)
	hslv = input('Enter developers code:    ')
	if hslv == codes[0]:
		codes = []
		users = []
		points = []
		save_data(users,points,codes)
		print('Data reset.')
	else:
		print('You are not allowed to entry this function and to reset the data_base for MarStar.')
		

def view_data():
	global codes
	global users
	global points
	print('Warning:this function is for view the whole MarStar database,this function can only use by the main developers of MarStar,if you are not the main developer of MarStar,DO NOT CONTINUE,EVEN TRYING.')
	time.sleep(1)
	hslv = input('Enter developers code:    ')
	if hslv == codes[0]:
		print(f"Users={users}")
		time.sleep(1)
		print(f"User's passwords={codes}")
		time.sleep(1)
		print(f"user's points={points}")
		total_view = []
		pos = -1
		for i in range(len(users)):
			pos += 1
			total_view.append(users[pos] + ' : ' + codes[pos] + ' : ' + str(points[pos]) + ' : ' + str(pos) + ' ( ' + str(pos + 1) + ' ) ')
		time.sleep(2)
		print(f"Full database of MarStar(username,user password,game points,MarStar code,user position):        {total_view}")
	else:
		print('Your are not allowed to entry the database.')

		  
def guide():
	print(colour(txt,'cyan',bold = True,bg = None))
	
def is_line():
	if board[0][0] == board[1][0] == board[2][0] != '#':
		if board[0][0] == 'X':
			return a
		elif board[0][0] == 'O':
			return b
		else:
			return c
	elif board[0][1] == board[1][1] == board[2][1] != '#':
		if board[0][1] == 'X':
			return a
		elif board[0][1] == 'O':
			return b
		else:
			return c
	elif board[0][2] == board[1][2] == board[2][2] != '#':
		if board[0][2] == 'X':
			return a
		elif board[0][2] == 'O':
			return b
		else:
			return c
	elif board[0][0] == board[0][1] == board[0][2] != '#':
		if board[0][0] == 'X':
			return a
		elif board[0][0] == 'O':
			return b
		else:
			return c
	elif board[1][0] == board[1][1] == board[1][2] != '#':
		if board[1][0] == 'X':
			return a
		elif board[1][0] == 'O':
			return b
		else:
			return c
	elif board[2][0] == board[2][1] == board[2][2] != '#':
		if board[2][0] == 'X':
			return a
		elif board[2][0] == 'O':
			return b
		else:
			return c
	elif board[0][0] == board[1][1] == board[2][2] != '#':
		if board[0][0] == 'X':
			return a
		elif board[0][0] == 'O':
			return b
		else:
			return c
	elif board[2][0] == board[1][1] == board[0][2] != '#':
		if board[2][0] == 'X':
			return a
		elif board[2][0] == 'O':
			return b
		else:
			return c
	else:
		return a + b


def x(x, y):
	global codes
	global users
	global points
	global cloud
	global board_original
	global output_board
	global recent
	global recent1
	global char_colour
	global num1
	global num2
	global nums
	global board
	board_original = board.copy()
	output_board = board.copy()

	recent.append((x,y))
	if len(recent) > 3:
		old = recent.pop(0)
		board[old] = '#'

	
	if board[x][y] == '#':
		board[x][y] = 'X'
		nums[x][y] = 1
		board_original = board.copy()
		print(col())
	elif board[x][y] == 'A':
		print(col())
		print(f"Sorry,board({x},{y}) is taken by playerAI")
	elif board[x][y] == 'O':
		print(col())
		print(f"Sorry,board({x},{y}) is taken by playerO")
	else:
		print(col())
		print(f"Sorry,board({x},{y}) is taken by playerAI")
	result = is_line()
	if result == a:
		print(colour('@PlayerX won!','magenta',bold = True,bg = 'green'))
		add_points = input('@PlayerX,please enter your username here to add 2 points on you account:    ')
		if add_points not in users:
			print('User does not exist,please check your spelling or use marstar.register to register a new account.')
		else:
			password_request = input(f"{add_points},enter your password here to verify that's you:    ")
			if codes[users.index(add_points)] == password_request:
					points[users.index(add_points)] += 2
					save_date(users,points,codes)
					print(f"Two points added to account {add_points}.Now you have {points[users.index(add_points)]} points on your account.")
			else:
				forgot_password = input(f"Wrong password,do you forgot your password?(y/n):    ")
				if forgot_password == 'y':
					marcode = input('Enter your MarStar code here:    ')
					if users[marcode] != add_points:
						print('MarStar code is wrong,use marstar.register() to register a new account.')
					else:
						new_password = input('Enter your new password:    ')
						codes[marcode] = new_password
						print(f"Username={add_points}    password={new_password}    MarStar code={users.index(add_points)}    remember these please,{add_points}.")
						points[users.index(add_points)] += 2
						save_date(users,points,codes)
						print(f"Two points added to account {add_points}.Now you have {points[users.index(add_points)]} points on your account.")
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent = []
		recent1 = []
		cloud = []
	elif result == b:
		print(colour('@PlayerO won!','yellow',bold = True,bg = 'blue'))
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent = []
		recent1 = []
		cloud = []
	elif not any('#' in row for row in board):
		print('DRAW,game over :<')
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent = []
		recent1 = []
		cloud = []


def o(x, y):
	global codes
	global users
	global points
	global cloud
	global board_original
	global recent
	global recent1
	global num1
	global num2
	global nums
	global board
	global char_colour
	baord_orignal = board.copy()
	recent1.append((x,y))

	if len(recent1) > 3:
		old=recent1.pop(0)
		board[old]='#'

	if board[x][y] == '#':
		board[x][y] = 'O'
		nums[x][y] = 127
		board_original = board.copy()
		print(col())
	elif board[x][y] == 'X':
		print(col())
		print(f"Sorry,board({x},{y}) is taken by playerX")
	elif board[x][y] == 'A':
		print(col())
		print(f"Sorry,board({x},{y}) is taken by playerAI")
	else:
		print(col())
		print(f"Sorry,board({x},{y}) is taken by yourself") 
	result = is_line()
	if result == a:
		print(colour('@PlayerX won!','magenta',bold = True,bg = 'green'))
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent1 = []
		recent = []
		cloud = []
	elif result == b:
		print(colour('@PlayerO won!','yellow',bold = True,bg = 'blue'))
		add_points = input('@PlayerO,please enter your username here to add 2 points on you account:    ')
		if add_points not in users:
			print('User does not exist,please check your spelling or use marstar.register to register a new account.')
		else:
			password_request = input(f"{add_points},enter your password here to verify that's you:    ")
			if codes[users.index(add_points)] == password_request:
				points[users.index(add_points)] += 2
				save_date(users,points,codes)
				print(f"Two points added to account {add_points}.Now you have {codes[users.index(add_points)]} points on your account.")
				
			else:
				forgot_password = input(f"Wrong password,do you forgot your password?(y/n):    ")
				if forgot_password == 'y':
					marcode = input('Enter your MarStar code here:    ')
					if users[marcode] != add_points:
						print('MarStar code is wrong,use marstar.register() to register a new account.')
					else:
						new_password = input('Enter your new password:    ')
						codes[marcode] = new_password
						print(f"Username={add_points}    password={new_password}    MarStar code={users.index(add_points)}    remember these please,{add_points}.")
						points[users.index(add_points)] += 2
						save_date(users,points,codes)
						print(f"Two points added to account {add_points}.Now you have {points[users.index(add_points)]} points on your account.")
						
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent1 = []
		recent = []
		cloud = []
		
	elif not any('#' in row for row in board):
		print('DRAW,game over :<')
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		recent1 = []
		recent = []
		cloud = []


def clear():
	global recent
	global cloud
	global recent1
	global board
	global nums
	recent = []
	cloud = []
	recent1 = []
	board = np.full((3,3),'#')
	nums = np.zeros((3,3))
	print(colour('Board reset.Data reset.','magenta',bold = True,bg = 'cyan'))

def ai():
	global recent
	global char_colour
	global cloud
	global board_original
	global board,nums
	rows, cols = board.shape
	found = False
	if 'X' not in board and 'A' not in board and 'O' not in board:
		board[1][1] = 'A'
		cloud.append((1,1))
		print(col())
		found = True
	else:
		for i in range(rows):
			countX = 0
			countO = 0
			empty_j = None
			for j in range(cols):
				if board[i][j] == 'X':
					countX += 1
				elif board[i][j] == 'O':
					countO += 1
				elif board[i][j] == '#':
					empty_j = j
	
			if empty_j is not None:
				if countX == 2 or countO == 2:
					pos = (i, empty_j)
					board[pos] = 'A'
					cloud.append(pos)
					if len(cloud) > 3:
						old = cloud.pop(0)
						board[old] = '#'
					print(col())
					found = True
		if not found:
			for j in range(cols):
				countX = 0
				countO = 0
				empty_i = None
				for i in range(rows):
					if board[i][j] == 'X':
						countX += 1
					elif board[i][j] == 'O':
						countO += 1
					elif board[i][j] == '#':
						empty_i = i
	
				if empty_i is not None:
					if countX == 2 or countO == 2:
						pos = (empty_i, j)
						board[pos] = 'A'
						cloud.append(pos)
						if len(cloud) > 3:
							old = cloud.pop(0)
							board[old] = '#'
						print(col())
						found = True
		if not found:
			countX = 0
			countO = 0
			empty_k = None
			for k in range(3):
				if board[k][k] == 'X':
					countX += 1
				elif board[k][k] == 'O':
					countO += 1
				else:
					empty_k = k
			if empty_k is not None and (countX == 2 or countO == 2):
				pos = (empty_k, empty_k)
				board[pos] = 'A'
				cloud.append(pos)
				if len(cloud) > 3:
					old = cloud.pop(0)
					board[old] = '#'
				print(col())
				found = True
		if not found:
			countX = 0
			countO = 0
			empty_k = None
			for k in range(3):
				i = k
				j = 2 - k
				if board[i][j] == 'X':
					countX += 1
				elif board[i][j] == 'O':
					countO += 1
				else:
					empty_k = (i,j)
			if empty_k is not None and (countX == 2 or countO == 2):
				pos = empty_k
				board[pos] = 'A'
				cloud.append(pos)
				if len(cloud) > 3:
					old = cloud.pop(0)
					board[old] = '#'
				print(col())
				found = True
		if not found:
			for i in range(rows):
				countA = 0
				empty_j = None
				for j in range(cols):
					if board[i][j] == 'A':
						countA += 1
					elif board[i][j] == '#':
						empty_j = j
				if empty_j is not None and countA == 2:
					pos = (i, empty_j)
					board[pos] = 'A'
					cloud.append(pos)
					if len(cloud) > 3:
						old = cloud.pop(0)
						board[old] = '#'
					print(col())
					found = True
		if not found:
			for j in range(cols):
				countA = 0
				empty_i = None
				for i in range(rows):
					if board[i][j] == 'A':
						countA += 1
					elif board[i][j] == '#':
						empty_i = i
				if empty_i is not None and countA == 2:
					pos = (empty_i, j)
					board[pos] = 'A'
					cloud.append(pos)
					if len(cloud) > 3:
						old = cloud.pop(0)
						board[old] = '#'
					print(col())
					found = True
		if not found:
			countA = 0
			empty_k = None
			for k in range(3):
				if board[k][k] == 'A':
					countA += 1
				elif board[k][k] == '#':
					empty_k = k
			if empty_k is not None and countA == 2:
				pos = (empty_k, empty_k)
				board[pos] = 'A'
				cloud.append(pos)
				if len(cloud) > 3:
					old = cloud.pop(0)
					board[old] = '#'
				print(col())
				found = True
		if not found:
			countA = 0
			empty_k = None
			for k in range(3):
				i = k
				j = 2 - k
				if board[i][j] == 'A':
					countA += 1
				elif board[i][j] == '#':
					empty_k = (i,j)
			if empty_k is not None and countA == 2:
				pos = empty_k
				board[pos] = 'A'
				cloud.append(pos)
				if len(cloud) > 3:
					old = cloud.pop(0)
					board[old] = '#'
				print(col())
				found = True
		if not found:
			positions = list(zip(*np.where(board == '#')))
			if positions:
				pos = random.choice(positions)
				board[pos] = 'A'
				cloud.append(pos)
				if len(cloud) > 3:
					old = cloud.pop(0)
					board[old] = '#'
				print(col())
				found = True
	result = is_line()
	if result == c:
		print(colour('@PlayerAI won!','blue',bold = True,bg = 'yellow'))
		print(colour('From @PlayerAI:"HOORAY!I won!I like playing with you!Hope next time we can play together again =) =) :)!"','magenta',bold = True,bg = 'cyan'))
		board = np.full((3,3),'#')
		nums = np.zeros((3,3))
		cloud = []
		recent = []
		recent1 = []
		
	else:
		string = ['Your turn :)','Your turn =)','I am done,your turn :>','Your turn!','I think i am going to win =)!Your turn!','YOUR TURN :)','Your turn :) :)']
		rand_num = random.randrange(len(string))
		colours = ['green','magenta','yellow','red','blue','cyan','white']
		c_pos = random.randrange(7)					
		print(colour(string[rand_num],colours[c_pos],bold = True,bg = None))			


def murphy():
	global users
	global points
	global codes
	print(colour('Welcome to the best number game ever,Murphy!Developed by MarStar.','green',bold = True,bg = None))
	time.sleep(1)
	game_over = False
	def fact(num):
		num = abs(num)
		if num != 0:
			base = num
			while base != 0:
				base -= 1
				num *= base
				if base == 0:
					return num
					break
		else:
			return 0
	print(colour('Game Started!','green',bold = True,bg = None))
	time.sleep(1)
	rand_num_list = random.sample(range(10000),2)
	original_num = rand_num_list[0]
	on = original_num
	tar = rand_num_list[1]
	print(f'Orignal number=({original_num})    target number=({tar}).')
	t = 0
	while game_over == False and t < 50:
		t += 1
		random_num = random.randrange(10000)
		rn = random.randrange(10000)
		print(f"Player A's game number:    {random_num}    player B's game number:    {rn}    good luck,both of you.")
		
		if t == 50:
			winner = max([abs(random_num - tar),abs(rn - tar)])
			if [abs(random_num - tar),abs(rn - tar)].index(winner) == 0:
				print('Game over,player A won!')
			else:
				print('Game over,player B won!')
		a = input(f'Player A,enter the operator you want to use to connect original number you get when game started {original_num},and game number {random_num} to get target number {tar},DO NOT USE WORD,USE MATHS OPERATOR(*,^,/,+,-,!,%,||,int(#):    ')
		if a == '*':
			original_num *= random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '^':
			original_num = original_num ** random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '/':
			original_num /= random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '+':
			original_num += random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '-':
			original_num -= random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '!':
			if original_num < 30:
				original_num = fact(original_num)
				print(f"Player A,your original number is now     {original_num}    .")
			else:
				print(f"Player A,you cannot use the factorial operator here,because the number will be to huge.")
		elif a == '%':
			original_num %= random_num
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '||':
			original_num = abs(original_num)
			print(f"Player A,your original number is now     {original_num}    .")
		elif a == '#':
			original_num = int(original_num)
			print(f"Player A,your original number is now     {original_num}    .")
		else:
			print('Wrong operator,do not use word,check the available operator list above.')
		if original_num == tar:
			game_over = True
			print('Player A won!Game over.')
			add_points = input('@Player A,please enter your username here to add 3 points on you account:    ')
			if add_points not in users:
				print('User does not exist,please check your spelling or use marstar.register to register a new account.')
			else:
				password_request = input(f"{add_points},enter your password here to verify that's you:    ")
				if codes[users.index(add_points)] == password_request:
					points[users.index(add_points)] += 3
					save_date(users,points,codes)
					print(f"Two points added to account {add_points}.Now you have {codes[users.index(add_points)]} points on your account.")
					
				else:
					forgot_password = input(f"Wrong password,do you forgot your password?(y/n):    ")
					if forgot_password == 'y':
						marcode = input('Enter your MarStar code here:    ')
						if users[marcode] != add_points:
							print('MarStar code is wrong,use marstar.register() to register a new account.')
						else:
							new_password = input('Enter your new password:    ')
							codes[marcode] = new_password
							print(f"Username={add_points}    password={new_password}    MarStar code={users.index(add_points)}    remember these please,{add_points}.")
							points[users.index(add_points)] += 3
							save_date(users,points,codes)
							print(f"Three points added to account {add_points}.Now you have {points[users.index(add_points)]} points on your account.")
			break
			
		time.sleep(1)
		b = input(f'Player B,enter the operator you want to use to connect original number you get when game started {on},and game number {rn} to get target number {tar},DO NOT USE WORD,USE MATHS OPERATOR(*,^,/,+,-,!,%,||,int(#):    ')
		if b == '*':
			on *= rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '^':
			on = on ** rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '/':
			on /= rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '+':
			on += rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '-':
			on -= rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '!':
			if on < 30:
				on = fact(on)
				print(f"Player B,your original number is now     {on}    .")
			else:
				print(f"Player B,you cannot use the factorial operator here,because the number will be to huge.")
		elif b == '%':
			on %= rn
			print(f"Player B,your original number is now     {on}    .")
		elif b == '||':
			on = abs(on)
			print(f"Player B,your original number is now     {on}    .")
		elif b == '#':
			on = int(on)
			print(f"Player B,your original number is now     {on}    .")
		else:
			print('Wrong operator,do not use word,check the available operator list above.')
		if on == tar:
			game_over = True
			print('Player B won!Game over.')
			add_points = input('@Player B,please enter your username here to add 3 points on you account:    ')
			if add_points not in users:
				print('User does not exist,please check your spelling or use marstar.register to register a new account.')
			else:
				password_request = input(f"{add_points},enter your password here to verify that's you:    ")
				if codes[users.index(add_points)] == password_request:
					points[users.index(add_points)] += 3
					save_date(users,points,codes)
					print(f"Two points added to account {add_points}.Now you have {codes[users.index(add_points)]} points on your account.")
					
				else:
					forgot_password = input(f"Wrong password,do you forgot your password?(y/n):    ")
					if forgot_password == 'y':
						marcode = input('Enter your MarStar code here:    ')
						if users[marcode] != add_points:
							print('MarStar code is wrong,use marstar.register() to register a new account.')
						else:
							new_password = input('Enter your new password:    ')
							codes[marcode] = new_password
							print(f"Username={add_points}    password={new_password}    MarStar code={users.index(add_points)}    remember these please,{add_points}.")
							points[users.index(add_points)] += 3
							save_date(users,points,codes)
							print(f"Three points added to account {add_points}.Now you have {points[users.index(add_points)]} points on your account.")
			break