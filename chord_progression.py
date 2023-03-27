from music21 import chord, key, stream
from midiutil import MIDIFile

from typing import List


def generate_chord_progression(key: key.Key) -> List[chord.Chord]:
    scale = key.getScale('major')
    I = chord.Chord([scale.pitchFromDegree(1), scale.pitchFromDegree(3), scale.pitchFromDegree(5)])
    IV = chord.Chord([scale.pitchFromDegree(4), scale.pitchFromDegree(6), scale.pitchFromDegree(1).transpose(7)])
    V = chord.Chord([scale.pitchFromDegree(5), scale.pitchFromDegree(7), scale.pitchFromDegree(2).transpose(7)])

    return [I, IV, V, IV]


def save_chord_progression_to_midi(chord_progression: List[chord.Chord], filename: str):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)

    silence_duration = 0.5  # Add 0.5 seconds of silence before the first chord

    for i, ch in enumerate(chord_progression):
        for j, note in enumerate(ch):
            # add 0.05 second delay between start times of each note in a chord
            midi.addNote(0, 0, note.pitch.midi, silence_duration + i * 2 + j * 0.05, 2, 100)
    
    with open(filename, 'wb') as f:
        midi.writeFile(f)


if __name__ == '__main__':
    key_c = key.Key('C')
    prog = generate_chord_progression(key_c)
    save_chord_progression_to_midi(prog, "out.midi")
