from flask import Flask, request, jsonify, render_template
from music21 import key
import chord_progression

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_chord_progression():
    key_str = request.json.get('key', 'C')
    key_obj = key.Key(key_str)
    progression = chord_progression.generate_chord_progression(key_obj)
    chord_progression.save_chord_progression_to_midi(progression, "out.midi")

    with open("out.midi", "rb") as f:
        midi_data = f.read()

    return jsonify({"midi_data": midi_data.hex()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
