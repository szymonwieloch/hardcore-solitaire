var COLORS = ['H', 'S', 'C', 'D'];


var Card = function(color, val){
	this.color = color;
	this. val = val;
	this.symbol = 'Card' + color + val;
	
	this.dump = String.fromCharCode(COLORS.indexOf(color) * 13 + val);
};

Card.prototype.isParent = function(card){
	if (!card){ return false}
	return card.color == this.color && this.val == card.val + 1;
}

var CARDS = {};

for (idx in COLORS){
	for (var i=0; i<13; ++i){
		var card = new Card(COLORS[idx], i);
		CARDS[card.symbol] = card;
	}
}

var Stack = function(){
	this._cards = [];
}

Stack.prototype.push = function(card){
	if (!card){ throw "Empty card!";}
	this._cards.push(card);
	this.top = card;
}

Stack.prototype.pop = function(card){
	try{
		var card = this._cards.pop();
		this.top = this._cards[this._cards.length - 1];
		return card;
	} catch(err){
		console.error(err);
		throw err;
	}
}

Stack.prototype.popForced = function(card){
	var card = this._cards.pop();
	this.top = this._cards[this._cards.length - 1];
	return card;
}

Stack.prototype.dump = function(){
	var cards = [];
	for (idx in this._cards){
		cards.push(this._cards[idx].dump);
	}
	return cards.join('');
}

var NormalStack = function(num){
	Stack.call(this);
	this.symbol = 'StackNormal' + num;
}

NormalStack.prototype = Object.create(Stack.prototype);

NormalStack.prototype.moveFrom = function(stack){
	if (!this.top){
		var card = stack.pop();
		if (!card){ return false;}
		this.push(card);
		return true;
	}
	if (!stack.top){ return false;}
	if (!this.top.isParent(stack.top)){ return false;}
	var card = stack.pop();
	if (!card) { return false;}
	this.push(card);
	return true;
}

var CentralStack = function(num){
	Stack.call(this);
	this.symbol = 'StackFinal' + num;
}

CentralStack.prototype = Object.create(Stack.prototype);

CentralStack.prototype.moveFrom = function(stack){
	if (stack.top  && stack.top.isParent(this.top)){
		var card = stack.pop();
		if (card){
			this.push(card);
			return true;
		}
	}
	return false
}

CentralStack.prototype.isFull = function(){
	return this._cards.length == 13;
}

CentralStack.prototype.pop = function(card){
}

var HelpingStack = function(){
	Stack.call(this);
	this.symbol = 'StackSingle';
}

HelpingStack.prototype = Object.create(Stack.prototype);

HelpingStack.prototype.moveFrom = function(stack){
	if (this.top){ return false; }
	var card = stack.pop();
	if (card){
		this.push(card);
		return true;
	} else {
		return false;
	}
}

function Game(){
	this._stacks = {};
	this._normalStacks = [];
	for (var i = 0; i< 10; ++i){
		var nstack = new NormalStack(i);
		this._stacks[nstack.symbol] = nstack;
		this._normalStacks.push(nstack);
	}
	
	this._centralStacks = [];
	for (var i = 0; i< 4; ++i){
		var cstack = new CentralStack(i);
		this._stacks[cstack.symbol] = cstack;
		this._centralStacks.push(cstack);
	}
	var hstack = new HelpingStack();
	this._stacks[hstack.symbol] = hstack;
	this._helpingStack = hstack;
}

Game.prototype.move = function(from, to){
	var f = this._stacks[from];
	var t = this._stacks[to];
	if (f && t){
		return t.moveFrom(f);
	}
	return false;
}

Game.prototype.dump = function(){
	var dumps = [];
	for (idx in this._normalStacks){
		dumps.push(this._normalStacks[idx].dump());
	}
	dumps.sort();
	for (idx in this._centralStacks){
		dumps.push(this._centralStacks[idx].dump());
	}
	dumps.push(this._helpingStack.dump());
	return dumps.join(';');
}

Game.prototype.isWon = function(){
	for (idx in this._centralStacks){
		if (!this._centralStacks[idx].isFull()) {return false;}
	}
	return true;
}

Game.prototype.checkWinning = function(){
	
	var analyzed = {};
    this.applyObvious();
	if (this.isWon()) { return true;}
	var that = this;
	var dump = that.dump();
	analyzed[dump] = true;
	function nextMove(){
		for (idx in that._stacks){
			var from = that._stacks[idx];
			for (idy in that._stacks){
				var to = that._stacks[idy];
				if (to.moveFrom(from)){
					//also apply obvious moves to reduce complexity
					//console.info(from.symbol, '->', to.symbol);
					var undo = that.applyObvious();
					undo.reverse();
					undo.push([from, to]);
					var dump = that.dump();
					//already analyzed
					if (!analyzed[dump]){
						analyzed[dump] = true;
						if (that.isWon()) { return true;}
						if (nextMove()) { return true;}	
					}
					//undo moves before leaving function
					for (idx in undo){
						//console.info(undo[idx][0].symbol, '<-', undo[idx][1].symbol);
						undo[idx][0].push(undo[idx][1].popForced());
					}
				}
			}
		}
		return false;
	}
	var result =  nextMove();
	return result;
}

Game.prototype.applyObvious = function(){
        var moves = [];
		var that = this;
        var move = function(){
            for(idx in that._centralStacks){
				var cstack = that._centralStacks[idx];
                for (idy in that._normalStacks){
					var nstack = that._normalStacks[idy];
                    if (cstack.moveFrom(nstack)){
						return [nstack, cstack];
					}
				}
                if (cstack.moveFrom(that._helpingStack)){
                    return [that._helpingStack, cstack];
				}
			}
            return null;
		}
        for (;;){
            mv = move();
            if (mv == null){ return moves;}
            moves.push(mv);
		}
}

Game.prototype.movePossible = function(){
	for (fromIdx in this._stacks){
		var from = this._stacks[fromIdx];
		for(toIdx in this._stacks){
			var to = this._stacks[toIdx];
			if (to.moveFrom(from)){ return true;}
		}
	}
	return false;
}

var startGame = function(){
	var game = new Game();
	for (idx in game._stacks){
		var stack = $('#'+ idx);
		stack.children('.card').each(function(){
			var id = $(this).attr('id');
			game._stacks[idx].push(CARDS[id]);
		})
	}
	return game;
}

