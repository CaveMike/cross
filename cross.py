#!/usr/local/bin/python
#!/usr/bin/python
#!/usr/local/bin/python
from UserString import MutableString
import string
from operator import itemgetter
import yaml
#import array
import random
import sys
import os
from optparse import OptionParser
import copy
import itertools

BLANK = '_'
BLOCK = '#'

class Dictionary:
	WEIGHT = \
		{
		'a'	:  8.167,
		'b'	:  1.492,
		'c'	:  2.782,
		'd'	:  4.253,
		'e'	: 12.702,
		'f'	:  2.228,
		'g'	:  2.015,
		'h'	:  6.094,
		'i'	:  6.966,
		'j'	:  0.153,
		'k'	:  0.772,
		'l'	:  4.025,
		'm'	:  2.406,
		'n'	:  6.749,
		'o'	:  7.507,
		'p'	:  1.929,
		'q'	:  0.095,
		'r'	:  5.987,
		's'	:  6.327,
		't'	:  9.056,
		'u'	:  2.758,
		'v'	:  0.978,
		'w'	:  2.360,
		'x'	:  0.150,
		'y'	:  1.974,
		'z'	:  0.074,
		}


	def __init__( self, min = None, max = None ):
		self.d = {}
		self.min = min
		self.max = max

	def load( self, path ):
		with open( path, 'r' ) as f:
			self.d = yaml.load( stream=f )

	def save( self, path ):
		with open( path, 'w' ) as f:
			yaml.dump( d.d, stream=f )

	def importFile( self, path ):
		try:
			with open( path, 'r' ) as f:
				for l in f:
					self.addWord( l.rstrip( '\n' ) )
		except IOError, e:
			print e


		self.sort()

	def addWord( self, word ):
		l = len(word)

		if self.min and l < self.min:
			return
		elif self.max and l > self.max:
			return

		try:
			weight = 0
			for c in word:
				weight += self.WEIGHT[c.lower()]
			weight /= l
			#print word, weight
		except KeyError:
			#print 'Invalid character ' + c + ' in ' + word + '.'
			return

		if l not in self.d:
			self.d[l] = []

		self.d[l].append( (word.lower(), weight) )

	def sort( self ):
		for k in self.d:
			# Remove duplicates.
			words = list(set(self.d[k]))
			# Sort based on weight.
			words.sort( key=itemgetter(1), reverse=True)
			# Save the new list.
			self.d[k] = words

	def shuffle( self ):
		for k in self.d.iterkeys():
			random.shuffle( self.d[k] )

	def isMatch( self, w1, w2 ):
		for i in range(len(w1)):
			if w1[i] == w2[i]:
				continue
			elif w1[i] == BLANK:
				continue
			else:
				return False

		return True

	def getMatches( self, w ):
		l = len(w)

		if l not in self.d:
			return None

		matches = []

		words = self.d[l]
		for entry in self.d[l]:
			if self.isMatch( w, entry[0] ):
				matches.append( entry[0] )

		return matches

	def __str__( self ):
		s = MutableString()

		for k in self.d:
			s += '['
			s += k
			s += ']: '
			s += len(self.d[k])

			if len(self.d[k]) < 10:
				s += ' '
				s += self.d[k]

			s += '\n'

		return str(s)

class Grid:
	HORIZONTAL = 'h'
	VERTICAL   = 'v'

	def __init__( self, width, height = None ):
		if not width:
			return

		if not height:
			height = width

		self.g = []
		self.width = width
		self.height = height

		for r in range(self.height):
			row = []
			for c in range(self.width):
				row.append( BLANK )
			self.g.append(row)

	def getAbs( self, x, y ):
		return self.g[y][x]

	def setAbs( self, x, y, v ):
		self.g[y][x] = v

	def getMaxX( self, o ):
		if o == self.HORIZONTAL:
			return self.width
		elif o == self.VERTICAL:
			return self.height
		else:
			raise Exception( 'Invalid orientation, ' + str(o) + '.' )

	def getMaxY( self, o ):
		if o == self.HORIZONTAL:
			return self.height
		elif o == self.VERTICAL:
			return self.width
		else:
			raise Exception( 'Invalid orientation, ' + str(o) + '.' )

	def get( self, o, x, y ):
		if o == self.HORIZONTAL:
			return self.g[y][x]
		elif o == self.VERTICAL:
			return self.g[x][y]
		else:
			raise Exception( 'Invalid orientation, ' + str(o) + '.' )

	def set( self, o, x, y, v ):
		if o == self.HORIZONTAL:
			self.g[y][x] = v
		elif o == self.VERTICAL:
			self.g[x][y] = v
		else:
			raise Exception( 'Invalid orientation, ' + str(o) + '.' )

	def getWord( self, o, x, y ):
		w = ''
		for i in range(x, self.getMaxX(o)):
			v = self.get( o, i, y )
			if v == BLOCK:
				break
			w += v

		return w

	def setWord( self, o, x, y, w ):
		if len(w) > ( self.getMaxX(o) + x ):
			raise Exception( 'Word too long.  Failed to add ' + str(w) + ' at ' + str(o) + ':(' + str(x) + ', ' + str(y) + ').' )

		i = 0
		for c in w:
			self.set( o, i, y, c )
			i += 1

	def getSlotsByOrientation( self, orientation ):
		slots = {}

		for y in range( self.getMaxY(orientation) ):
			start = 0
			for x in range( self.getMaxX(orientation) + 1 ):
				if x == self.getMaxX(orientation) or self.get(orientation, x, y) == BLOCK:
					# Found a block, check if we have a word.
					l = x - start
					if l:
						# We have a word.
						if l not in slots:
							slots[l] = []

						slots[l].append( (orientation, start, y) )

					# Start a new word.
					start = x + 1

		return slots

	def getSlots( self ):
		hslots = self.getSlotsByOrientation( self.HORIZONTAL )
		vslots = self.getSlotsByOrientation( self.VERTICAL )
		return hslots, vslots

	def __str__( self ):
		s = MutableString()

		s += 'width: '
		s += self.width
		s += '\n'
		s += 'height: '
		s += self.height
		s += '\n'

		s += '-' * ( self.width + 2 ) + '\n'
		for r in self.g:
			s += '|'
			for c in r:
				s += c
			s += '|\n'

		s += '-' * ( self.width + 2 ) + '\n'

		return str(s)

class Template:
	@staticmethod
	def set( grid, blockPercentage ):
		numBlocks = int( blockPercentage * grid.height * grid.width )
		print 'Number of blocks: %d.' % ( numBlocks )
		for i in range(numBlocks):
			while True:
				r = random.randrange(grid.height)
				c = random.randrange(grid.width)
				print 'Block at ( %d, %d )' % ( r, c )
				if grid.getAbs( r, c ) == BLOCK:
					# Try again.
					print 'Already has a block.  Try again.'
					continue;

				grid.setAbs( r, c, BLOCK )
				break

class Filler:
	def __init__( self, g, d ):
		self.g = g
		self.d = d
		self.used = set()
		self.undo = []

	def iter( self ):
		( hslots, vslots ) = self.g.getSlots()
		print 'hslots:', hslots
		print 'vslots:', vslots

		keys = sorted(hslots, reverse=True)
		for k in keys:
			print k
			for entry in hslots[k]:
				yield entry 

		keys = sorted(vslots, reverse=True)
		for k in keys:
			print k
			for entry in vslots[k]:
				yield entry 

	def fill( self ):
		self.__fill( self.iter() )

	def __fill( self, i ):
		try:
			entry = i.next()
		except StopIteration:
			print 'Success.  All slots have been filled.'
			return True

		w = self.g.getWord( *entry )
		print w
		matches = d.getMatches( w )
		for match in matches:
			if match not in self.used:
				print 'new:', entry, w, matches, match
				self.used.add( match )
				self.undo.append( entry + ( w, match ) )

				i, inew = itertools.tee( i )
				if self.__fill( inew ):
					print 'Success.  All subsequent slots have been filled.'
					return True

				print 'Used set (before):', self.used
				self.used.remove( match )
				print 'Used set (after):', self.used
				self.undo.pop()
			else:
				print 'Used already:', match

		print 'Cannot match ', entry, w, matches
		return False
	

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('--seed', action='store', dest='seed', default=None, help='seed the random generator')
	parser.add_option('--dict', dest='dictionaryPath', default='american-english-shorter.yaml', metavar='FILE', help='specify the dictionary file')
	parser.add_option('--import', dest='importPath', default=None, metavar='FILE', help='specify the word list to import')
	parser.add_option('--height', dest='height', default=4, help='specify the height of the puzzle')
	parser.add_option('--width', dest='width', default=4, help='specify the width of the puzzle')
	parser.add_option('--min', dest='min', default=3, help='specify the minimum word length')

	(options, args) = parser.parse_args()
	print sys.argv
	print 'options', type(options), options
	print 'args', args

	if options.seed:
		random.seed( options.seed )

	d = None
	if options.importPath:
		d = Dictionary( options.min )
		d.importFile( options.importPath )
		d.save( options.importPath + '.yaml' )
		print d

	if options.dictionaryPath:
		d = Dictionary()
		d.load( options.dictionaryPath )
		print d

	g = None
	if options.width and options.height:
		g = Grid( options.width, options.height )

		#Template.set( g, 0.5 )

		#g.setAbs( 0, 2, 'h' )
		#g.setAbs( 3, 2, BLOCK )
		#g.set( 'v', 3, 1, 'z' )
		g.setWord( 'h', 0, 0, 'nice' )

		#print 'x', g.getWord( 'h', 0, 2 )
		#print 'y', g.getWord( 'h', 1, 3 )
		#print 'z', g.getWord( 'v', 0, 1 )
		#print 'a', g.getWord( 'v', 3, 1 )

		print g

	if g and d:
		Filler( g, d ).fill()
		print g

#	for i in range(g.width):
#		w = g.getWord( 'v', 0, i )
#		print 'word', w
#		matches = d.getMatches( w )
#		print 'matches', matches
#		if matches:
#			g.setWord( 'v', 0, i, matches[0] )

# different grid strategies: fixed, symmetric, british/american
# difficulty for words
# clue database with difficulty
# extend dictionary to include acronyms, british-english, foreign languages
# min-word, max-word, horizontal-symmetry, vertical-symmetry

