from game import Game, simulate
from os import path
import json

fname = path.join(path.dirname(__file__), 'games.dat')
with open(fname, 'a') as file:
	found = 0
	while True:
		game = Game()
		game.new()
		result = simulate(game)
		if result:
			found += 1
			s = json.dumps(game.dump())
			file.write(s)
			print "found", found , 'games, current length =', len(s)
		else:
			print 'cannot win the game'
