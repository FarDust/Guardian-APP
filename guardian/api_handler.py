from abc import ABCMeta
from threading import Thread, Lock
from config import *
from guardian.utils import parse_info
from guardian.db_register import ask_info

class Handler(Thread,metaclass=ABCMeta):

    def __init__(self):
        self.message = bytes()
        self._current_state = int()
        super().__init__()

    def run(self):
        pass

    @property
    def state(self):
        return self._current_state

class Guardian_Handler(Handler):
    lock = Lock()

    def __init__(self,message,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if isinstance(message,bytes):
            self.message = message
        else:
            raise TypeError('bytes required for this handler')
        self.daemon = True
    
    def run(self):
        with self.lock:
            self._current_state = 0 # "Face found: calling API..."
            response = ask_info(self.message)
            if not "error" in response:
                self._current_state = 1 # "Face detected"
                return parse_info(response)
            else:
                self._current_state = -1 #"Error: {}".format(responce)