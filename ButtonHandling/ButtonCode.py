import RPi.GPIO as GPIO
import atexit
import threading
import time
atexit.register(GPIO.cleanup)
GPIO.setmode(GPIO.BCM)

def init_pin(gpio_nr, callback):
	GPIO.setup(gpio_nr, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read(pin):
	return not bool(GPIO.input(pin))


class ButtonHandler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.pins = [12, 17, 5, 23, 24]
		self.callback = None
	
		for pin in self.pins:
			init_pin(pin, self._callback)

		self.setDaemon(True)
		self.start()

	def run(self):
		presstime = time.time()
		while True:
			for i, pin in enumerate(self.pins):
				if read(pin):
					presstime = time.time()
					self._callback(i)
					time.sleep(0.4)
					while read(pin):
						self._callback(i)
						time.sleep(0.1)

	def bind(self, callback):
		self.callback = callback


	def _callback(self, button):
		# print("button: {} pressed".format(button))
		if self.callback is not None:
			self.callback(button)


pins = [12, 17, 5, 23, 24]
if __name__ == "__main__":
	B = ButtonHandler()

	time.sleep(100)
	print("bye")
