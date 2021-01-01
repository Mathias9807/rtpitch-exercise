#!/usr/bin/env python3

import rtmidi
import time
import queue
import sys
from threading import Timer
import random
random.seed()

# Open MIDI input device if exists
midiin = rtmidi.MidiIn()
available = midiin.get_ports()
if not available:
	print("No available ports")
	exit()
midiin.open_port(0)

# Open virtual midi out
midiout = rtmidi.MidiOut()
midiout.open_virtual_port("rtpitch")

def generateNote():
	while True:
		newNote = random.randint(60, 60 + 12)
		if newNote != generateNote.lastNote:
			generateNote.lastNote = newNote
			return newNote
generateNote.lastNote = 0

def wait(delay=999):
	if delay > 0.5:
		delay = 0.5
	time.sleep(delay)

def playNote(note):
	midiout.send_message([144, note, 80])
	t = Timer(0.5, lambda: midiout.send_message([128, note, 0]))
	t.start()

def noteToText(note):
	midiNotes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
	return midiNotes[note % 12] + chr(ord('₀') + int(note / 12) - 1)

# Queue for notes to be handled in the main loop
notes = queue.Queue()

# Setup MIDI note input handler
class MidiInputHandler(object):
	def __init__(self, port):
		self.port = port

	def __call__(self, event, data=None):
		message, deltatime = event
		if message[0] == 144:
			notes.put(message[1])
		midiout.send_message(message)
midiin.set_callback(MidiInputHandler(0))

print("Entering main loop. Press Control-C to exit.")
try:
	while True:
		# Create a new randomized note
		currentNote = generateNote()

		# Play the new note
		playNote(currentNote)

		while True:
			startTime = time.time()
			# Wait until a note has been played
			note = notes.get()

			if note == currentNote:
				sys.stdout.write('\033[2K\033[1G'+noteToText(currentNote)+'\n')
				wait(time.time() - startTime)
				break
			else:
				nNotes = notes.qsize()
				wait(time.time() - startTime)

				# If they're mashing new notes, wait until they stop
				while nNotes != notes.qsize():
					nNotes = notes.qsize()
					wait()

				playNote(currentNote)
except KeyboardInterrupt:
	pass
finally:
	midiin.close_port()
	midiout.close_port()
	del midiin
	del midiout

# vim: ts=4 sts=4
