$( init );

var STACK_PADDING = 5;
var CARD_VISIBLE = 15;
var CARD_WIDTH = 73;
 
function init() {
	
	resetDraggables();
  
  
  
  $('.stack').droppable({
      accept: '.card',
      hoverClass: 'hoveredstack',
      drop: handleCardDrop
    });
 }; 
 
function handleCardDrop (event, ui){
	var from = ui.draggable.parent().attr('id');
	var to = $(this).attr('id');
	if (from == to){
		ui.draggable.animate(ui.draggable.data('orginalPosition'));
		return;
	}
	var game = startGame();
	if (!game.move(from, to)){
		msgbox.error("Invalid move.");
		sound.play(sound.ERROR);
		ui.draggable.animate(ui.draggable.data('orginalPosition'));
		return;
	}
	moveCard(from, to);
	game_history.push([from, to]);
	msgbox.success("Correct move.");
	sound.play(sound.MOVE);
	if (game.isWon()){
		onGameWon();
	} else if (!game.movePossible()){
		msgbox.warning('There are no possible moves');
		sound.play(sound.WARNING);
	} else {
		msgbox.success('Correct move');
		sound.play(sound.MOVE);
	}
};
 
function resetDraggables(){
	$('.card').each(function(index){$(this).draggable('destroy')});
	$('.normalstack').each(function(index){
		$(this).find('.card').last().draggable( {
			revert: 'invalid',
			stack: '.card',
			containment: '#board',
			cursor: 'move'
		});
	
	} );
	
	
	$('#StackSingle').find('.card').last().draggable( {
			revert: 'invalid',
			stack: '.card',
			'zindex': 1,
			containment: '#board',
			cursor: 'move'
		});
		
	$('.leftstack').each(function(){
		$(this).children('.card').each(function(index){
			var position = {
				top: STACK_PADDING+'px', 
				left: (STACK_PADDING + index*CARD_VISIBLE)+'px'
			};
			$(this).css(position);
			$(this).data('orginalPosition', position);
			$(this).css('z-index', index);
		});
	});
	
	$('.rightstack').each(function(){
		var size = parseInt($(this).css('width'));
		$(this).children('.card').each(function(index){
			var position = {
				top: STACK_PADDING+'px', 
				left: (size -(STACK_PADDING + CARD_WIDTH + index*CARD_VISIBLE))+'px'
			};
			$(this).css(position);
			$(this).css('z-index', index);
			$(this).data('orginalPosition', position);
		});
	});
	
	$('.centralstack').each(function(){
		$(this).children('.card').each(function(index){
		
			var position = {
				top: STACK_PADDING+'px', 
				left: STACK_PADDING+'px'
			};
			$(this).css(position);
			$(this).data('orginalPosition', position);
			$(this).css('z-index', index);
		});
	});
};

//SOUND
 var sound = {
	MOVE : 'movesound',
	ERROR: 'errorsound',
	WARNING: 'warningsound',
	SHUFFLE: 'shufflesound',
	
	play: function(sound){
		var elem = $('#' + sound)[0];
		elem.load();
		elem.play();
	}
};
 
//MSG BOX
 var msgbox = {
	info: function(text){
		$('#msgboxtext').html(text);
		$('#msgbox img').css({'display': 'none'});
		$('#infoicon').css({'display': 'block'});	
		$('#msgbox').css({'background-color': '#000', 'color': '#FFF'});
		$('#msgbox').animate({'background-color': '#FFF', 'color': '#000'});
	},
	warning: function(text){
		$('#msgboxtext').html(text);
		$('#msgbox img').css({'display': 'none'});
		$('#warningicon').css({'display': 'block'});	
		$('#msgbox').css({'background-color': '#ff8c00', 'color': '#FFF'});
		$('#msgbox').animate({'background-color': '#FFF', 'color': '#000'});
	}, 
	error: function(text){
		$('#msgboxtext').html(text);
		$('#msgbox img').css({'display': 'none'});
		$('#erroricon').css({'display': 'block'});			
		$('#msgbox').css({'background-color': '#F00', 'color': '#FFF'});
		$('#msgbox').animate({'background-color': '#FFF', 'color': '#F00'});
	},
	success: function(text){
		$('#msgboxtext').html(text);
		$('#msgbox img').css({'display': 'none'});
		$('#successicon').css({'display': 'block'});	
		$('#msgbox').css({'background-color': '#000', 'color': '#FFF'});
		$('#msgbox').animate({'background-color': '#FFF', 'color': '#000'});
	}
}
 
function saveName(){
	var data = {};
	data.name = $('#id_name').val();
	data.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').attr('value');
	$.post('./savename/', data, function(result){
		var response = JSON.parse(result);
		msgbox.info(response.msg);
	});
	return false;
}

function checkWinning(){
	var game = startGame();
	try{
		var result = game.checkWinning();
		if (result){
			alert('It is possible to win the game!');
		} else {
			alert('It is NOT possible to win the game!');
		}
	} catch(err){
		alert('It is probably possible to win the game, but the number of combinations was to big to simulate the whole game!');
	}
}

function moveCard(from, to){
	console.info('moveCard ', from, ' ', to);
	var fromStack = $('#' + from);
	var toStack = $('#' + to);
	var card = fromStack.children('.card').last();
	card.appendTo(toStack);
	resetDraggables();
};

function undo(){
	var move = game_history.pop();
	if (move){
		moveCard(move[1], move[0]);
		sound.play(sound.MOVE);
	}
};

function undo5(){
	var before = game_history.length
	for (idx = 0; idx<5; ++idx){
		var move = game_history.pop();
	if (!move){break;}
	moveCard(move[1], move[0]);
	}
	if (before !== game_history.length){
		sound.play(sound.MOVE);
	}
};

function applyObvious(){
	var game = startGame();
	var moves = game.applyObvious();
	for (idx in moves){
		var from = moves[idx][0].symbol;
		var to = moves[idx][1].symbol;
		moveCard(from, to);
		game_history.push([from, to]);
	}
	if (moves.length == 0){ 
		msgbox.info('There are no obvious moves');
		return;
	}
	
	if (game.isWon()){
		onGameWon();
	} else if (!game.movePossible()){
		msgbox.warning('There are no possible moves');
		sound.play(sound.WARNING);
	} else {
		msgbox.success('Obvious moves applied');
		sound.play(sound.SHUFFLE);
	}
}



function History(history){
	this._history = history;
	this._changed = false;
	this.length = history.length;
}

function setSaveIcon(enabled){
	if (enabled){
		$('#savedisabledicon').css('display', 'none');
		$('#saveicon').css('display', 'block');	
	} else {
		$('#saveicon').css('display', 'none');
		$('#savedisabledicon').css('display', 'block');
	}
}

History.prototype = new Object();

History.prototype.pop = function(){
	var ret = this._history.pop();
	this._changed = false;
	return ret;
}

History.prototype._onChanged = function(){
	this._changed = true;
	this.length = this._history.length;
	setSaveIcon(true);
}

History.prototype.push = function(move){
	this._history.push(move);
	this._onChanged();
}

History.prototype.toArray = function(){
	return this._history.slice();
}

History.prototype.saveGame = function(){
	if (!this._changed){return;}
	this._changed = false;
	setSaveIcon(false);
	
	msgbox.info('Saving game.');
	var url = document.URL + 'move/';
	var csrfToken = $('input[name="csrfmiddlewaretoken"]').attr('value');
	var moves = JSON.stringify(this._history);
	var that = this;
	var data = {moves: moves, 'csrfmiddlewaretoken':csrfToken }
	$.post(url, data, function(){
		msgbox.info('Game saved.');
	}).fail(function(){
		msgbox.error('Problem saving game. Please check Internet conneciton!');
		that._onChanged();
	});
}

function saveGame(){
	game_history.saveGame();
}

function onGameWon(){
	msgbox.success('You have won the game!');
    if(WIN_URL){
        window.open(WIN_URL,"_self")
    } else{
        var url = document.URL + 'move/';
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').attr('value');
        var moves = JSON.stringify(history._history);
        var data = {moves: moves, 'csrfmiddlewaretoken':csrfToken }
        postToUrl(url, data);
    }
}

function postToUrl(path, params) {
    var form = document.createElement("form");
    form.setAttribute("method", 'post');
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }
    document.body.appendChild(form);
    form.submit();
	//document.body.removeChild(form);
}
