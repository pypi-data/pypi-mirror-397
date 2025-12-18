from __future__ import absolute_import
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
__doc__ = """
""" # TODO

import sys
import argparse
from . import NoteTrainer, LIMITS

def RunNoteTrainer():
	import argparse # not available in Python 2.5 (at least not without installing from PyPI)
	class HelpFormatter( argparse.RawDescriptionHelpFormatter ): pass
	#class HelpFormatter( argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter ): pass
	parser = argparse.ArgumentParser( description=__doc__, formatter_class=HelpFormatter, prog='python -m pystave', )
	parser.add_argument( '-m', '--midi-channel',   '--midichannel', metavar='N',         type=int,        default=0,    help='attempt to open MIDI channel number `N` for input (the default is 0, meaning MIDI is disabled - in which case you can still use keys A-G on your computer keyboard)' )
	parser.add_argument( '-t', '--time-limit',     '--timelimit',   metavar='SECONDS',   type=float,      default=4.0,  help='set the time limit for responding to each note, in seconds' )
	parser.add_argument( '-c', '--clefs',          '--clef',        metavar='X',         action='append', default=[],   help='include clef `X` - Possible values are "bass" and "treble" (the default is to test both, choosing randomly each time around, which is equivalent to supplying `-c treble -c bass` or `-c bass,treble`)' )
	parser.add_argument( '-s', '--window-scaling', '--size',        metavar='FACTOR',    type=float,      default=1.0,  help='scale the size of the window by this factor (default 1.0)' )
	parser.add_argument( '-x', '--window-left',    '--left',        metavar='PIXELS',    type=int,        default=None, help='set the horizontal position of the left edge of the window, in pixels' )
	parser.add_argument( '-y', '--window-top',     '--top',         metavar='PIXELS',    type=int,        default=None, help='set the vertical position of the top edge of the window, in pixels' )
	OPTS = parser.parse_args()
	OPTS.clefs = ','.join( OPTS.clefs ).replace(',', ' ').strip().split()
	unrecognized = [c for c in OPTS.clefs if c not in LIMITS]
	if unrecognized: raise SystemExit('unrecognized clef %r' % unrecognized[0])
	#print(OPTS)
	NoteTrainer(**OPTS.__dict__)

if __name__ == '__main__':
	RunNoteTrainer()
