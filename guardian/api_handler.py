from abc import ABCMeta
from threading import Thread, Lock
from config import *
from guardian.utils import parse_info
from guardian.db_register import ask_info

class Handler(Thread,metaclass=ABCMeta):

    def __init__(self):
        self.message = bytes()
        self._current_state = type('state',tuple() , {'value': int(), 'data': str()})
        super().__init__()

    def run(self):
        pass

    @property
    def state_object(self):
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
            self._current_state.value = 0 # "Face found"
            response = ask_info(self.message)
            if not "error" in response:
                self._current_state.value = 1 # "Face detected"
                self._current_state.data = parse_info(response)
            else:
                self._current_state.value = -1 # Error
                self._current_state.data = "Error: {}".format(response)