# -*- coding: utf-8 -*-

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import click
from pychanlun import server as apiserver
from pychanlun.monitor import BeichiMonitor

@click.group()
def run():
    pass

@run.command()
@click.argument("command", default="run")
def server(**kwargs):
    """运行服务端"""
    command = kwargs.get('command')
    if command == "run":
        apiserver.run(**kwargs)

@run.command()
@click.argument("name", default="beichi")
def monitor(**kwargs):
    """运行监控"""
    name = kwargs.get("name")
    if name == "beichi":
        BeichiMonitor.run(**kwargs)

if __name__ == '__main__':
    run()
