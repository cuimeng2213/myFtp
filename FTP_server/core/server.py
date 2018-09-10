import os
import json
import configparser
import socketserver
from conf import settings

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
class ServerHandler(socketserver.BaseRequestHandler):

	def handle(self):#重写父类handle方法
		print("handler")
		while True:
			#相当于客户端请求的句柄
			data = self.request.recv(1024).strip()
			#转换成json
			if data == b'':
				return
			data = json.loads(data.decode("utf-8"))
			"""
			{"action":"auth",
			 "username":"",
			 "password":""}
			"""
			if data.get("action"):
				if hasattr(self,data.get("action")):
					func = getattr(self,data.get("action"))
					func(**data)
				else:
					print("not found cmd")
			else:
				print("Invalid cmd")
	
	def authenticate(self, user, pwd):
		cfg = configparser.ConfigParser()
		cfg.read(settings.ACCOUNT_PATH)
		if user in cfg.sections():
			#判断密码是否正确
			if cfg[user]["Password"] == pwd:
				#匹配成功
				self.user = user
				self.mainPath = os.path.join(settings.BASE_DIR,"home",self.user)
				print("auth ok")
				return user
		return None
	
	def auth(self, **data):
		print("recv data: ", data)
		username = data.get("username")
		password = data.get("password")
		user = self.authenticate(username, password)
		if user:
			self.send_response(254)
		else:
			self.send_response(253)
			
	def send_response(self,status_code):
		response = {"status_code":status_code,"status_mse":STATUS_CODE.get(status_code)}
		self.request.sendall(json.dumps(response).encode("utf-8"))
		
	def put(self, **data):
		print(data)
		file_name = data.get("file_name")
		file_size = data.get("file_size")
		target_path = data.get("target_path")
		
		abs_path = os.path.join(self.mainPath,target_path,file_name)
		has_recvived = 0
		#上传一个文件会有几种可能
		#文件是否存在
		if os.path.exists(abs_path):
			file_has_size = os.stat(abs_path).st_size
			if file_has_size < file_size:
				#代表断点续传
				self.request.sendall("800".encode("utf-8"))
				choice = self.request.recv(1024).decode("utf-8")
				if choice == "Y":
					has_recvived += file_has_size
					self.request.sendall(str(file_has_size).encode("utf-8"))
					f = open(abs_path,"ab")
				else:
					f = open(abs_path,"wb")
			else:
				#文件完全存在
				self.request.sendall("801".encode("utf-8"))
				return
		else:
			self.request.sendall("802".encode("utf-8"))
			#文件不存在新建该文件
			f = open(abs_path,"wb")
			
		while has_recvived < file_size:
			try:
				data = self.request.recv(1024)
				f.write(data)
				has_recvived+=len(data)
			except Exception as e:
				break
		f.close()
		print("recv over")
	def ls(self, **data):
		file_list = os.listdir(self.mainPath)
		if not len(file_list):
			file_str = "<empty>"
		else:
			file_str = "\n".join(file_list)
		self.request.sendall(file_str.encode("utf-8"))
		
	def cd(self, **data):
		dirname = data.get("dirname")
		if dirname == "..":
			#cd到上一层目录
			self.mainPath = os.path.dirname(self.mainPath)
		else:
			self.mainPath=os.path.join(self.mainPath,dirname)
		self.request.sendall(self.mainPath.encode("utf-8"))
		
	def mkdir(self, **data):
		dirname = data.get("dirname")
		
		path = os.path.join(self.mainPath,dirname)
		if not os.path.exists(path):
			if "/" in dirname:
				os.makedirs(path)
			else:
				os.mkdir(path)
			self.request.sendall("create dirname success".encode("utf-8"))
		else:
			self.request.sendall("dirname exists".encode("utf-8"))
		
		
		
		
		
