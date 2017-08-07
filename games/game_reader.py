from game import Game, simulate
from os import path
import os
import json
import random

random.seed()

_fname = path.join(path.dirname(__file__), 'games.dat')

class GameReader:
	GAME_SIZE = 389
	file = None
	
	def _open(self):
		if self.file is None:
			
			self.file = open(_fname, 'r')
			self.file.seek(0, os.SEEK_END)
			self.games = size = self.file.tell()/self.GAME_SIZE
	
	def random(self):
		self._open()
		number = random.randint(0, self.games-1)
		self.file.seek(self.GAME_SIZE*number)
		return self.file.read(self.GAME_SIZE)
		
		