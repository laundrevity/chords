from music21 import chord, key, stream, note
from midiutil import MIDIFile

from typing import List
import math
import traceback

def major_pentatonic_scale(key: str) -> List[str]:
    major_scale_steps = [2, 2, 1, 2, 2, 2, 1]
    pentatonic_scale_steps = [2, 2, 3, 2, 3]
    print('getting scale_notes')
    scale_notes = [note.Note(key)]

    print('getting current_note')
    current_note = note.Note(key)
    for step in pentatonic_scale_steps:
        current_note = current_note.transpose(step)
        scale_notes.append(current_note)

    print('returning names with octave')
    return [n.nameWithOctave for n in scale_notes]

def generate_chord_progression(key: key.Key, progression: str) -> List[chord.Chord]:
    scale = key.getScale('major')
    I = chord.Chord([scale.pitchFromDegree(1), scale.pitchFromDegree(3), scale.pitchFromDegree(5)])
    IV = chord.Chord([scale.pitchFromDegree(4), scale.pitchFromDegree(6), scale.pitchFromDegree(1).transpose(7)])
    V = chord.Chord([scale.pitchFromDegree(5), scale.pitchFromDegree(7), scale.pitchFromDegree(2).transpose(7)])
    vi = chord.Chord([scale.pitchFromDegree(6), scale.pitchFromDegree(1).transpose(7), scale.pitchFromDegree(3).transpose(7)])
    viio = chord.Chord([scale.pitchFromDegree(7), scale.pitchFromDegree(2).transpose(7), scale.pitchFromDegree(4).transpose(7)])
    iii = chord.Chord([scale.pitchFromDegree(3), scale.pitchFromDegree(5), scale.pitchFromDegree(7)])
    ii = chord.Chord([scale.pitchFromDegree(2), scale.pitchFromDegree(4), scale.pitchFromDegree(6)])

    chord_progression = []
    for s in progression.split('-'):
        match s:
            case "I":
                chord_progression.append(I)
            case "IV":
                chord_progression.append(IV)
            case "V":
                chord_progression.append(V)
            case "vi":
                chord_progression.append(vi)
            case "viio":
                chord_progression.append(viio)
            case "iii":
                chord_progression.append(iii)
            case "ii":
                chord_progression.append(ii)
    return chord_progression

def save_chord_progression_to_midi(
    chord_progression: List[chord.Chord], 
    time_signature: str, 
    melody_style: str, 
    melody_notes_per_chord: int, 
    filename: str) -> float:
    num, denom = map(int, time_signature.split('/'))
    midi = MIDIFile(2)
    tempo_bpm = 120
    midi.addTempo(0, 0, tempo_bpm)
    midi.addTempo(1, 0, tempo_bpm)

    # calculate the power of 2 for the denominator
    denom_power_of_two = int(math.log2(denom))

    # add the time signature event with proper parameters
    midi.addTimeSignature(0, 0, num, denom_power_of_two, 24, 8)
    midi.addTimeSignature(1, 0, num, denom_power_of_two, 24, 8)

    silence_duration = 0.0  # Add 0.5 seconds of silence before the first chord
    chord_duration = num  # Change the chord duration based on the time signature
    # chord_duration = 1


    # melody settings
    # melody_notes_per_chord = 8
    # melody_style = "jumps"

    for i, ch in enumerate(chord_progression):
        for j, _note in enumerate(ch):
            # add 0.05 second delay between start times of each note in a chord
            start_time = silence_duration + i * chord_duration + j * 0.01
            midi.addNote(
                0, 
                0, 
                _note.pitch.midi, 
                start_time,
                chord_duration, 
                100
            )

        # add the melody notes
        melody_notes = []
        print(f"matching {melody_style=}")
        match melody_style:
            case "ascending":
                melody_notes = major_pentatonic_scale(ch.root().name)
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]
            case "descending":
                melody_notes = list(reversed(major_pentatonic_scale(ch.root().name)))
                octaves = list(reversed([ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]))
            case "alternating":
                pentatonic_scale = major_pentatonic_scale(ch.root().name)
                melody_notes = [note for pair in zip(pentatonic_scale, reversed(pentatonic_scale)) for note in pair]
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]
            case "arpeggio":
                pentatonic_scale = major_pentatonic_scale(ch.root().name)
                melody_notes = [pentatonic_scale[t] for t in [0, 2, 4, 5]]
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]
            case "motif":
                motif = [0, 2, 4, 2]
                pentatonic_scale = major_pentatonic_scale(ch.root().name)
                melody_notes = [pentatonic_scale[i] for i in motif]
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]
            case "jumps":
                interval = 2 # a third jump in the pentatonic scale
                pentatonic_scale = major_pentatonic_scale(ch.root().name)
                melody_notes = [pentatonic_scale[(t * interval) % len(pentatonic_scale)] for t in range(melody_notes_per_chord)]
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]
            case "sequence":
                pentatonic_scale = major_pentatonic_scale(ch.root().name)
                motif = [0, 2, 4]  # Define a short motif using scale degrees
                transpositions = [0, 2, -2]  # Define a list of transpositions for the motif
                melody_notes = [pentatonic_scale[(i + t) % len(pentatonic_scale)] for t in transpositions for i in motif]
                octaves = [ch.pitches[0].octave + (k // len(melody_notes)) for k in range(melody_notes_per_chord)]


        print(f"Got melody_notes: {melody_notes}")
        if melody_notes:
            for k in range(melody_notes_per_chord):
                melody_note = note.Note(melody_notes[k % len(melody_notes)])
                # melody_note.octave = ch.pitches[0].octave + (k // len(melody_notes))
                melody_note.octave = octaves[k]
                melody_duration = chord_duration / melody_notes_per_chord
                start_time = silence_duration + i * chord_duration + k * melody_duration
                midi.addNote(1, 0, melody_note.pitch.midi, start_time, melody_duration, 50)

    with open(filename, 'wb') as f:
        try:
            midi.writeFile(f)
        except Exception as e:
            print(f"got error writing midi: {e}")
            print(traceback.format_exc())

    # duration = (chord_duration * len(chord_progression) + silence_duration) * (tempo_bpm / 60) / denom
    total_beats = num * len(chord_progression)
    beat_duration = 60 / tempo_bpm
    duration = (total_beats * beat_duration) + silence_duration
    return duration


if __name__ == '__main__':
    key_c = key.Key('C')
    prog = generate_chord_progression(key_c)
    save_chord_progression_to_midi(prog, "out.midi")
