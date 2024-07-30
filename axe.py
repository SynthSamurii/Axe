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

# Save players to a file
def save_players(players):
    with open('data/players.json', 'w') as file:
        json.dump(players, file)

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
    # Create a list of dictionaries to store zombie positions
    zombies = []
    for i in range(11):
        # Generate random position for each zombie
        top = random.randint(0, 750)  # Changed to fit the height of the image
        left = random.randint(-200, 1000)  # Leave some space at the sides
        zombies.append({"top": top, "left": left})
    return render_template('zombies.html', zombies=zombies)

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

# Socket event to show zombies for zombies game
@socketio.on('show_zombies')
def handle_show_zombies():
    emit('display_zombies', broadcast=True)



@socketio.on('remove_zombie')
def handle_remove_zombie(data):
    emit('hide_zombie', data)


# Main entry point
if __name__ == '__main__':
    socketio.run(app, debug=True)
