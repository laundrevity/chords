from flask import Flask, request, jsonify, render_template
from music21 import key
import chord_progression

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_chord_progression():
    try:
        data = request.json
        key_input = data['key']
        progression = data['progression']
        time_signature = data['time_signature']
        melody_style = data['melody_style']
        melody_notes_per_chord = int(data['melody_notes_per_chord'])
        
        key_obj = key.Key(key_input)
        progression = chord_progression.generate_chord_progression(key_obj, progression)
        duration = chord_progression.save_chord_progression_to_midi(progression, time_signature, melody_style, melody_notes_per_chord, "out.midi")
        print('saved chord progression')

        with open("out.midi", "rb") as f:
            midi_data = f.read()

        return jsonify({
            "success": True, "midi_data": midi_data.hex(), "duration": duration})

    except Exception as e:
        print(f"got error: {e} when handling {request=}")
        return jsonify({"success": False})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
