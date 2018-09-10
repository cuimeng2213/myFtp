import socketserver
class Mysocket(socketserver.BaseRequestHandler):
	def handler(self):
		pass
s = socketserver.ThreadingTCPServer