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

"""
 -m N             Listen to midi channel #N, The default is 0, meaning no midi
--midichannel=N   input (respond with letter keys A-G only).

 -s X             Scale the size of the window by factor X (default 1).
--size=X


 -t T             Set the time limit for responding to T seconds (default 4).
--timelimit=T


 -c C             Include clef C. Possible values are "bass" and "treble".
--clef=C          The default is to test both (choose randomly each time
                  around) which is equivalent to supplying `-c treble -c bass`
                  or `-c bass,treble`.

""" # TODO: move option-specific doc to argparse help= args

import sys
from . import NoteTrainer

def RunNoteTrainer():
	args = sys.argv[ 1: ]  # TODO: rework this using argparse
	kwargs = {}
	import getopt
	try: opts, args = getopt.getopt(args, 't:c:m:s:', ['timelimit=', 'clef=', 'clefs=', 'midichannel=', 'size='])
	except getopt.GetoptError as e: print( e ); exit() # `as` syntax breaks Python 2.5 compatibility
	for opt,arg in opts:
		if   opt in ['-t', '--time_limit', '--timelimit']: kwargs['time_limit'] = float(arg)
		elif opt in ['-c', '--clefs', '--clef']: kwargs.setdefault('clefs', []).extend(arg.replace(',', ' ').strip().split())
		elif opt in ['-m', '--midi-channel', '--midichannel']: kwargs['midi_channel'] = int(arg)
		elif opt in ['-s', '--window-scaling', '--size']: kwargs['window_scaling'] = float(arg)
	NoteTrainer(**kwargs)

if __name__ == '__main__':
	RunNoteTrainer()
