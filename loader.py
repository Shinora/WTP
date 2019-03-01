from threading import Thread
import time
from yaspin import yaspin

class loader(Thread):
    def __init__(self, message):
        Thread.__init__(self)
        self.message = message
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            with yaspin(text=self.message, side="left", color="blue"):
                time.sleep(0.75)

    def stop(self):
        self.running = False
