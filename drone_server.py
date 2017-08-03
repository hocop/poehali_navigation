#My commands
#import requests
#requests.post('http://127.0.0.1:5000/cord', data={'tgFi':'1.0', 'tgTh':'-0.1', 'cam':'left'}).text

import os
from threading import Thread

import time
import random
import pause
import pygame
from flask import Flask, request, abort, send_file, redirect
from math import *

# cameras properties
##########################################################################
camRheight = 0.3
camRdist = 4.0

camLheight = 0.3
camLdist = 5.0
###########################################################################

# For plotting ##############
MAKE_PLOTS = False

xs = [0.0]
ys = [0.0]
zs = [0.0]
if MAKE_PLOTS:
	import matplotlib.pyplot as plt
	plt.axis([-10, 10, -10, 10])
	plt.ion()
#############################

app = Flask(__name__)

tgFiR=0.0
tgThR=0.0
tgFiL=0.0
tgThL=0.0

####### This is the result ##########
x, y, z = 0.0, 0.0, 0.0

def cord(tgFiR, tgThR, tgFiL, tgThL):
	x = (camRdist+camLdist*tgFiL)*tgFiR / (1.0 - tgFiR*tgFiL) # it's global but poh
	y = (camLdist+camRdist*tgFiR)*tgFiL / (1.0 - tgFiR*tgFiL)
	zR = sqrt(x**2+(y+camRdist)**2) * tgThR
	zL = sqrt(y**2+(x+camLdist)**2) * tgThL
	z = (zR+zL) / 2.0
	print 'Deviation: ', (zR+zL)**2
	return x, y, z

@app.route('/cord', methods=['POST'])
def play_endpoint():
	tgFi = float(request.form.get('tgFi'))
	tgTh = float(request.form.get('tgTh'))
	cam = request.form.get('cam')
	tgFiR, tgThR, tgFiL, tgThL = 0,0,0,0
	if cam == 'right':
		tgFiR = tgFi
		tgThR = tgTh
	if cam == 'left':
		tgFiL = tgFi
		tgThL = tgTh
	x, y, z = cord(tgFiR, tgThR, tgFiL, tgThL)
	print x
	print y
	print z
	#### for plotting #######
	if MAKE_PLOTS:
		global xs
		global ys
		global zs
		xs += [x]
		ys += [y]
		zs += [z]
		plt.plot(xs, zs)
		plt.pause(0.05)
	##########################
	return 'ok'


@app.route('/')
def index():
	return redirect('https://github.com/CopterExpress/copter_hack_music_server')


app.run(debug=False, host='0.0.0.0')
