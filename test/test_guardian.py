import unittest
import time
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from guardian import Camera
from guardian.api_handler import Guardian_Handler

class GuardianTest(unittest.TestCase):
    def test_clasifier(self):
        self.assertNotEqual(Camera.faceCascade, None)

class GuardianHandlerTest(unittest.TestCase):
    
    def test_handler_bytes(self):
        with self.assertRaises(TypeError):
            Guardian_Handler(str())
    
    def test_handler_errorState(self):
        firt_handler = Guardian_Handler(bytes())
        firt_handler.start()
        firt_handler.join()
        self.assertEqual(firt_handler.state,-1)

    

if __name__ == "__main__":
    test = GuardianTest()