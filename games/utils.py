from django.core.urlresolvers import reverse
import json

def card_to_image2(card):
    card_name = 'cards/%03d%s.gif'%(card.value, card.color.lower())
    name = reverse('media', args=(card_name,))
    return name

VAL2SYMB = {
    0: 'a',
    9: 't',
    10: 'j',
    11: 'q',
    12: 'k'
}
def card_to_image(card):
    symb = VAL2SYMB.get(card.value, card.value+1)
    card_name = 'cards/%s%s.gif'%(card.color.lower(), symb)
    name = reverse('media', args=(card_name,))
    return name
    
def card_repr(card, position):
    return {
        'url': card_to_image(card),
        'movable' : False,
        'position': position,
        'symbol': card.symbol
    }
    
def stack_repr(stack, rev):
    cards = [card_repr(card, num) for num, card in enumerate(stack)]
    if stack.can_pop and cards:
        last = len(cards)-1
        cards[last]['movable'] = True
    ret = {
        'cards' : cards,
        'symbol': stack.symbol,
        'reversed': rev,
    }
    return ret
        
    
class Msg():
    #levels
    INFO = 'info'
    DONE = 'done'
    WARN = 'warning'
    ERROR = 'error'
    #statuses
    SUCCESS = 'success'
    FAILURE = 'failure'
    WIN = 'win'
    
    _IMAGES = {
        INFO: 'images/info.png', 
        DONE: 'images/success.png',
        WARN: 'images/warning.png',
        ERROR: 'images/error.png'
    }
        
    def __init__(self):
        self.status = self.SUCCESS
        self.msg = ''
        self.level = self.INFO
        
    def dump(self):
        msg = '<img src="%s" alt="%s" /> %s'%(reverse('media', args=(self._IMAGES[self.level],)), self.level, self.msg)
        out = {
            'status': self.status,
            'level': self.level,
            'msg': msg
        }
        return json.dumps(out)