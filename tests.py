from time import sleep
from api import *
import logging


def callback(response):
    print(response)
    
    
server = ServerThread()
server.start()

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
set_logger(logger)
set_conn_state(True)
set_server_url("http://127.0.0.1:8000")

server.add_process(update)
server.add_process(signup, args=("Gorge Bruno", "pavelvasilev2304@gmail.com", "4A6MyUbk"), callback=callback)
server.add_process(login, args=("pavelvasilev2304@gmail.com", "4A6MyUbk"), callback=callback)
server.add_process(get_self_achievements, callback=callback)
server.add_process(put_achievement, args=("found spining aniphire",), callback=callback)

while True:
    sleep(1)
