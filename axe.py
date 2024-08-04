# app.py
from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_socketio import SocketIO, emit
import json
import random

app = Flask(__name__)
socketio = SocketIO(app)



# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Load players from a file
def load_players():
    try:
        with open('data/players.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
players = load_players()
player_scores = {player: [0] * 10 for player in players}
player_zombies = {player: list(range(1, 12)) for player in players}  # Each player starts with all zombies active

# Save players to a file
def save_players(players):
    with open('data/players.json', 'w') as file:
        json.dump(players, file)


@app.route('/reset_players', methods=['POST'])
def reset_players():
    save_players([])
    return redirect(url_for('setup'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        players = request.form.getlist('players')
        save_players(players)
        return redirect(url_for('index'))
    players = load_players()
    return render_template('setup.html', players=players)

# Route for the scoring page
@app.route('/scoring')
def scoring():
    with open('data/players.json', 'r') as file:
        players = json.load(file)
    scores = {player: [0] * 10 for player in players}
    return render_template('score.html', players=players, scores=scores)

# Route for the zombies game page
@app.route('/zombies')
def zombies():
    # with open('data/players.json', 'r') as file:
    #     players = json.load(file)
    # scores = {player: [0] * 11 for player in players}
    # zombies = []
    # for i in range(11):
    #     # Generate random position for each zombie
    #     top = random.randint(0, 650)  # Changed to fit the height of the image
    #     left = random.randint(-200, 1000)  # Leave some space at the sides
    #     zombies.append({"top": top, "left": left})
    return render_template('zombies.html', zombies=player_zombies, players=players, scores=player_scores)
    # # Create a list of dictionaries to store zombie positions
    # zombies = []
    # for i in range(11):
    #     # Generate random position for each zombie
    #     top = random.randint(0, 750)  # Changed to fit the height of the image
    #     left = random.randint(-200, 1000)  # Leave some space at the sides
    #     zombies.append({"top": top, "left": left})
    # return render_template('zombies.html', zombies=zombies)

@socketio.on("RESET_ZOMBIES")
def reset_zombies():
    global player_zombies
    player_zombies = {player: list(range(1, 12)) for player in players}  # Each player starts with all zombies active


@socketio.on('remove_zombie')
def handle_remove_zombie(data):
    print("REMOVING")
    print(f"Received request to remove zombie {data['zombie_number']} for player {data['player']}")
    player = data['player']
    zombie_number = data['zombie_number']
    if zombie_number in player_zombies[player]:
        player_zombies[player].remove(zombie_number)
        print(f"Zombie {zombie_number} removed for player {player}. Remaining zombies: {player_zombies[player]}")

        emit('remove_zombie', zombie_number, broadcast=True)

@socketio.on('redraw_board')
def handle_remove_zombie(data):
    print("UPDATING BOARD")
    player = data['player']
    emit('update_zombies', {'player': player, 'zombies': player_zombies[player]}, broadcast=True)



# Route for the board page
@app.route('/board')
def board():
    return render_template('board.html')

# Route to save player setup
@app.route('/save_setup', methods=['POST'])
def save_setup():
    players = request.json.get('players', [])
    with open('players.json', 'w') as file:
        json.dump(players, file)
    return jsonify(success=True)

# Socket event to show target for scoring
@socketio.on('show_target')
def handle_show_target():
    emit('display_target', broadcast=True)


@socketio.on('show_zombies')
def handle_show_zombies():
    for player, zombies in player_zombies.items():
        emit('display_zombies', {'player': player, 'zombies': zombies}, broadcast=True)
# # Socket event to show zombies for zombies game
# @socketio.on('show_zombies')
# def handle_show_zombies():
#     emit('display_zombies', 'update_zombies', broadcast=True)



# @socketio.on('remove_zombie')
# def handle_remove_zombie(data):
#     emit('hide_zombie', data)

@socketio.on('remove_all')
def handle_remove_all():
    emit('hide_all', broadcast=True)

# Main entry point
if __name__ == '__main__':
    socketio.run(app, port=5000, host='0.0.0.0', debug=True)
