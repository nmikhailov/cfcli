#!/usr/bin/python2
# -*- coding: utf-8 -*-

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import poster
import urllib2
import urllib
import cookielib

class CodeforcesClient(object):
	def __init__(self, login, password, debug_level=0):
		""" Start up """
		register_openers()

		self.login = login
		self.password = password

		self.cj = cookielib.MozillaCookieJar()

		self.opener = poster.streaminghttp.register_openers()

		self.opener.add_handler(urllib2.HTTPRedirectHandler())
		self.opener.add_handler(urllib2.HTTPHandler(debuglevel=debug_level))
		self.opener.add_handler(urllib2.HTTPSHandler(debuglevel=debug_level))
		self.opener.add_handler(urllib2.HTTPCookieProcessor(self.cj))

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
		  '_tta' : self.get_tta(),
		  'submitted' : 'true',
		  'remember' : 'true',
		})
		self.opener.open("http://codeforces.com/enter/", login_data)

	def get_language_id(self, file_name):
		langs = {'java' : 23, 'cpp' : 16, 'py' : 7,	'cs' : 9}

		for key, val in langs.items():
			if file_name.endswith('.' + key):
				return val

	def submit_solution(self, contest_id, task_id, file_name):
		data, headers = multipart_encode({
				'submittedProblemIndex': task_id,
				'programTypeId' : self.get_language_id(file_name),
				'source' : '',
				'_tta' : self.get_tta(),
				'sourceFile' : open(file_name),
				})
		print data, headers
		request = urllib2.Request("http://codeforces.com/contest/" + contest_id + "/submit/", data, headers)
		request = self.opener.open(request)
		print ''.join(request.readlines())


if __name__ == '__main__':
	settings = {}
	for line in open(".cfclient"):
		key, val = line.strip().split()
		settings[key] = val

	client = CodeforcesClient(settings['login'], settings['pass'])
	#print client.get_index()
	client.submit_solution('166', 'B', './solutions/solution.cpp')
