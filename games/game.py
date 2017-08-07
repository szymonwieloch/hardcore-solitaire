import random
import json
import heapq
import copy

class Card(object):
    COLORS = ('H', 'S', 'D', 'C')
    def __init__(self, color=None, value=None, dump=None):
        if dump:
            self.load(dump)
        else:
            self.color = color
            self.value = value
        self.short_dump = '%02d'% (self.COLORS.index(self.color)* 13 + self.value)
        
        self.symbol = 'Card%s%s'%(self.color,self.value)
        
    def dump(self):
        return '%s%s'%(self.color, self.value)
        
    def load(self, val):
        self.color = val[:1]
        self.value = int(val[1:])
        
    def is_parent(self, card):
        return self.color == card.color and self.value == card.value + 1
        
    def is_child(self, card):
        return self.color == card.color and self.value + 1 == card.value 
    
class Stack(object):
    def __init__(self, num, dump=None):
        self._num = num
        if dump:
            self.load(dump)
        else:
            self._stack = []
        
    @property
    def top(self):
        size = len(self._stack)
        if  size == 0: return None
        return self._stack[size-1]
        
    def pop(self):
        return self._stack.pop()
        
    def add(self, card):
        self._stack.append(card)
        
    def dump(self):
        cards = [card.dump() for card in self._stack]
        return cards
        
    def short_dump(self):
        return ''.join([c.short_dump for c in self._stack])
        
    def load(self, val):
        self._stack = [Card(dump=card) for card in val]
        
    def copy(self):
        cp = self.__class__(self._num)
        cp._stack = list(self._stack)
        return cp
        
    def can_move_from(self, stack):
        if not stack.can_pop: return False
        top = stack.top;
        if top is None: return False
        return self.can_push(top)
    
    def move_from(self, stack):
        if self.can_move_from(stack):
            self._stack.append(stack._stack.pop())
            return True
        else: return False   

    def __iter__(self):
        return iter(self._stack)
        
    def __len__(self):
        return len(self._stack)

        
class SingleStack(Stack):
    @property
    def symbol(self):
        return "StackSingle"
    
    @property
    def can_pop(self):
        return True
        
    def can_push(self, card):
        return self.top is None

class NormalStack(Stack):
    @property
    def symbol(self):
        return "StackNormal%s"%self._num
        
    @property
    def can_pop(self):
        return True     

    def can_push(self, card):
        return self.top is None or self.top.is_parent(card)
    
class FinalStack(Stack):
    @property
    def symbol(self):
        return "StackFinal%s"%self._num
        
    @property
    def can_pop(self):
        return False
        
    def can_push(self, card):
        return  self.top.is_child(card)
        

class Game(object):
    def __init__(self):
        pass
        
    def new(self):
        self.single_queue = SingleStack(0)
        
        self.final_queues = []
        for num, c in enumerate(Card.COLORS):
            q = FinalStack(num)
            q.add(Card(c, 0))
            self.final_queues.append(q)
        
        cards = [Card(color, value) for color in Card.COLORS for value in range(1,13)]
        random.shuffle(cards)
        self.normal_queues = [ ]
        for i in range(0, 10):
            s = NormalStack(i)
            self.normal_queues.append(s)
        
        for index, card in enumerate(cards):
            queue_idx = index %10
            self.normal_queues[queue_idx].add(card)
            
        self._set_by_symbol()
     
    def _set_by_symbol(self):
        self._by_symbol = {}
        self._by_symbol[self.single_queue.symbol] = self.single_queue
        for s in self.final_queues:
            self._by_symbol[s.symbol] = s
        for s in self.normal_queues:
            self._by_symbol[s.symbol] = s      
            
    def dump(self):
        single = self.single_queue.dump()
        final = [q.dump() for q in self.final_queues]
        normal = [q.dump() for q in self.normal_queues]
        
        return {'single' : single,
                'normal' : normal,
                'final': final
               }
    def short_dump(self):
        stacks = [s.short_dump() for s in self.normal_queues]
        stacks.sort() # be deterministic
        stacks.append(self.single_queue.short_dump())
        
        count = len(self.single_queue)
        for s in self.normal_queues: count += len(s)
        
        
        
        return ('%02d,'%count) + ",".join(stacks)
                
    def load(self, dump):
        self.single_queue = SingleStack(0, dump=dump['single'])
        self.final_queues = [FinalStack(num, dump=d) for num, d in enumerate(dump['final'])]
        self.normal_queues = [NormalStack(num, dump=d) for num, d in enumerate(dump['normal'])]
        self._set_by_symbol()
        
    def move(self, frm, to):
        stack_from = self._by_symbol[frm]
        stack_to = self._by_symbol[to]
        return stack_to.move_from(stack_from)
        
    def forced_move(self, frm, to):
        stack_from = self._by_symbol[frm]
        stack_to = self._by_symbol[to]
        stack_to.add(stack_from.pop())
        
    def is_won(self):
        sum = len(self.single_queue)
        for s in self.normal_queues:
            sum += len(s)
        return sum == 0
        
    def copy(self):
        #return copy.deepcopy(self)
        
        cp = Game()
        cp.single_queue = self.single_queue.copy()
        cp.final_queues = [f.copy() for f in self.final_queues]
        cp.normal_queues = [n.copy() for n in self.normal_queues]
        cp._set_by_symbol()
        return cp
        
        
    def move_possible(self):
        for s_from in self._by_symbol.itervalues():
            for s_to in self._by_symbol.itervalues():
                if s_to.can_move_from(s_from): return True
        return False
        
    def all_moves(self):
        original = self.short_dump()
        for symbol_frm, frm in self._by_symbol.iteritems():
            for symbol_to, to in self._by_symbol.iteritems():
                if to.move_from(frm):
                    
                    moves=[(symbol_frm, symbol_to)]
                    moves.extend(self.apply_obvious_moves())
                    yield self.short_dump(), self.copy
                    for move in reversed(moves):
                        self.forced_move(move[1], move[0])
                    assert original == self.short_dump()
        
    def apply_obvious_moves(self):
        moves = []
        def move():
            for f in self.final_queues:
                for n in self.normal_queues:
                    if f.move_from(n): return (n.symbol, f.symbol)
                if self.single_queue.top and f.move_from(self.single_queue):
                    return (self.single_queue.symbol, f.symbol)
            return None
        while True:
            mv = move()
            if mv is None: return moves
            moves.append(mv)

def simulate(game):
    cp = copy.deepcopy(game)
    cp.apply_obvious_moves()
    analyzed = set()
    sd = game.short_dump()
    new = {sd: cp}
    heap = []
    heapq.heappush(heap, sd)
    code = None
    while new:
        #print len(new), len(analyzed)
        try:
            code = heapq.heappop(heap)
        except IndexError:
            return False
        game = new.pop(code)
        analyzed.add(code)
        for move, cp in game.all_moves():
            if move not in analyzed and move not in new:
                new_game = cp()
                if new_game.is_won(): return True
                new[move] = new_game
                heapq.heappush(heap, move)
                
    return False
    
    
        