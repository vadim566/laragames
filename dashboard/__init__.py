from flask import render_template
from flask_login import current_user

from db.db import User
from functions.functions import analayzeGame


def games_dashboard():
    user = User.query.filter_by(id=current_user.id).first()

    games = []
    games.append(user.game4Rel)
    games.append(user.game5Rel)
    games.append(user.game6Rel)
    games.append(user.game7Rel)
    games.append(user.game8Rel)
    games.append(user.game9Rel)
    games.append(user.game10Rel)
    games.append(user.game11Rel)
    games.append(user.game12Rel)
    total_games=0
    total_wins=0
    game_sets = []

    for i in range(len(games)):
        game_sets.append([0])
        game_sets[i] = analayzeGame(games[i], game_sets[i])
        game_sets[i].append(str(i))
        total_games=total_games+game_sets[i][2][1]#add the wins  per day
        total_wins=total_wins+game_sets[i][3][1]

    levels=[0,10,20,50,100,200,400,800,1000,1500,2000]
    total_exprience=(total_games-total_wins)*0.3+total_wins
    exprience_next_level=0
    level=int(total_exprience)
    for i in range(len(levels)):
        if level < levels[i] :
            level=i
            exprience_next_level=levels[i]-total_exprience
            break;

    print(total_wins)
    title='Account'
    return title,game_sets, total_wins ,total_games,level,exprience_next_level


def account_dashboard():
    title, game_sets, total_wins, total_games, level, exprience_next_level=games_dashboard()

    return render_template('account.html', title='Account', games=game_sets, wins=total_wins ,gametotal=total_games,p_level=level,exp_level=exprience_next_level)
