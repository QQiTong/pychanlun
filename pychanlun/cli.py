# -*- coding: utf-8 -*-

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import click
import pychanlun.server as apiserver


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


if __name__ == '__main__':
    run()
