#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, numpy, time
from recorder import *
import pygame, pygame.mouse, logging, os, subprocess, sys, random
from pygame.locals import *

class Visualization:
	def __init__(self, filename, minNum, maxNum):
		"Ininitializes a new pygame screen using the framebuffer"

		self.w = 1280
		self.h = 780
		self.filename = filename
		self.minNum = minNum
		self.maxNum = maxNum
		
		self.framesDirName = "frames"

		self.initPygame()
		self.initRecorder()
		
		self.initNumberOfGifFolders()

	def initPygame(self):
		pygame.init()
		#self.screen = pygame.display.set_mode((self.w, self.h), FULLSCREEN)
		self.screen = pygame.display.set_mode((self.w, self.h))
		pygame.mouse.set_visible(False)
		self.clock = pygame.time.Clock()

	def initRecorder(self):
		self.SR = SwhRecorder()
		self.SR.setup()
		self.SR.continuousStart()
		
	def initNumberOfGifFolders(self):
		files = folders = 0

		for _, dirnames, filenames in os.walk(self.framesDirName):
			# ^ this idiom means "we won't be using this value"
			files += len(filenames)
			folders += len(dirnames)
		
		print "{:,} files, {:,} folders".format(files, folders)
		
		self.numberOfGifFolders = folders

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

	def show(self):
		run = True
		maxAvg = 1
		lastMapped = 0
		tendency = 0
		mapped = 0
		changeImg = False
		coolDownChangeImg = 4
		coolDownCurrentImage = 10
		
		isADanceGif = False
		
		while run:
			try:
				if changeImg:
					#import ipdb; ipdb.set_trace()
					changeImg = False
					coolDownChangeImg = 4
					#from random import randint
					#imgToLoad = randint(0,2)
					
					#print random.choice(os.listdir(self.framesDirName))
					
					gifToLoadDirName = random.choice(os.listdir(self.framesDirName))
					
					print gifToLoadDirName
					
					run = True
					self.filename = "frames/"
					self.filename += gifToLoadDirName
					
					dirOfGifToShow = self.filename
					
					self.filename += "/gif_splited-%d.jpg"
					
					if "dance" in dirOfGifToShow:
						isADanceGif = True
					else:
						isADanceGif = False
					
					print self.filename
					
					self.minNum = 0
					self.maxNum = len([f for f in os.listdir(dirOfGifToShow) if os.path.isfile(os.path.join(dirOfGifToShow, f))])

					print "{:,} files for the gif charged".format(self.maxNum)

					maxAvg = 0
					lastMapped = 0
					tendency = 1
					mapped = 0
			
				#self.clock.tick(20)
				# quit on "window close" and Escape
				for evt in pygame.event.get():
					if evt.type == KEYDOWN:
						if evt.key == K_SPACE:
							pygame.display.toggle_fullscreen()
                                                
						elif evt.key == K_ESCAPE:
							run = False
						elif evt.key == K_F11:
							pygame.display.toggle_fullscreen()
						elif evt.key == K_F6:
							run = True
							#v = Visualization("frames/dough/teig-%d.jpg", 0, 66)
							#self = v
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
						#continue
						tendency = 1
						mapped = lastMapped + tendency
					elif mapped > lastMapped:
						tendency = 1
					elif mapped < lastMapped:
						tendency = -1

					# smooth transition
					if lastMapped - mapped > 2:
						if isADanceGif:
							tendency = 3 * tendency
						else:
							mapped = lastMapped - ((lastMapped - mapped))

					
					if lastMapped - mapped > self.maxNum / 2:
						coolDownChangeImg -= 1
					elif lastMapped - mapped > 8:
						coolDownChangeImg -= 1
					
					if coolDownChangeImg <= 0:
						coolDownChangeImg = 4
						#changeImg = True

					elif coolDownCurrentImage <= 0:
						coolDownChangeImg = 4
						from random import randint
						coolDownCurrentImage = randint(5,40)
						changeImg = True

					if isADanceGif:
						mapped = lastMapped + tendency
						
					# save last image
					lastMapped = mapped
					
					coolDownCurrentImage -= 1
					#print "calcd"
				else:
					#import ipdb; ipdb.set_trace()
					mapped = lastMapped + tendency
					if not self.minNum <= mapped <= self.maxNum:
						continue
					#print "tendency"

				# display image
				#print self.filename % mapped
				#import ipdb; ipdb.set_trace()
				img = pygame.image.load(self.filename % mapped).convert()

				# use whole screen
				img = self.scalePercentage(img, 1)
				self.screen.blit(img, (0, 0))
				pygame.display.update()

				# give it a second until the audio buffer is filled up
				time.sleep(0.01)
			except:
				continue
				#break
		self.SR.continuousEnd()
		self.SR.close()

if __name__ == "__main__":
	#v = Visualization("frames/dancing/my_feels-%d.jpg", 0, 35)
	v = Visualization("frames/dough/gif_splited-%d.jpg", 0, 66)
	#v = Visualization("frames/melon/melon-%d.jpg", 9, 108)
	v.show()
	#pygame.quit()


	
	
