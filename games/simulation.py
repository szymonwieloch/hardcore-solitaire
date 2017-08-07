from game import Game, simulate
from datetime import datetime
import cProfile

def multiple():
    start = datetime.now()
    success = 0
    for i in range(0, 100):
        game = Game()
        game.new()
        result = simulate(game)
        print 'result', result, i
        if result: success += 1
    end = datetime.now()
    diff = end - start
    print 'took', diff
    print 'average', diff/100
    print 'successes', success

def single():
    global game
    game = Game()
    data = {'single': [], 'final': [['H0'], ['S0'], ['D0'], ['C0']], 'normal': [['S3', 'H10', 'D6', 'C3', 'D8'], ['S5', 'D11', 'H9', 'H5', 'C1'], ['D10', 'C8', 'D3', 'D2', 'C12'], ['D5', 'H11', 'S11', 'H2', 'D12'], ['S8', 'C11', 'S2', 'H3', 'S12'], ['C4', 'S6', 'C9', 'D9', 'H4'], ['D4', 'S4', 'C6', 'D1', 'H6'], ['C5', 'C10', 'H7', 'H8', 'S7'], ['C7', 'C2', 'S10', 'H12'], ['H1', 'S9', 'S1', 'D7']]}
    game.load(data)
    #game.new()
    #print repr(game.dump())
    result = simulate(game)
    print 'result', result
    
cProfile.run('single()')
#cPrifile.run('multiple()')
