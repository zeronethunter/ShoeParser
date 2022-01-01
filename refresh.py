import shlex
import os
from subprocess import Popen


def start():
    print(os.getcwd())
    cmd = shlex.split('scrapy runspider basketshop_spider.py -o items.jl')
    p = Popen(cmd, shell=True)
    p.wait()
