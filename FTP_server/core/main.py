#coding: utf-8
#解析命令行的模块
import optparse
import socketserver

from core import server
from conf import settings


class ArgvHandler():
	
	def __init__(self):
		self.op = optparse.OptionParser()
		
		#self.op.add_option("-s","--server", dest="server")
		#self.op.add_option("-P","--port", dest="port")
		options, args = self.op.parse_args()
		
		self.verify_args(options,args)
	def verify_args(self,options,args):
		cmd = args[0]
		#使用反射处理命令行参数
		if hasattr(self,cmd):#查看实例方法所以传入self
			func = getattr(self,cmd)
			func()
	def start(self):
		print("server is working",settings.IP, settings.PORT)
		s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHandler)
		print("ok")
		s.serve_forever()
		
	def help(self):
		pass
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		