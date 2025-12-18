#!/usr/bin/env -S python
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
TODO: submodule doc
"""

from . import ReadResults

def PlotResponseTimes():
	results = ReadResults(raw=True)
	for i, result in enumerate(results): result['SerialIndex'] = i
	rt = [rec['ResponseTimeMsec'] for rec in results]
	minrt = float(min(rt))
	scalert = float(max(rt)) - minrt
	
	import matplotlib, matplotlib.pyplot as plt
	cm = matplotlib.cm.bwr
	plt.clf()
	subplots = {'bass':plt.subplot(2,1,2), 'treble':plt.subplot(2,1,1)}
	for clef,ax in subplots.items():
		nLedgerLines = 2
		for y in range(-nLedgerLines, 5+nLedgerLines):
			ax.plot([0, 1], [y, y], 'k-', alpha=(1.0 if 0<=y<=4 else 0.1), transform=ax.get_yaxis_transform())
		for rec in results:
			if rec['Clef'] != clef: continue
			c = (rec['ResponseTimeMsec'] - minrt)/scalert
			c = list(cm(c))
			h, = ax.plot(rec['SerialIndex'], rec['Height'], 'ko')
			if rec['WasCorrect']: h.set(marker='o', markerfacecolor=c, markeredgecolor=(0.0,0.0,0.0), markersize=10, alpha=0.9)
			else:                 h.set(marker='x',                                                   markersize= 7, alpha=0.7)
		ax.set_ylim([-4.0, 8.0])
		ax.set_yticks([])
		ax.set_xlim([0,len(results)])
		ax.set_ylabel(clef)
	plt.draw()
	plt.draw()
	
if __name__ == '__main__':
	import sys, matplotlib.pyplot as plt
	if 'IPython' in sys.modules: plt.ion()
	PlotResponseTimes()
	if 'IPython' not in sys.modules: plt.show()
