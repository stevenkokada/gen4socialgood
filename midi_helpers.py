#!/usr/bin/env python

import pretty_midi
import numpy as np


def midi_file_to_piano_roll(filename, fs):

    midi_pretty_format = pretty_midi.PrettyMIDI(filename)
    print(type(midi_pretty_format.instruments))
    print(len(midi_pretty_format.instruments))
    if len(midi_pretty_format.instruments)==0:
        return
    piano_midi = midi_pretty_format.instruments[0] # Get the piano channels
    piano_roll = piano_midi.get_piano_roll(fs=fs)
    
    return piano_roll



def piano_roll_to_pretty_midi(piano_roll, fs, program=0):
    '''Convert a Piano Roll array into a PrettyMidi object
     with a single instrument.
    Parameters
    ----------
    piano_roll : np.ndarray, shape=(128,frames), dtype=int
        Piano roll of one instrument
    fs : int
        Sampling frequency of the columns, i.e. each column is spaced apart
        by ``1./fs`` seconds.
    program : int
        The program number of the instrument.
    Returns
    -------
    midi_object : pretty_midi.PrettyMIDI
        A pretty_midi.PrettyMIDI class instance describing
        the piano roll.
    '''
    notes, frames = piano_roll.shape
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    # pad 1 column of zeros so we can acknowledge inital and ending events
    piano_roll = np.pad(piano_roll, [(0, 0), (1, 1)], 'constant')

    # use changes in velocities to find note on / note off events
    velocity_changes = np.nonzero(np.diff(piano_roll).T)

    # keep track on velocities and note on times
    prev_velocities = np.zeros(notes, dtype=int)
    note_on_time = np.zeros(notes)

    for time, note in zip(*velocity_changes):
        # use time + 1 because of padding above
        velocity = piano_roll[note, time + 1]
        time = time / fs
        if velocity > 0:
            if prev_velocities[note] == 0:
                note_on_time[note] = time
                prev_velocities[note] = velocity
        else:
            pm_note = pretty_midi.Note(
                velocity=prev_velocities[note],
                pitch=note,
                start=note_on_time[note],
                end=time)
            instrument.notes.append(pm_note)
            prev_velocities[note] = 0
    pm.instruments.append(instrument)
    return pm


def pretty_midi_to_midi_file(pretty_midi):
    decoded_midi = piano_roll_to_pretty_midi(piano_roll, fs=FS, program=0)
    decoded_midi.write("decoded_"+FILE)






