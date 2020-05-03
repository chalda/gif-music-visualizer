#!C:/Python27/python2.exe
# -*- coding: utf-8 -*-

import sys, numpy, time, random, string, re
import sched

from recorder import *
import pygame, pygame.mouse, logging, os, subprocess, sys
from pygame.locals import *

class Visualization:
	def __init__(self, filename, minNum, maxNum):
		"Ininitializes a new pygame screen using the framebuffer"

		self.w = 800
		self.h = 600
		self.filename = filename
		self.minNum = minNum
		self.maxNum = maxNum
		self.current = filename

		self.initPygame()
		self.initRecorder()

	def initPygame(self):
		pygame.init()
		self.screen = pygame.display.set_mode((self.w, self.h))
		pygame.mouse.set_visible(False)
		self.clock = pygame.time.Clock()

	def initRecorder(self):
		self.SR = SwhRecorder()
		self.SR.setup()
		self.SR.continuousStart()

	def translate(self, value, leftMin, leftMax, rightMin, rightMax):
		# Figure out how 'wide' each range is
		leftSpan = leftMax - leftMin
		rightSpan = rightMax - rightMin

		# Convert the left range into a 0-1 range (float)
		valueScaled = float(value - leftMin) / float(leftSpan)

		# Convert the 0-1 range into a value in the right range.
		return rightMin + (valueScaled * rightSpan)

	def scalePercentage(self, surface, perc):
		screenRect = self.screen.get_rect()
		surface = pygame.transform.scale(surface, (int(perc*screenRect.width),
		int(perc*screenRect.height)))
		return surface

	def get_limits(self, path, max):
		try:
			with open(path + "preset.txt") as f:
				print "found a preset"
				array = []
				for line in f:  # read rest of lines
					array.append(int(line))
				print array
				print array[0], array[1]
				return array[0], array[1]
		except:
			print "no preset found"
			return 0, max


	def transition(self, newFilename, newMin, newMax):
		self.filename = newFilename
		self.minNum = newMin
		self.maxNum = newMax
		#self.show()

	def new_random_image(self):
		nextImage = random.choice(os.listdir("frames/"))
		print nextImage
		# os.
		# max_file = [file for file in filenames if max(
		# 	[re.match(r'.*(\d+)\.jpg', i).group(1) for i in filenames if re.match(r'.*(\d+)\.jpg', i)]) in file][0]
		strLen = len(nextImage)
		print strLen
		jpgImages = [f for f in os.listdir("frames/%s/" % (nextImage)) if re.match(r'.*\.jpg', f)]
		print jpgImages

		largest_index = max([int(f[strLen+1:f.index('.')]) for f in jpgImages])

		print largest_index

		minF, maxF = self.get_limits("frames/%s/" % (nextImage),largest_index)
		print minF, maxF


		# os.chdir("frames/" + nextImage)
		print os.curdir
		print("Doing stuff...")
		self.transition("frames/%s/%s-" % (nextImage, nextImage) + "%d.jpg", minF, maxF)

	def show(self):
		run = True
		maxAvg = 1
		lastMapped = 0
		tendency = 0
		mapped = 0
		playTime = 0 #millis
		newImage = False
		while run:
			try:
				#self.clock.tick(20)
				# quit on "window close" and Escape
				for evt in pygame.event.get():
					if evt.type == KEYDOWN:
						if evt.key == K_ESCAPE:
							run = False
						elif evt.key == K_F11:
							pygame.display.toggle_fullscreen()
						elif evt.key == K_DOWN:
							newImage = True
					elif evt.type == QUIT:
						run = False

				if self.SR.newAudio:
					# fourier transformation
					fft = self.SR.fft()[1]
					self.SR.newAudio = False

					avg = reduce(lambda x, y: x + y, fft) / len(fft)

					# dynamic maximum
					if avg > maxAvg:
						maxAvg = avg

					# translate range into number of frames
					mapped = self.translate(avg, 0, maxAvg, self.minNum, self.maxNum)

					# do not update if image does not change
					if mapped == lastMapped:
						continue
					elif mapped > lastMapped:
						tendency = 1
					elif mapped < lastMapped:
						tendency = -1

					# smooth transition
					if lastMapped - mapped > 2:
						mapped = lastMapped - ((lastMapped - mapped)/2)

					# save last image
					lastMapped = mapped
					#print "calcd"
				else:
					mapped = lastMapped + tendency
					if not self.minNum <= mapped <= self.maxNum:
						continue
					#print "tendency"

				# display image
				#print self.filename % mapped
				img = pygame.image.load(self.filename % mapped).convert()

				# use whole screen
				img = self.scalePercentage(img, 1)
				self.screen.blit(img, (0, 0))
				pygame.display.update()

				# give it a second until the audio buffer is filled up
				time.sleep(0.02)
				playTime += 0.02
				#print playTime
				if playTime > 6 or newImage:
					print "new image time"
					newImage = True
					break
			except:
				e = sys.exc_info()[0]
				print e
				break

		if not run:
			self.SR.close()
			pygame.quit()

		return newImage


if __name__ == "__main__":
	#v = Visualization("frames/dough/teig-%d.jpg", 0, 66)
	#v = Visualization("frames/melon/melon-%d.jpg", 9, 108)
	#v = Visualization("frames/dance/dance-%d.jpg", 0, 19)
	#v = Visualization("frames/dance2/dance-%d.jpg", 0, 99)
	v = Visualization("frames/wacky/wacky-%d.jpg", 0, 59)
	#v = Visualization("frames/bernie/bernie-%d.jpg", 50, 170)

# 	s = sched.scheduler(time.time, time.sleep)
# #
# 	def image_loop(sc, newImage):
# 		nI = False
# 		if newImage:
# 			v.new_random_image()
# 			nI = v.show()
# 		s.enter(45, 1, image_loop, (sc, nI))
#
# 	# do your stuff
#
#
# 	s.enter(5, 1, image_loop, (s, True))
# 	s.run()

	while True:
		v.new_random_image()
		nI = v.show()


