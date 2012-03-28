#!/usr/bin/python2

import urllib2
import urllib
import cookielib
import os
import math

class CodeforcesClient(object):
	def __init__(self, login, password, debug_level=0):
		""" Start up """
		self.login = login
		self.password = password

		self.cj = cookielib.MozillaCookieJar()

		self.opener = urllib2.build_opener(
		  urllib2.HTTPRedirectHandler(),
		  urllib2.HTTPHandler(debuglevel=debug_level),
		  urllib2.HTTPSHandler(debuglevel=debug_level),
		  urllib2.HTTPCookieProcessor(self.cj)
		)

		self.opener.addheaders = [
		  ('User-agent', ('Mozilla/5.0 (X11; Linux x86_64) '
			'AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21)'))
		]

		self.auth()

	def get_index(self):
		"""
		Get index page
		"""
		response = self.opener.open("http://codeforces.com/")
		return ''.join(response.readlines())
	
	def calc_tta(self, hstr):
		"""
		This calculates protection value (_tta)
		Reversed from js
		"""
		total = 0
		for i, ch in enumerate(hstr):
			total = (total + (i + 1) * (i + 2) * ord(ch)) % 1009
			if i % 3 == 0:
				total += 1
			if i % 2 == 0:
				total *= 2

			if i > 0:
				total -= ord(hstr[i / 2]) / 2 * (total % 5)
			total = total % 1009
		return total

	def get_tta(self):
		"""
		Returns tta for session
		"""	
		tta = filter(lambda x: x.name == '39ce7', self.cj)[0].value
		tta = self.calc_tta(tta)
		return tta

	def auth(self):
		"""
		Auth in codeforces 
		"""

		# Retrive cookies
		self.opener.open('http://codeforces.com/enter/')

		# Log in
		login_data = urllib.urlencode({
		  'handle' : self.login,
		  'password' : self.password,
		  '_tta' : get_tta(),
		  'submitted' : 'true',
		  'remember' : 'true',
		})
		self.opener.open("http://codeforces.com/enter/", login_data)

if __name__ == '__main__':
	settings = {}
	for line in open(".cfclient"):
		key, val = line.strip().split()
		settings[key] = val
	
	client = CodeforcesClient(settings['login'], settings['pass'])
	print client.get_index()
