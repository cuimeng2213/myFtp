#coding: utf-8
import os, sys
#将父级目录添加到sys.path中，以便可以导入core模块
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PATH)
from core import main


if __name__ == "__main__":
	main.ArgvHandler()