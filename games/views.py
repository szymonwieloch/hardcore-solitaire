# Create your views here.

from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from games.forms import *
from games.utils import stack_repr, Msg
import datetime
import game
import json
import traceback
from game_reader import GameReader
from models import Game

_game_reader = GameReader()

def _new_game(request, random, save):
    play = game.Game()
    if random:
        play.new()
    else:
        play.load(json.loads(_game_reader.random()))
    
    if save:
        gm = Game()
        now = datetime.datetime.now()
        gm.name= 'Unnamed game %s'%now.strftime("%Y-%m-%d %H:%M:%S")
        
        gm.data = json.dumps(play.dump())
        gm.history = '[]'
        gm.created = now
        gm.modified = now
        user = User.objects.get(username=request.user.username)
        gm.user = user
        gm.save()
        return HttpResponseRedirect(reverse('game', args=(gm.id,)))
    else:
        return _draw_board(request, play)
        
@login_required
def load_game(request):
    template = get_template('main.html')
    games = Game.objects.all().order_by('-modified')
    variables = Context({
    'games': games,
    'user': request.user
    })
    output = template.render(variables)
    return HttpResponse(output)
def main_page(request):
    return render_to_response('welcome.html', context_instance=RequestContext(request))
    
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
    
@login_required
def new_random_game(request):
    return _new_game(request, True, True)

@login_required    
def new_winnable_game(request):
    return _new_game(request, False, True)
    
def new_quick_game(request):
    return _new_game(request, False, False)
    

@login_required
def continue_game(request):
    games = Game.objects.all().order_by('-modified')[:1]
    if games:
        return HttpResponseRedirect(reverse('game', args=(games[0].id,)))
    else:
        return new_game(request)

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
                )
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })
    return render_to_response( 'register.html', variables )

def _draw_board(request, play, history = '[]', game_id = None, form=None):
    template = get_template('game.html')
    central = list(play.final_queues)
    central.append(play.single_queue)
    central = [stack_repr(c, False) for c in central] 
    left = play.normal_queues[::2]
    left = [stack_repr(s, False) for s in left]
    right = play.normal_queues[1::2]
    right = [stack_repr(s, True) for s in right]
    variables = RequestContext(request, {
    'left': left,
    'right': right,
    'central': central,
    'game_id': game_id,
    'form': form,
    'history': history
    })
    return HttpResponse(template.render(variables))

@login_required    
def game_page(request, game_id):
    gm = Game.objects.get(id=game_id)
    play=game.Game()
    play.load(json.loads(gm.data))
    history = json.loads(gm.history)
    for frm, to in history:
        play.move(frm, to)
    if play.is_won():
        gm.delete()
        return render_to_response('win.html', context_instance=RequestContext(request))
    form = GameNameForm(initial={'name': gm.name})
    return _draw_board(request, play, gm.history, game_id, form)
        
@login_required    
def apply_obvious(request, game_id):
    gm = Game.objects.get(id=game_id)
    play=game.Game()
    play.load(json.loads(gm.data))
    play.apply_obvious_moves()
    gm.data = json.dumps(play.dump())
    gm.save()
    return HttpResponseRedirect(reverse('game', args=(game_id,)))

@login_required        
def move(request, game_id):
    try:
        if request.method != 'POST':
            return
        gm = Game.objects.get(id=game_id)
        play=game.Game()
        play.load(json.loads(gm.data))  
        output = Msg()
        moves = json.loads(request.POST['moves'])
        print 'moves', moves
        for move in moves:
            frm = move[0]
            to = move[1]
            correct = play.move(frm, to)
            if not correct:
                output.level = Msg.ERROR
                output.status = Msg.FAILURE
                output.msg = "Bad move!"
                return HttpResponse(output.dump())
        gm.history = json.dumps(moves)
        gm.save()
        output.level = Msg.DONE
        if play.is_won():
            gm.delete()
            return HttpResponseRedirect(reverse('win'))
        elif not play.move_possible():
            output.level = Msg.WARN
            output.msg = "There are no legal moves left!"
            
        else:
            output.msg = "Correct move. Game was saved."
        return HttpResponse(output.dump())
        
    except Exception as err:
        print err
        traceback.print_exc()

@login_required        
def delete(request, game_id):
    gm = Game.objects.get(id=game_id)
    gm.delete()
    return HttpResponseRedirect(reverse('load'))
    
@login_required        
def give_up(request, game_id):
    gm = Game.objects.get(id=game_id)
    gm.delete()
    return HttpResponseRedirect(reverse('newgame'))

def rules_page(request):
    return render_to_response( 'rules.html', context_instance=RequestContext(request))
    
def interface_page(request):
    return render_to_response( 'interface.html', context_instance=RequestContext(request))
    
def win(request):
    return render_to_response('win.html', context_instance=RequestContext(request))
    
def about_page(request):
    return render_to_response( 'about.html', context_instance=RequestContext(request))

@login_required    
def save_name(request, game_id):
    if request.method != 'POST':
        return
    gm = Game.objects.get(id=game_id) 
    gm.name = request.POST['name']
    gm.save()
    out = Msg()
    out.msg ='Game was saved as "%s".'%request.POST['name']
    return HttpResponse(out.dump())
         