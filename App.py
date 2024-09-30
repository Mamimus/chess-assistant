from flask import Flask, render_template, request
import chess
import random
import requests
import numpy as np
app = Flask(__name__)

current_game = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/move", methods=['POST'])
def get_bot_move():
    fen = request.json['fen']
    board = chess.Board(fen)

    url = "https://explorer.lichess.ovh/lichess"

    # Define the query parameters as a dictionary
    params = {
        "variant": "standard",
        "fen": fen
    }

    # Send the GET request with parameters and headers
    response = requests.get(url, params=params)
    data = response.json()
    moves = data['moves']

    cumsum_moves = np.zeros(len(moves))
    cumsum_moves[0] = moves[0]['white']+moves[0]['black']+moves[0]['draws']
    for i in range(1,len(moves)):
        cumsum_moves[i] = moves[i]['white']+moves[i]['black']+moves[i]['draws']+cumsum_moves[i-1]

    if cumsum_moves[-1] <=10: ## if the dataset is too small it will just move randomly for now
        move = random.choice(list(board.legal_moves))
    else:
        r = random.uniform(0,cumsum_moves[-1])
        for i in range(len(moves)):
            if r<=cumsum_moves[i]:
                uci=moves[i]['uci']
                move = chess.Move.from_uci(uci)
                break


    #Make this True when you want to default to Stockfish
    make_best_move = False

    return {'move':board.san(move), 'best_move':make_best_move}

if __name__ == '__main__':
    app.run(debug=True)

