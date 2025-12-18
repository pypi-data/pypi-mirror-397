__version__ = '1.0.2'

# $BEGIN_PYSTAVE_LICENSE$
# 
# This file is part of the pystave project, a Python package that
# helps with sight-reading practice in music.
# 
# Copyright (c) 2009- Jeremy Hill
# 
# pystave is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_PYSTAVE_LICENSE$

"""
TODO: module doc
"""

# Dependencies:
# 
# pygame is used to open the window, load and render the images, and capture keyboard
# events.
# 
# In addition, the `-m` or `--midichannel` option requires the `pygame.midi` submodule
# which is based on pyPortMidi (seemingly temporarily, according to the comments in the
# implementation - but it looks like this has been the case for a long time). pygame
# appears to bundle the necessary binaries of pyPortMidi and the underlying PortMidi
# library.
# 
# My earlier (and still fallback) midi support implementation used `import pypm` directly
# instead, for which the dependency was much harder to install - the import only succeeds
# if the pyPortMidi package has been installed explicitly and the PortMidi shared library
# (`pm_dll.dll` on Windows) is available. You have to go back a lot of Python versions
# if you want a ready-made binary.  When I originally developed this on Python 2.5 for
# 32-bit Windows, the following worked for me:
# (1) download the pre-built pyPortMidi self-installing .exe from the link at
#        http://cratel.wichita.edu/cratel/cratel%20pyportmidi
# (2) install it (either by launching it or by using easy_install on it) and
# (3) also download `pm_dll.dll` (from the same webpage) and put it in the module
#     directory next to `pypm.pyd`
# The pyPortMidi Python/Pyrex source is available at
#        http://alumni.media.mit.edu/~harrison/code.html

#__all__ = [
#	
#] # TODO

import os
import ast # not available in Python 2.5
import sys
import time
import math
import random
import inspect
import warnings

warnings.filterwarnings( 'ignore', category=UserWarning, module='pygame', message='pkg_resources is deprecated.*' ) # pygame devs know about this, but some packaged versions haven't caught up
#import pygame

##############################################################################	
##############################################################################	

KEY_SIGNATURES = {
	'c major': {},
	'g major': {'#':('F')},	
}
ROMAN_TO_STAVE = {'C':0.0, 'D':0.5, 'E':1.0, 'F':1.5, 'G':2.0, 'A':2.5, 'B':3.0}
STAVE_TO_ROMAN = dict([(v,k) for k,v in ROMAN_TO_STAVE.items()])
NATURALS  = {'C':0,     'D':2,     'E':4, 'F':5,     'G':7,     'A':9,     'B':11}
CHROMATIC = ('C', 'C#', 'D', 'D#', 'E',   'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
ACCIDENTALS = {'#':+1, 'b':-1, 'n':0}

try: __file__
except:
	try: frame = inspect.currentframe(); __file__ = inspect.getfile( frame )
	finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
HERE = os.path.realpath( os.path.dirname( __file__ ) ).replace( os.path.sep, '/' )
def PackagePath( *pargs ):
	return os.path.abspath( os.path.join( HERE, *pargs ) ).replace( os.path.sep, '/' )

##############################################################################	
##############################################################################	


def name2semitone(name):
	if isinstance(name, str) and (' ' in name or '+' in name or ',' in name):
		name = name.replace(',', ' ').replace('+', ' ').strip().split()
	if isinstance(name, (tuple,list)): return [name2semitone(x) for x in name]
	nat,name = name[0].upper(),name[1:]
	val = NATURALS[nat]
	while name[0] in ACCIDENTALS:
		val += ACCIDENTALS[name[0]]
		name = name[1:]
	val += 12 * int(name)
	val += 12 # octave shift to make compatible with midi values
	return val
	
##############################################################################	

def semitone2name(val):
	# TODO: could be made sensitive to key signature
	if isinstance(val, (tuple,list)): return [semitone2name(x) for x in val]
	val -= 12 # octave shift to make compatible with midi values
	octave = int(int(val) / 12)
	val -= octave * 12
	name = CHROMATIC[val] + str(octave)
	return name

##############################################################################	

def midi2semitone(midiEvent):
	if len(midiEvent) == 0 or isinstance(midiEvent[0][0], (tuple,list)): return [midi2semitone(x) for x in midiEvent]
	return midiEvent[0][1]
	
##############################################################################	

def name2height(name, key='c major'):
	# TODO:  key signature is currently not respected
	# ideally we would work via name2semitone and see which semitone values appear in the scale 
	if isinstance(name, str) and (' ' in name or '+' in name or ',' in name):
		name = name.replace(',', ' ').replace('+', ' ').strip().split()
	if isinstance(name, (tuple,list)): return [name2height(x, key=key) for x in name]

	ls = ROMAN_TO_STAVE.get(name[0].upper())
	ms = int(name[-1]) - 1
	return 3.5 * ms + ls

##############################################################################	

def height2name(h, accidental='', key='c major'):
	ms = math.floor(h / 3.5)
	ls = h - ms * 3.5
	ls = round(2.0 * ls) / 2.0
	name = STAVE_TO_ROMAN.get(ls)
	if accidental != 'n':
		if name in KEY_SIGNATURES[key].get('#', ()): name += '#'
		if name in KEY_SIGNATURES[key].get('b', ()): name += 'b'
		name += accidental
		name = name.replace('#b','').replace('b#','')
	name += str(int(round(ms+1)))
	return name

##############################################################################	

def NoteSorter(distributionKey):
	clef, name = distributionKey
	semitone = name2semitone(name)
	if not isinstance(semitone, (tuple,list)): semitone = [semitone]
	return clef, list(semitone)

##############################################################################	
##############################################################################	

class Stave(object):
	def __init__(self, screen, image, ledgerline_image, key='c major'):
		self.screen = screen
		self.image = image
		self.ledgerline_image = ledgerline_image
		self.key = key
		
	def draw(self):
		image = self.image
		screen = self.screen
		self.pos = [0, int((screen.get_height() - image.get_height())/2)]
		screen.blit(image, self.pos)
	
	def time2xpos(self, t, imagewidth=None):
		staveheight = self.image.get_height()
		if imagewidth == None: imagewidth = 1.3 * staveheight / 4.0
		if hasattr(imagewidth, 'get_width'): imagewidth = imagewidth.get_width()
		stavewidth  = self.image.get_width()
		x = self.pos[0] +  stavewidth * float(t)
		x -= imagewidth / 2.0
		return int(round(x))
		
	def height2ypos(self, h, imageheight=None):
		staveheight = self.image.get_height()
		if imageheight == None: imageheight = staveheight / 4.0
		if hasattr(imageheight, 'get_height'): imageheight = imageheight.get_height()
		y = self.pos[1] + staveheight - staveheight * h / 4.0
		y -= imageheight / 2.0
		return int(round(y))
		
##############################################################################	
##############################################################################	

class Clef(object):
	def __init__(self, stave, image, voice='treble'):
		self.stave = stave
		self.voice = voice.lower()
		self.base = {'treble':'E4', 'bass':'G2'}.get(self.voice)
		self.image = image
		
	def draw(self):
		image = self.image
		stave = self.stave
		screen = stave.screen
		self.pos = [stave.pos[0], stave.pos[1] + int((stave.image.get_height() - image.get_height())/2)]
		screen.blit(image, self.pos)
		
##############################################################################	
##############################################################################	

class Note(object):
	def __init__(self, clef, image, value='C4'):
		self.__value = []
		self.clef = clef
		self.image = image		
		self.value = value
		self.wrong = self.image.copy()
		for x in range(self.wrong.get_width()):
			for y in range(self.wrong.get_height()):
				v = list(self.wrong.get_at((x,y)))
				v[0] = 255
				self.wrong.set_at((x,y),v)
	
	@property
	def value(self):
		return self.__value
	@value.setter # not available in Python 2.5
	def value(self, x):
		if isinstance(x, str): x = x.replace('+', ' ').replace(',', ' ').strip().split()
		self.__value[:] = x
	
	def height(self):
		key = self.clef.stave.key
		base = name2height(self.clef.base, key)
		value = self.value
		if not isinstance(value, (list,tuple)): value = value.replace('+', ' ').replace(',', ' ').strip().split()
		value = [name2height(v, key) - base for v in value] 
		return value

	def draw(self, t=0.67, wrong=False):
		image = self.image
		if wrong: image = self.wrong
		clef = self.clef
		stave = clef.stave
		screen = stave.screen
		height = self.height()
				
		ledgerline_image = stave.ledgerline_image
		x = stave.time2xpos(t, ledgerline_image)
		llh = ledgerline_image.get_height()
		for h in range(-1, int(math.ceil(min(height)))-1, -1):
			screen.blit(ledgerline_image, (x, stave.height2ypos(h,llh)))
		for h in range(5, int(math.floor(max(height)))+1, +1):
			screen.blit(ledgerline_image, (x, stave.height2ypos(h,llh)))

		x = stave.time2xpos(t, image)
		for h in sorted(height):
			self.pos = [x, stave.height2ypos(h)]
			screen.blit(image, self.pos)

##############################################################################	
##############################################################################	

def LogFileName():
	logfile = 'notes_trainer_history.py'
	import platform
	if platform.system().lower() == 'windows': logfile = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], '_'+logfile)
	else: logfile = os.path.join(os.environ['HOME'], '.'+logfile)
	return logfile

##############################################################################	

def ResponseRecord(t0, note, whichnote, answer, time_limit, when=None):
	if when == None: when = time.time()
	rt = when - t0
	tt = time.localtime(t0)
	trueval = note.value[whichnote]
	truesemi = name2semitone(trueval)
	if isinstance(answer, (int,float)):
		correct = int(answer == truesemi)
	else:
		correct = int(answer != None and answer.upper() == trueval[:len(answer)].upper())
	return (
		('SerialTimeStamp', int(round(t0))),
		('Date', time.strftime('%Y%m%d', tt)),
		('Time', time.strftime('%H%M%S', tt)),
		('KeySignature', note.clef.stave.key),
		('NumberOfNotes', len(note.value)),
		('NoteIndex', int(whichnote)),
		('Clef', note.clef.voice),
		('TrueValue', trueval),
		('TrueMidi', truesemi),
		('Height', note.height()[whichnote]),
		('TimeLimitMsec', int(round(time_limit * 1000))),
		('RespondedInTime', int(rt <= time_limit)),
		('WasCorrect', correct),
		('Response', answer), # integers for midi responses, strings for keyboard responses
		('ResponseTimeMsec', int(round(rt * 1000))),
	)

##############################################################################	

def WriteResponseRecord(a, fp=sys.stdout):
	fp.write("{")
	for k,v in a:
		v = repr(v)
		fp.write("'%s':%s, " % (k, v))
		fp.write(" " * (8 - len(v)))
	fp.write("},\n")

##############################################################################	

def ReadResults(fn=None, criteria={}, raw=False):
	"""
	`criteria` is a dict whose keys are fieldnames of the response record and
	whose values are single-argument lambdas that return whether or not to keep
	this record, given the corresponding value from the record.
	"""
	if fn==None: fn = LogFileName()
	results = []
	try:
		with open(fn) as fh: fileContent = fh.read()
		results += ast.literal_eval( '[' + fileContent + ']' )
	except:
		print( "could not read history file" )
	n={}; c={}; rt={}; p={}
	filtered = []
	for r in results:
		for k,test in criteria.items():
			v = r.get(k)
			if isinstance(test, type) or ( isinstance(test, tuple) and all(isinstance(x, type) for x in test) ):
				if not isinstance(v, test): break
			elif callable(test):
				if not test(v): break
			else:
				if v != test: break
		else: # all tests passed
			filtered.append(r)
	if raw: return filtered
	for r in filtered:
		k = (r['Clef'], r['Height'], r['TrueValue'])
		n[k] = n.get(k, 0) + 1
		c[k] = c.get(k, 0) + r['WasCorrect']
		rt[k] = rt.get(k, 0) + float(r['ResponseTimeMsec'])
	for k in n:
		p[k] = float(n[k] - c[k] + 0.5)/float(n[k] + 1)
		rt[k] /= float(n[k])
	out = {}
	for k in n:
		out[k] = {'n':n[k], 'nwrong':n[k]-c[k], 'pwrong':p[k], 'rtmean':int(round(rt[k]))}
	return out

##############################################################################	

def PrepareImage(img, scalingFactor=1, convertAlpha=True):
	import pygame
	if isinstance(img, str): img = pygame.image.load(PackagePath('images', img))
	if scalingFactor != 1: img = pygame.transform.scale(img, (int(img.get_width()*scalingFactor), int(img.get_height()*scalingFactor)))
	if convertAlpha: img = img.convert_alpha()
	return img
	
##############################################################################	

def InitMidi():
	try: import pygame.midi; pygame.midi.init() # pygame.midi wraps pyPortMidi
	except: import pypm; pypm.Initialize() # pyPortMidi direct (harder to install)
	else: pypm = None
	return pypm

##############################################################################	

def CleanUp():
	if 'pypm' in sys.modules:        import pypm;        pypm.Terminate()
	if 'pygame.midi' in sys.modules: import pygame.midi; pygame.midi.quit()
	if 'pygame' in sys.modules:      import pygame;      pygame.quit()

##############################################################################	
##############################################################################	

def NoteTrainer(time_limit=4.0, midi_channel=0, window_scaling=1.0, clefs=()):
	
	key_signature = 'c major' # TODO: hard-coded for now.  For other keys, Clef.draw needs to be able to render the key signature, Note.draw needs to be able to render accidentals, and the setup should somehow (a) respect the key signature when making the input distribution and (b) have some mechanism for randomly choosing accidentals 

	if isinstance(clefs, str): clefs = clefs.replace(',', ' ').strip().split()
	clefs = sorted(set(clefs))
	if not clefs: clefs = ['bass', 'treble']
	limits = {
		  'bass': ['B1', 'F4'],
		'treble': ['G3', 'D6'],
	}
	distribution = {}	

	import pygame
	midiDevice = None
	if midi_channel:
		try:
			pypm = InitMidi() # pypm will be None if the import succeeds via pygame.midi; it will only be non-None if the actual pypm module was imported (rare case)
		except:
			print( "failed to initialize MIDI" )
		else:
			if pypm: devinfo = pypm.GetDeviceInfo(midi_channel-1)
			else:    devinfo = pygame.midi.get_device_info(midi_channel-1)
			if devinfo:
				print( "found MIDI device \"%s\" on channel %d" % (devinfo[1], midi_channel) )
				if devinfo[2]:
					if pypm: midiDevice = pypm.Input(midi_channel-1)
					else:    midiDevice = pygame.midi.Input(midi_channel-1)
				else: print( "but it does not appear to be an input device" )
			else:
				print( "did not find any MIDI device on channel %d" % midi_channel )
	
	os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
	pygame.init()
	stave_image = PrepareImage('stave.png', convertAlpha=False)
	SCREEN_WIDTH  = int(stave_image.get_width() * window_scaling)
	SCREEN_HEIGHT = int(stave_image.get_height() * 3 * window_scaling)
	BG_COLOR = 255, 255, 200
	
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	
	stave_image = PrepareImage(stave_image, scalingFactor=window_scaling)
	ledgerline_image = PrepareImage('ledger_line.png', scalingFactor=window_scaling)
	note_image = PrepareImage('note_open.png', scalingFactor=window_scaling)
	
	stave = Stave(screen, stave_image, ledgerline_image, key_signature)
	
	key = stave.key
	candidates = []
	for voice in clefs:
		start = name2height(limits[voice][0], key)
		stop  = name2height(limits[voice][1], key)
		while start <= stop:
			val = height2name(start, key=key)
			start += 0.5
			candidates.append((voice, val))
	
	if distribution:
		distribution = dict(distribution)
	else:
		# base the distribution on your previous probability of getting the note wrong
		distribution = ReadResults()
		distribution = dict([((k[0],k[2]), v['pwrong']) for k,v in distribution.items()])
		
		# clip distribution to prescribed clefs and ranges
		for k in list(distribution.keys()):
			voice,values = k
			if not voice in clefs: del distribution[k]; continue
			if not isinstance(values, (list,tuple)): values = [values]
			h = [name2height(value, key) for value in values]
			if min(h) < name2height(limits[voice][0], key) or max(h) > name2height(limits[voice][1], key): del distribution[k]
		
		# ensure full range is in distribution (at max probability if unseen)
		# TODO: could change so that this is done only if we're not dealing with chords...
		if len(distribution): maxp = max(distribution.values())
		else: maxp = 1.0
		for c in candidates:
			if c not in distribution: distribution[c] = maxp
			elif not distribution[c]: distribution[c] = 1.0 / len(candidates)
	
	# normalize distribution
	denom = 0.0
	for n in distribution: denom += float(distribution[n])
	if not denom: raise ValueError( 'empty distribution' )
	for n in distribution: distribution[n] /= denom
	
	for k,v in sorted(distribution.items(), key=lambda item: NoteSorter(item[0])): print( '%20r : %r,' % ( k, v ) )
	
	
	for i in range(len(clefs)):
		voice = clefs[i]
		clef_image = PrepareImage('clef_' + voice + '.png', scalingFactor=window_scaling)
		clefs[i] = Clef(stave, clef_image, voice)
	clefs = dict([(c.voice,c) for c in clefs])
	
	
	fp = open(LogFileName(), "a")
	
	prev = None
	keepgoing = True
	while keepgoing:
		
		chosen = prev
		while chosen == prev:  # TODO:  note that this constraint screws up the probability distribution
			r = random.random()	
			cumulative = 0.0
			chosen = None
			for k in sorted(distribution.keys()):
				chosen = k
				if r <= distribution[k]: break
				r -= distribution[k]
		prev = chosen	
		
		voice,value = chosen
		clef = clefs[voice]
		note = Note(clef, note_image, value)
		
		# Uncomment the line below to demonstrate proof-of-concept that a "note" can just as easily be a chord:
		# `note.value` can be a sequence of names (and can be set that way using a comma- or plus-delimited string).
		# The trainer will wait until the number of keys pressed equals the number of notes displayed (or the trial times out).
		# It will turn red any notes whose corresponding key was not pressed, and count the trial as a success if all notes were hit.
		# The history record will break out each note in the chord, distinguished from the others by the NoteIndex field.
		# To include this feature in the game, it's just a question of coming up with a strategy for exploring the space of chords in the distribution.
		# The proof-of-concept below just adds a major or minor third (depending on the base note) above the target note:
		
		#note.value = note.value[0] + '+' + height2name(name2height(note.value[0]) + 1)

		answers = []
		midikeys = []	
		pygame.event.get()
		t0 = time.time()
		deadline = t0 + time_limit
		screen.fill(BG_COLOR)
		stave.draw()
		clef.draw()
		note.draw()
		pygame.display.flip()
		nnotes = len(note.value)

		if midiDevice:
			if pypm: midiPoll, midiRead = midiDevice.Poll, midiDevice.Read
			else:    midiPoll, midiRead = midiDevice.poll, midiDevice.read
			while midiPoll(): midiRead(1)[0]

		while keepgoing and len(answers) < nnotes:
	
			time.sleep(0.010)
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT: keepgoing = False
				if event.type == pygame.KEYDOWN:
					try: k = event.unicode.upper()
					except: k = '*'
					#print(repr(k))
					if not isinstance( k, type( '' ) ): k = k.encode()
					if k == 'Q': answers = []; keepgoing = False
					if k in ['A', 'B', 'C', 'D', 'E', 'F', 'G'] and len(answers) < nnotes:
						answers.append(ResponseRecord(t0, note, len(answers), k, time_limit))

			if midiDevice:
				while midiPoll():
					event = midiRead(1)[0]
					#print( event )
					if not event[0][2] in [0, 64]:  # 0 and 64 appear to denote "key released" events, which we're not interested in
						midikeys.append((midi2semitone(event), time.time()))
				if len(midikeys) >= nnotes:
					for k,when in sorted(midikeys[:nnotes]):
						answers.append(ResponseRecord(t0, note, len(answers), k, time_limit, when))
			
			if time.time() > deadline:
				while len(answers) < nnotes:
					answers.append(ResponseRecord(t0, note, len(answers), None, time_limit))

		answers = answers[:nnotes]
		correct = [dict(a).get('WasCorrect') for a in answers]
		if not all(correct):
			note.value = [note.value[i] for i in range(len(correct)) if not correct[i]]
			stop = time.time() + 0.5
			note.draw(wrong=True)  # TODO: maybe nice to display the correct answer?
			pygame.display.flip()
			while time.time() < stop:
				pygame.event.get()
				time.sleep(0.010)
							
		for a in answers:
			WriteResponseRecord(a, fp)
		
	if not fp.isatty(): fp.close()
	CleanUp()

##############################################################################	
##############################################################################	
