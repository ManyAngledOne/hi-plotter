# sudo apt-get install python-pyparsing python-argparse
# TODO: use pySerial or something to talk to the plotter without a third party serial interface
# TODO: translate directly from SVG files, rather than using inkscape as an intermediary to generate HPGL files
from sys import exit, argv
from pyparsing import Word, nums, alphas, OneOrMore, oneOf, Combine, ParseException
from collections import deque

help = '''\nTranslates from .plt files to DMP-2 dumb plotter serial language\n\n
        Usage: python hi-plotter [.PLT] [OUTPUT]\n\n.PLT\t\tPath to .plt file\n\n
        OUTPUT\t\tPath to DMP-2 dumb plotter ascii output file\n\n
        Output should be sent to DMP-2 over serial with 4800 7N2.'''

def plot(x0, y0, xold, yold):

	if x0 > xold:
		if y0 > yold:
			output.write('q')
		elif y0 < yold:
			output.write('s')
		elif y0 == yold
			output.write('r')
	elif x0 < xold:
		if y0 < yold:
			output.write('u')
		elif y0 > yold:
			output.write('w')
		elif y0 == yold:
			output.write('w')
	elif x0 == xold:
		if y0 > yold:
			output.write('p')
		elif y0 < yold:
			output.write('t')

#input
try:
	infile = open(argv[1], 'r')
	output = open(argv[2], 'w')
except IOError:
	print '\nError, invalid path'
	exit(help)

#define parsing parameters
begin = Combine('IN' + ';')
pen = oneOf('PU PD')
choords = Word(nums) + ',' + Word(nums)
slicer = begin + OneOrMore(pen + choords + ';')

try:
	parsed = slicer.parseString(infile.read()) #parse

except ParseException:
	print('\nInput file not .hpgl or similar format?')
	exit(help)

output.write('y') #ensure pen is up
old_pen = 'PU'

x0 = 0
y0 = 0

xold = x0
yold = y0

d = deque(parsed)
d.popleft() #get rid of pen size/color selection that only HP plotters have.

while True:
	try:
		pen = d.popleft()
	except IndexError:
		output.write('y')
		infile.close()
		output.close()
		exit('\nProcess complete. Send to plotter with 4800 7N2 and set the plotter head to the bottom-leftmost position to calibrate position.\n')
	pre_x1 = int(d.popleft())
	d.popleft() #pop comma
	pre_y1 = int(d.popleft())
	d.popleft() #pop semicolon

	if pen == 'PU' and old_pen == 'PD': #only send lift char when pen is down
		output.write('y')
	if pen == 'PD' and old_pen == 'PU': #only send drop char when pen is up
		output.write('z') #give enough padding to allow time for pen to drop before movement (none may be fine)
 
	old_pen = pen

	#scale .plt format numbers to DMP-2 numbers, dmp is 200dpi, .plt is 1268 dpi
	# (x/1268)*200 = x*0.157729
	post_x1 = int(round(pre_x1*0.157729))
	post_y1 = int(round(pre_y1*0.157729))

	x1 = post_x1
	y1 = post_y1
			
	dx = abs(x1-x0)
	dy = abs(y1-y0)
		
	if x0 < x1:
		sx = 1
	else:
		sx = -1
	if y0 < y1:
		sy = 1
	else:
		sy = -1

	err = dx - dy

	while True:
		plot(x0, y0, xold, yold)		

		xold = x0
		yold = y0

		if x0 == x1 and y0 == y1:
			break
		e2 = 2*err
		if e2 > -dy:
			err = err - dy
			x0 = x0 + sx
		if e2 < dx:
			err = err + dx
			y0 = y0 + sy
