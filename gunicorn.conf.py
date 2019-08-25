import multiprocessing
import os

for k,v in os.environ.items():
    if k.startswith("GUNICORN_"):
        key = k.split('_', 1)[1].lower()
        locals()[key] = v

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
bind = "0.0.0.0:5000"

loglevel = "info"

debug = True