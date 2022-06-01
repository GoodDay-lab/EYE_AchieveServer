
import threading
import requests
import logging
import queue
import time


"""
      All parameters in config object are necessary without them you may get an Exception
    logger - logging.Logger object
    server_url - url to your remote server
    online - parameter (if online is False then all func will ignore)
    sid - parameter (it sets when you call login)
"""

class ServerThread(threading.Thread):
    """
      class ServerThread is need to make a requests and return a manage in same time
    One day I found a problem that when you make a request - your app is freezes
    This class have to solve this problem.
    """
    def __init__(self):
        super().__init__()
        self.queue = queue.Queue(10)
        self.interval = (1 / 30)
        self.stop_word = True
    
    def run(self):
        while self.stop_word:
            if not self.queue.empty():
                func, args, kwargs, callback = self.queue.get()
                response = func(*args, **kwargs)
                if callback:
                    callback(response)
            time.sleep(self.interval)
    
    def add_process(self, func, args=None, kwargs=None, callback=None):
        """
        param: func (function) - It's your api function, actually it can be another function
        param: args (tuple) - It's args to your func
        param: kwargs (dict) - It's kwargs to your func
        param: callback (function) - This function will invoke when you get a response
                                    as one param callback takes a response.
        
          I admit advise to use this class and method to call api functions.
        """
        args = args or ()
        kwargs = kwargs or {}
        self.queue.put((func, args, kwargs, callback))
    
    def stop(self):
        """
          To stop server. You can miss some requests. Be carefully
        """
        self.stop_word = False


config = {
    "logger": None,
    "server_url": None,
    "online": 0,
    "sid": None
}


def set_server_url(url):
    global config
    if not url.endswith("/"):
        url += "/"
    config['server_url'] = url


def set_logger(new_logger):
    global config
    config['logger'] = new_logger


def set_conn_state(new_state):
    global config
    config['online'] = new_state
    

def empty_func(*args, **kwargs): return None


def validate(func):
    """
      If you want play offline and do not get connect to remote server
    you should set (config['online'] = False) 
    then all functions that you will run as (login, signup, etc.) will do nothig
    """
    def f(*args, **kwargs):
        if config['online'] and config['server_url'] is not None:
            return func(*args, **kwargs)
        else:
            return empty_func(*args, **kwargs)
    return f
    
    
@validate
def signup(name, email, passw):
    """
    param: name (str)
    param: email (str)
    param: passw (str)
    
      Simple function that sign you up in server
    and create a database row specially for you!
    """
    sign_url = "%ssignup" % config['server_url']
    json = {
        "name": name,
        "email": email,
        "passw": passw
    }
    response = requests.post(sign_url, json=json).json()
    if response['status']:
        config['logger'].info("[Success] %s" % response['msg'])
    else:
        config['logger'].info("[Fail] %s" % response['msg'])
    return response


@validate
def login(email, passw):
    """
    param: email (str)
    param: passw (str)
    
      Simple function that log in you on server
    if success:
        in response['msg'] is sid (session id)
        session id is necessary to nex functions 
    else:
        return a error code
    """
    login_url = "%slogin" % config['server_url']
    json = {
        "email": email,
        "passw": passw
    }
    response = requests.post(login_url, json=json).json()
    if response['status']:
        config['logger'].info("[Success] sid (%s)" % response['msg'])
        config['sid'] = response['msg']
    else:
        config['logger'].info("[Fail] %s" % response['msg'])
    return response


@validate
def update():
    """
    
      Special method to update all achievements with saving current user's achievements
    necessary for remote control when you want to delete one achieve
    """
    update_url = "%supdate" % config['server_url']
    response = requests.post(update_url).json()
    if response['status']:
        config['logger'].info("[Success] %s" % response['msg'])
    else:
        config['logger'].info("[Fail] %s" % response['msg'])
    return response


@validate
def get_achievements():
    """
    
      Special method that returns a achievements of all users
    very neccesary method if you want make a gui table
    """
    achievements_url = "%sachievements" % config['server_url']
    response = requests.get(achievements_url).json()
    return response


@validate
def get_self_achievements():
    """
    
      sid is in config dict and update every time when you call login
    function.
    """
    achievement_url = "%sachievement" % config['server_url']
    
    if config['sid'] is None:
        return
        
    json = {
        'sid': config['sid']
    }
    response = requests.get(achievement_url, json=json).json()
    if response['status']:
        config['logger'].info("[Success] you got self achievements")
    else:
        config['logger'].info("[Fail] %s" % response['msg'])
    return response


@validate
def put_achievement(achieve):
    """
    param: achieve (str) - name of achievement
    
      Set correct achieve name as in 'achievements.json' on server
    after calling this func your state will change on True
    It means you got an achievement
    """
    achievement_url = "%sachievement" % config['server_url']
    if config['sid'] is None:
        return
        
    json = {
        'sid': config['sid'],
        "achieve": achieve
    }
    response = requests.put(achievement_url, json=json).json()
    if response['status']:
        config['logger'].info("[Success] you put self achievement")
    else:
        config['logger'].info("[Fail] %s" % response['msg'])
    return response
