__version__ = '1.3.1'

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
import re
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

SCALES = {
	# Major keys
	'C major'  : 'C D E F G A B',
	'G major'  : 'G A B C D E F#',
	'D major'  : 'D E F# G A B C#',
	'A major'  : 'A B C# D E F# G#',
	'E major'  : 'E F# G# A B C# D#',
	'B major'  : 'B C# D# E F# G# A#',
	'F# major' : 'F# G# A# B C# D# E#',
	'C# major' : 'C# D# E# F# G# A# B#',
	
	'F major'  : 'F G A Bb C D E',
	'Bb major' : 'Bb C D Eb F G A',
	'Eb major' : 'Eb F G Ab Bb C D',
	'Ab major' : 'Ab Bb C Db Eb F G',
	'Db major' : 'Db Eb F Gb Ab Bb C',
	'Gb major' : 'Gb Ab Bb Cb Db Eb F',
	'Cb major' : 'Cb Db Eb Fb Gb Ab Bb',
	
	# Natural minor keys
	'A minor'  : 'A B C D E F G',
	'E minor'  : 'E F# G A B C D',
	'B minor'  : 'B C# D E F# G A',
	'F# minor' : 'F# G# A B C# D E',
	'C# minor' : 'C# D# E F# G# A B',
	'G# minor' : 'G# A# B C# D# E F#',
	'D# minor' : 'D# E# F# G# A# B C#',
	
	'D minor'  : 'D E F G A Bb C',
	'G minor'  : 'G A Bb C D Eb F',
	'C minor'  : 'C D Eb F G Ab Bb',
	'F minor'  : 'F G Ab Bb C Db Eb',
	'Bb minor' : 'Bb C Db Eb F Gb Ab',
	'Eb minor' : 'Eb F Gb Ab Bb Cb Db',
	'Ab minor' : 'Ab Bb Cb Db Eb Fb Gb',
}
CHROMATIC      = ('C/B#', 'C#/Db', 'D', 'D#/Eb', 'E/Fb',  'F/E#', 'F#/Gb', 'G', 'G#/Ab', 'A', 'Bb/A#', 'B/Cb')
NATURALS       = {'C':0,           'D':2,        'E':4,   'F':5,           'G':7,        'A':9,        'B':11}
ROMAN_TO_STAVE = {'C':0,           'D':1,        'E':2,   'F':3,           'G':4,        'A':5,        'B': 6}
STAVE_TO_ROMAN = dict([(v,k) for k,v in ROMAN_TO_STAVE.items()])
ACCIDENTALS = {'#':+1, 'b':-1, 'n':0}
CLEFS = {
	  'bass': ['B1', 'G2', 'G3', 'F4'],
	'treble': ['G3', 'E4', 'G5', 'D6'],
	# 0: lowest note we'll normally consider testing on this clef
	# 1: note corresponding to the lowest stave line on this clef
	# 2: note corresponding to the highest position we can use when drawing a key signature on this clef
	# 3: highest note we'll normally consider testing on this clef
}

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

def semitone2name(val, key='C major'):
	if isinstance(val, (tuple,list)): return [semitone2name(x, key=key) for x in val]
	val -= 12 # octave shift to make compatible with midi values
	octave = int(int(val) / 12)
	val -= octave * 12
	name = CHROMATIC[val]
	if '/' in name:
		name = name.split('/')
		scale = SCALES[StandardizeKeyName(key)]
		name = name[1] if name[1] in scale else name[0]
	name += str(octave)
	return name

##############################################################################	

def midi2semitone(midiEvent):
	if len(midiEvent) == 0 or isinstance(midiEvent[0][0], (tuple,list)): return [midi2semitone(x) for x in midiEvent]
	return midiEvent[0][1]
	
##############################################################################	

def name2height(name):
	if isinstance(name, str) and (' ' in name or '+' in name or ',' in name):
		name = name.replace(',', ' ').replace('+', ' ').strip().split()
	if isinstance(name, (tuple,list)): return [name2height(x) for x in name]
	ls = ROMAN_TO_STAVE.get(name[0].upper()) / 2.0 # ignore accidentals---they do not change the height
	ms = int(name[-1]) - 1
	return 3.5 * ms + ls

##############################################################################	

def height2name(h, accidental='', key='C major'):
	ms = math.floor(h / 3.5)
	ls = h - ms * 3.5
	ls = int(round(2.0 * ls))
	name = STAVE_TO_ROMAN.get(ls) # this gets you the name on the naive assumption that the key is C major
	if accidental != 'n':         # and if there's an explicit natural accidental, it can stay that way
		scale = SCALES[StandardizeKeyName(key)]  # but otherwise let's consult the scale of the specified key
		if   name + '#' in scale: name += '#'    # and add sharp if appropriate
		elif name + 'b' in scale: name += 'b'    # or flat if appropriate
		name += accidental
		name = name.replace('#b','').replace('b#','')
	name += str(int(round(ms+1)))
	return name

##############################################################################	

def StandardizeKeyName(k):
	k = k[:1].upper() + k[1:].lower()
	k = re.sub(r'^\s*([A-G])n?([\#b]?)\s*(maj(or)?)?$', r'\1\2 major', k)
	k = re.sub(r'^\s*([A-G])n?([\#b]?)\s*m(in(or)?)?$', r'\1\2 minor', k)
	return k

##############################################################################	

def NoteSorter(arg):
	if isinstance(arg, (tuple, list)): clef, name = arg
	else: clef, name = '???', arg
	semitone = name2semitone(name)
	if not isinstance(semitone, (tuple,list)): semitone = [semitone]
	return clef, list(semitone)

##############################################################################	
##############################################################################	

class Stave(object):
	def __init__(self, screen, image, other_images, key='C major'):
		self.screen = screen
		self.image = image
		self.other_images = other_images
		self.key = StandardizeKeyName(key)
		
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
		self.base = name2height(CLEFS[self.voice][1]) # height of lowest continuous line
		self.image = image
		self.hspace = None
		
	def draw(self):
		image = self.image
		stave = self.stave
		screen = stave.screen
		self.pos = [stave.pos[0], stave.pos[1] + int((stave.image.get_height() - image.get_height())/2)]
		screen.blit(image, self.pos)
		
		self.hspace = 0
		x = self.pos[0] + image.get_width() + 10
		sharps = [name + '#' for name in 'FCGDAEB' if (name + '#') in SCALES[stave.key]]
		flats  = [name + 'b' for name in 'BEADGCF' if (name + 'b') in SCALES[stave.key]]
		previousPreviousHeight = previousHeight = None
		for modifier in sharps + flats:
			minHeight, maxHeight = name2height(CLEFS[self.voice][1:3])
			minHeight -= 0.5 # because the key of Cb major/Ab minor actually marks an Fb just below the lowest line in the bass clef
			heights = [name2height(modifier + str(octave)) for octave in range(10)]
			heights = [height for height in heights if minHeight <= height <= maxHeight]
			if not heights: print('could not work out where to draw %s in key signature' % modifier); continue
			if previousPreviousHeight is None: height = max(heights)
			else: height = min(heights, key=lambda x: abs(x-previousPreviousHeight))
			symbol = Accidental(stave, modifier[-1])
			symbol.draw(x, height - self.base)
			x += symbol.image.get_width()
			previousPreviousHeight = previousHeight
			previousHeight = height
		self.hspace = x / float(stave.image.get_width())
##############################################################################	
##############################################################################	

class Accidental(object):
	def __init__(self, stave, image):
		self.stave = stave
		if isinstance(image, str): image = stave.other_images.get(image, image)
		self.image = image
	
	def draw(self, leftEdgeInPixels, relativeHeight, xshift=0.0):
		image = self.image
		if not image: return
		if isinstance(image, str): print('accidental %r not found' % image); return
		stave = self.stave
		screen = stave.screen
		pos = [ leftEdgeInPixels + image.get_width() * xshift, stave.height2ypos(relativeHeight, image) ]
		screen.blit(image, pos)

##############################################################################	
##############################################################################	

class Note(object):
	def __init__(self, clef, image, value='C4'):
		self.__value = []
		self.clef = clef
		self.image = image		
		self.value = value
		self.wrong = self.image.copy()
		self.last_t = None
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
		return [name2height(v) - self.clef.base for v in self.value] 

	def accidental(self):
		result = []
		key = self.clef.stave.key
		for target in self.value:
			default = height2name(name2height(target), key=key)
			target = target.rstrip('0123456789')[1:]
			default = default.rstrip('0123456789')[1:]
			if   target  == default: result.append('')
			elif target  == '':      result.append('n')
			elif default == '':      result.append(target)
			else:                    result.append(target * 2)
		return result
		
	def draw(self, t=None, wrong=False):
		if t is None: t = self.last_t
		if t is None: t = 0.7
		self.last_t = t
		
		image = self.image
		if wrong: image = self.wrong
		clef = self.clef
		stave = clef.stave
		screen = stave.screen
		height = self.height()
		
		ledgerline_image = stave.other_images['_']
		x = stave.time2xpos(t, ledgerline_image)
		llh = ledgerline_image.get_height()
		for h in range(-1, int(math.ceil(min(height)))-1, -1):
			screen.blit(ledgerline_image, (x, stave.height2ypos(h,llh)))
		for h in range(5, int(math.floor(max(height)))+1, +1):
			screen.blit(ledgerline_image, (x, stave.height2ypos(h,llh)))

		x = stave.time2xpos(t, image)
		for h, accidentalCode in sorted(zip(height, self.accidental())):
			self.pos = [x, stave.height2ypos(h, image)]
			screen.blit(image, self.pos)
			Accidental(stave, accidentalCode).draw(x, h, xshift=-1.1)

##############################################################################	
##############################################################################	

def LogFileName():
	logfile = 'note_trainer_history.py'
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

def ReadResults(fn=None, criteria={}, summarize=False):
	"""
	`criteria` is a dict whose keys are fieldnames of the response record and
	whose values can be:
	
	- types or tuples of types (to reject the record if the corresponding value
	  in the record is not of the specified type)
	- callables that take one argument (the corresponding value in the record)
	  and return False if the record is to be rejected
	- other values, which are simply compared against the corresponding value
	  in the record (the record will be rejected if they do not match).
	"""
	if fn==None: fn = LogFileName()
	results = []
	try:
		with open(fn) as fh: fileContent = fh.read()
		fileContent = '[' + fileContent + ']'
		try:    import ast # not available on Python 2.5
		except: results +=             eval(fileContent)
		else:   results += ast.literal_eval(fileContent)
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
	if not summarize: return filtered
	for r in filtered:
		k = (r['Clef'], r['Height'], r['TrueValue'])
		n[k] = n.get(k, 0) + 1
		c[k] = c.get(k, 0) + r['WasCorrect']
		rt[k] = rt.get(k, 0) + float(r['ResponseTimeMsec'])
	for k in n:
		p[k] = float(n[k] - c[k] + 0.5) / float(n[k] + 1)
		rt[k] /= float(n[k])
	out = {}
	for k in n:
		out[k] = {'n':n[k], 'nwrong':n[k]-c[k], 'pwrong':p[k], 'rtmean':int(round(rt[k]))}
	return out

##############################################################################	

def PrepareImage(img, scalingFactor=1, convertAlpha=True):
	import pygame
	if isinstance(img, str): img = pygame.image.load(PackagePath('images', img))
	if not isinstance(scalingFactor, (tuple, list)): scalingFactor = ( scalingFactor, scalingFactor )
	scalingFactor = tuple(scalingFactor)
	if scalingFactor != (1, 1): img = pygame.transform.scale(img, (int(img.get_width()*scalingFactor[0]), int(img.get_height()*scalingFactor[1])))
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

def GrokDistribution(distribution=None, key='C major', clefs='any', verbose=True):
	"""
	`distribution` may be a `dict`, a `list`, or a `str`.
	
	The `key` argument is used only if `distribution` is empty: in this case,
	a uniform distribution is generated across the notes of the scale of the
	specified key.
	
	The `clefs` argument should specify a sequence of clef names (or it can be
	'any', which is the default). After the distribution is generated, it will
	be cut down as necessary to restrict it to the clefs specified here.
	
	** DISTRIBUTION FORMAT **
	
	When supplying `distribution` as a string, it may be a text specification
	of possible note challenges, or it may be the name of a file that contains
	such a specification.
	
	In the text, represent each possible challenge on a separate line (for
	command-line use, you can run lines together delimited by semicolons if you
	must).
	
	Each line can be formatted as an optional clef name, followed by one or
	more note names, followed by an optional relative-frequency specifier,
	optionally followed by a `%` character denoting a comment.  If octave
	numbers are missing from the notes, they are inferred (chords are assumed
	to be written from the bottom up).  Here is a working example that
	illustrates some of the possibilities::
	
	    treble  E+G+B   %  any EGB chords that fit on the treble clef
	    E+G+B           %  any EGB chords that fit on any of the clefs in use
	    D4+F            %  the D4F4 chord, on any clef on which it fits
	    bass G4  3.0    %  force presentation of G4 on the bass clef (even
	                    %  though it normally would not be considered to fit
	                    %  there) with 3x the normal probability of occurring
	    
	You can use commas, colons, `+` and/or whitespace to delimit clef names,
	note names and frequency specifiers.  This allows you to be fairly free-
	form (as in the example above) or to stick to a strict tabulated format
	if you prefer (csv and tsv both work).	
	""" # NB: the first `*` in the docstring above is detected in __main__.py,
	# to allow distribution-format help to be obtained on the command-line
	
	if isinstance(clefs, str): clefs = None if clefs.lower() in ['any', 'all'] else clefs.replace(',', ' ').split()
	if clefs is None: clefs = list(CLEFS)
	clefs = [c.lower() for c in clefs]
	
	if distribution:
		if isinstance(distribution, str):
			if os.path.isfile(distribution):
				with open(distribution) as fh: distribution = fh.read()
			distribution = [line for line in distribution.replace(';', '\n').replace('\r', '\n').split('\n')]
			
		if isinstance(distribution, (tuple,list)):
			for entry in distribution:
				if len(entry) != 2: break
				if not isinstance(entry[1], (float,int)): break
				if not isinstance(entry[0], tuple): break
				if len(entry[0]) != 2: break
				if not isinstance(entry[0][0], str): break
				if not isinstance(entry[0][1], (str, tuple)): break
				if isinstance(entry[0][1], tuple) and not all(isinstance(x, str) for x in entry[0][1]): break
			else:
				distribution = dict(distribution)
				
		if isinstance(distribution, (tuple,list)):
			src, distribution = distribution, {}
			for entry in src:
				if isinstance(entry, str):
					entry = entry.replace('%', ' %').replace(':', ' ').replace(',', ' ').replace('+', ' ').strip().split()
				entry = list(entry)
				for iWord, word in enumerate(list(entry)):
					if word.startswith('%'): entry = entry[:iWord]; break
				if not entry: continue
				try:    float(entry[-1])
				except: p = 1.0
				else:   p = float(entry.pop(-1))
				if not entry: continue
				voices = []
				while entry and entry[0].lower() in CLEFS: voices.append(entry.pop(0).upper())
				if not voices: voices = list(CLEFS)
				if not entry: continue
				if any(noteName.endswith(tuple('0123456789')) for noteName in entry):
					entries = [entry]
				else:
					voices = [voice.lower() for voice in voices]
					entries = [ [entry[0] + str(octave)] + list(entry[1:]) for octave in range(10) ]
				entries = [InferOctaveNumbers(entry) for entry in entries]
				for voice in voices:
					for entry in entries:
						distribution[(voice, tuple(entry))] = p
						
		distribution = dict(distribution)
		
	else:
		distribution = {}
		scale = SCALES[StandardizeKeyName(key)].split()
		for octave in range(10):
			for voice in clefs:
				for name in scale:
					distribution[(voice, name + str(octave))] = 1.0
		
	# clip distribution to prescribed clefs and ranges
	for k in list(distribution.keys()):
		voice,values = k
		if not voice.lower() in clefs: del distribution[k]; continue
		if voice != voice.lower(): distribution[(voice.lower(), values)] = distribution.pop(k); continue # don't clip, if the voice was in upper case (i.e. it was explicitly supplied in a custom distribution)
		if not isinstance(values, (list,tuple)): values = [values]
		h = name2height(values)
		if min(h) < name2height(CLEFS[voice][0]) or max(h) > name2height(CLEFS[voice][-1]): del distribution[k]

	# the following could be used to modify the distribution on your previous probability of getting the note wrong
	#previousProbabilityWrong = dict([((k[0],k[2]), v['pwrong']) for k,v in ReadResults(summarize=True).items()]) # NB: not exhaustive, nor precisely estimated
	# now apply some heuristic...
		
	# normalize distribution
	denom = 0.0
	for n in distribution: denom += float(distribution[n])
	if not denom: raise ValueError( 'empty distribution' )
	for n in distribution: distribution[n] /= denom
	if verbose: PrintDistribution(distribution)
	return distribution
	
def PrintDistribution(distribution):
	for k,v in sorted(distribution.items(), key=lambda item: NoteSorter(item[0])):
		voice, names = k
		if not isinstance(names, str): names = '+'.join(names)
		print( '%20r : %r,' % ( (voice, names), v ) )

def InferOctaveNumbers(names):
	names = [name[:1].upper() + name[1:].lower() for name in names]
	for direction in [+1, -1]:
		previous = None
		for i, name in enumerate(names):
			if previous and not name.endswith(tuple('0123456789')):
				octave = int(previous[-1])
				if direction * name2semitone(name + str(octave)) < direction * name2semitone(previous): octave += direction
				name += str(octave)
			names[i] = name
			if name.endswith(tuple('0123456789')): previous = name
		names = names[::-1]
	return tuple(names)
		
##############################################################################	
##############################################################################	

def NoteTrainer(
		time_limit = 4.0,
		midi_channel = 'auto',
		clefs = (),
		key_signature = 'C major',
		window_scaling = 1.0,
		window_left = None,
		window_top = None,
		distribution = None,
	):
	
	if isinstance(clefs, str): clefs = clefs.replace(',', ' ').strip().lower().split()
	clefs = sorted(set(clefs))
	if not clefs: clefs = ['bass', 'treble']
	unrecognized = [c for c in clefs if c not in CLEFS]
	if unrecognized: raise ValueError('unrecognized clef %r' % unrecognized[0])
	distribution = GrokDistribution(distribution, key=key_signature, clefs=clefs)

	import pygame
	midiDevice = None
	if midi_channel:
		print('')
		try:
			pypm = InitMidi() # pypm will be None if the import succeeds via pygame.midi; it will only be non-None if the actual pypm module was imported (rare case)
		except:
			print( "failed to initialize MIDI" )
			midi_channel = 0
		else:
			if midi_channel in [-1, 'auto']:
				if pypm: midi_channel = pypm.GetDefaultInputDeviceID() + 1
				else:    midi_channel = pygame.midi.get_default_input_id() + 1
			if not midi_channel:
				print( "no MIDI input device detected" )
			
	if midi_channel:
		if pypm: devinfo = pypm.GetDeviceInfo(midi_channel-1)
		else:    devinfo = pygame.midi.get_device_info(midi_channel-1)
		if devinfo:
			deviceName = devinfo[1]
			if not isinstance(deviceName, type('')): deviceName = deviceName.decode()
			print( "found MIDI device \"%s\" on channel %d" % (deviceName, midi_channel) )
			if devinfo[2]:
				if pypm: midiDevice = pypm.Input(midi_channel-1)
				else:    midiDevice = pygame.midi.Input(midi_channel-1)
			else: print( "but it does not appear to be an input device" )
		else:
			print( "did not find any MIDI device on channel %d" % midi_channel )
	
	if window_left is None: window_left = 0
	if window_top  is None: window_top  = 50 if sys.platform.lower().startswith('win') else 0
	os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (window_left, window_top) # TODO: effective x and y position are incorrect, and weirdly linked once you go onto a second screen on macOS
	#print(os.environ['SDL_VIDEO_WINDOW_POS'])
	pygame.init()
	xstretch = 1.5
	stave_image = PrepareImage('stave.png', convertAlpha=False)
	SCREEN_WIDTH  = int(stave_image.get_width() * xstretch * window_scaling)
	SCREEN_HEIGHT = int(stave_image.get_height() * 3 * window_scaling)
	BG_COLOR = 255, 255, 200
	
	pygame.display.set_mode((1,1), getattr(pygame, 'HIDDEN', 0))
	icon = PrepareImage('icon.png', convertAlpha=True)
	if sys.platform.lower().startswith('win'): icon = pygame.transform.smoothscale(icon, (32, 32))
	pygame.display.set_icon(icon)
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
	pygame.display.set_caption('Note Trainer')
		
	stave_image = PrepareImage(stave_image, scalingFactor=[xstretch * window_scaling, window_scaling])
	note_image = PrepareImage('note_open.png', scalingFactor=window_scaling)
	other_images = {
		'_'  : PrepareImage('ledger_line.png', scalingFactor=window_scaling),
		'n'  : PrepareImage('natural.png',     scalingFactor=window_scaling),
		'#'  : PrepareImage('sharp.png',       scalingFactor=window_scaling),
		'b'  : PrepareImage('flat.png',        scalingFactor=window_scaling),
		'##' : PrepareImage('doublesharp.png', scalingFactor=window_scaling),
		'bb' : PrepareImage('doubleflat.png',  scalingFactor=window_scaling),
	}
	stave = Stave(screen, stave_image, other_images, key_signature)
	
	for i in range(len(clefs)):
		voice = clefs[i]
		clef_image = PrepareImage('clef_' + voice + '.png', scalingFactor=window_scaling)
		clefs[i] = Clef(stave, clef_image, voice)
	clefs = dict([(c.voice,c) for c in clefs])
	
	
	fp = open(LogFileName(), "a")
	
	prev = None
	keepgoing = True
	paused = False
	while keepgoing:
		if not paused or prev is None:
			chosen = prev
			while chosen == prev:  # TODO:  note that this constraint distorts the probability distribution somewhat
				r = random.random()	
				cumulative = 0.0
				chosen = None
				for k in sorted(distribution.keys()):
					chosen = k
					if r <= distribution[k]: break
					r -= distribution[k]
				#break  # uncomment this to avoid distorting the distribution
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
		if not paused: note.draw(0.5 + 0.5 * clef.hspace)
		pygame.display.flip()
		nnotes = len(note.value)

		if midiDevice:
			if pypm: midiPoll, midiRead = midiDevice.Poll, midiDevice.Read
			else:    midiPoll, midiRead = midiDevice.poll, midiDevice.read
			while midiPoll(): midiRead(1)[0]

		while keepgoing and paused:
			answers = []; nnotes = 0
			time.sleep(0.010)
			for event in pygame.event.get():
				if event.type == pygame.QUIT: keepgoing = paused = False
				if event.type == pygame.KEYDOWN:
					try: k = event.unicode.upper()
					except: k = '*'
					if not isinstance(k, type('')): k = k.encode()
					if   k == 'Q': answers = []; keepgoing = False
					elif k in [' ', 'P']: paused = False
					elif k: print(event)

		while keepgoing and len(answers) < nnotes:
	
			time.sleep(0.010)
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT: keepgoing = False
				if event.type == pygame.KEYDOWN:
					try: k = event.unicode.upper()
					except: k = '*'
					if not isinstance(k, type('')): k = k.encode()
					if   k == 'Q': answers = []; keepgoing = False
					elif k in [' ', 'P']: paused = True
					elif k in ['A', 'B', 'C', 'D', 'E', 'F', 'G'] and len(answers) < nnotes:
						answers.append(ResponseRecord(t0, note, len(answers), k, time_limit))
					else: print(event)
			if paused: break
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
					
		if paused: continue
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
