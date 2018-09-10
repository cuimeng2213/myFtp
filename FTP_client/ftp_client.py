#coding: utf-8

import json
import optparse
import socket
import os, sys
#自定义状态码
STATUS_CODE = {
	250:"Invalid cmd",
	251:"Invalid cmd",
	252:"Invalid auth data",
	253:"Wrong username or password",
	254:"Passed authentications",
	255:"Filename doesn't provided",
	256:"File doesn't exist on server",
	257:"ready to send file",
	258:"md5 verification",
	
	800:"the file exist, but nor enough, is continue?",
	801:"the file exist!",
	802:"ready to receive datas",
	900:" md5 valdate success",
}

class ClientHandler():
	def __init__(self):
		self.op = optparse.OptionParser()
		
		self.op.add_option("-s","--server", dest="server")
		self.op.add_option("-P","--port", dest="port")
		self.op.add_option("-u","--username", dest="username")
		self.op.add_option("-p","--password", dest="password")
		
		self.options, self.args = self.op.parse_args()
		#校验命令参数是否有效
		self.verify_args(self.options, self.args)
		
		self.make_connection()
		self.mainPath = os.path.dirname(os.path.abspath(__file__))
		self.last = 0
	
	def verify_args(self,options,args):
		server = options.server
		port = options.port
		
		if int(port) > 0 and int(port)<65535:
			return True
		else:
			exit("port is error")
			
	def make_connection(self):
		self.sk = socket.socket()
		self.sk.connect((self.options.server,int(self.options.port)))
		
	def interactive(self):
		if self.authenticate():
			print("auth ok begin to interactive......")
			while True:
				cmd_info = input("[%s]" % self.current_dir).strip() #put xx.png images
				cmd_list = cmd_info.split()
				try:
					if hasattr(self,cmd_list[0]):
						func = getattr(self,cmd_list[0])
						func(*cmd_list)
				except Exception as e:
					print("err>>>> ",e)
					continue
				
	def put(self, *cmd_list):
		#put 12.png images
		action,local_path,target_path = cmd_list
		#本地文件路径拼接
		local_path = os.path.join(self.mainPath,local_path)
		file_name = os.path.basename(local_path)
		file_size = os.stat(local_path).st_size
		data = {
			"action":"put",
			"file_name":file_name,
			"file_size":file_size,
			"target_path":target_path,
		}
		self.sk.send(json.dumps(data).encode("utf-8"))
		is_exist = self.sk.recv(1024).decode("utf-8")
		
		has_sent=0
		if is_exist == "800":
			#文件不完整
			choice = input("the file exist, but not enough is continue?[Y/N]").strip()
			if choice.upper() == "Y":
				self.sk.send("Y".encode("utf-8"))
				continue_position=self.sk.recv(1024).decode("utf-8")
				has_sent += int(continue_position)
				
			else:
				self.sk.send("N".encode("utf-8"))
		elif is_exist == "801":
			#文件存在且完整
			print("file exist")
			return
		else:
			print("begin send data")
		f = open(local_path,"rb")
		f.seek(has_sent)
		while has_sent < file_size:
			data = f.read(1024)
			self.sk.send(data)
			has_sent += len(data)
			self.show_progress(has_sent, file_size)
		f.close()
		
		print("put success")
	def show_progress(self,has, total):
		rate = float(has)/float(total)
		rate_num = int(rate*100)
		if self.last != rate_num:
			sys.stdout.write("%s%%%s\r" % (rate_num,"#"*rate_num/2))
		self.last = rate_num
		
		
	#认证
	def authenticate(self):
			if self.options.username is None or self.options.password is None:
				username = input("username: ")
				password=input("password: ")
				print("username=[{username}] password=[{password}]".format(username=username,password=password))
				return self.get_auth_result(username, password)
			else:
				return self.get_auth_result(self.options.username, self.options.password)
	def response(self):
		data = self.sk.recv(1024).decode("utf-8")
		data = json.loads(data)
		return data
	def get_auth_result(self, user, pwd):
		data = {
			"action":"auth",
			"username":user,
			"password":pwd,
		}
		self.sk.send(json.dumps(data).encode("utf-8"))
		res = self.response()
		print("res = ",res.get("status_code"))
		
		if res.get("status_code") == 254:
			self.user =user
			self.current_dir=user
		else:
			print(STATUS_CODE[res["status_code"]])
		
		return True
	def ls(self, *cmd_list):
		data = {
			"action":"ls",
		}
		self.sk.send(json.dumps(data).encode("utf-8"))
		
		data = self.sk.recv(1024).decode("utf-8")
		print(data)
	def cd(self, *cmd_list):
		data = {
			"action":"cd",
			"dirname":cmd_list[1]
		}
		self.sk.send(json.dumps(data).encode("utf-8"))
		data = self.sk.recv(1024).decode("utf-8")
		self.current_dir = os.path.basename(data)
		print("cd: ", os.path.basename(data))
	
	def mkdir(self, *cmd_list):
		data = {
			"action":"mkdir",
			"dirname":cmd_list[1],
		}
		self.sk.send(json.dumps(data).encode("utf-8"))
		data = self.sk.recv(1024).decode("utf-8")
		print(data)
if __name__=="__main__":
	ch = ClientHandler()
	ch.interactive()