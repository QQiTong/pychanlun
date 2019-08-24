import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
bind = "0.0.0.0:5000"

accesslog = "./log/access.log"
errorlog = "./log/error.log"

loglever = "info"

debug = True