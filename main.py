#!/usr/bin/python2
# -*- coding: utf-8 -*-

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import BeautifulSoup
import poster
import urllib2
import urllib
import cookielib
import sys
import re
from console import ansiformat

class Table(object):
	def __init__(self, table, c_cross='+', c_horiz='-', c_vert='|'):
		"""Normalize table"""
		self.c_cross = c_cross
		self.c_horiz = c_horiz
		self.c_vert = c_vert

		self.table = table
		# Calc width
		self.widths = [0] * len(table[0])
		for row in self.table:
			for cid, element in enumerate(row):
				self.widths[cid] = max(self.widths[cid], len(element) + 1)

		for cid, element in enumerate(self.table[0]):
			if (self.widths[cid] - len(element)) % 2:
				self.widths[cid] += 1

	def __str__(self):
		delim = self.c_cross + ''.join([self.c_horiz * w + self.c_cross for w in self.widths])
		text = delim + "\n"

		for r_id, row in enumerate(self.table):
			for elem, width in zip(row, self.widths):
				color = get_color(elem)
				if r_id == 0:
					text += self.c_vert + ansiformat('*blue*', elem.center(width))
				else:
					text += self.c_vert + ansiformat(color, elem.ljust(width))

			text += self.c_vert + '\n'
			if r_id == 0:
				text += delim + '\n'

		return text + delim


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

	def submit_solution(self, contest_id, task_id, file_name):
		data, headers = multipart_encode({
				'submittedProblemIndex': task_id,
				'programTypeId' : get_language_id(file_name),
				'source' : '',
				'_tta' : self.get_tta(),
				'sourceFile' : open(file_name),
				})
		print data, headers
		request = urllib2.Request("http://codeforces.com/contest/" + contest_id + "/submit/", data, headers)
		request = self.opener.open(request)
		print ''.join(request.readlines())

	def get_status(self, contest_id):
		request = self.opener.open("http://codeforces.com/contest/" + str(contest_id) + "/my")
		html = ''.join(request.readlines())
		soup = BeautifulSoup.BeautifulSoup(html)
		soup_table = soup.find(attrs={'class' : 'status-frame-datatable'})
		table = []
		for row in soup_table.findAll('tr'):
			trow = []
			for header in row.findAll(re.compile('t[dh]')):
				trow += [header.getText().strip()]
			table += [trow]
		print str(Table(table))
		
def get_language_id(file_name):
	langs = {'java' : 23, 'cpp' : 16, 'py' : 7,	'cs' : 9}

	for key, val in langs.items():
		if file_name.endswith('.' + key):
			return val

def get_color(text):
	colors = {
			'Aceepted' : '*green*',
			'Time limit exceeded on test' : 'red',
			'Runtime error' : 'red',
			'Wrong answer' : 'red',
			'Compilation error' : 'red',
			}
	for key, value in colors.items():
		if text.startswith(key):
			return value
	return ''

if __name__ == '__main__':
	settings = {}
	for line in open(".cfclient"):
		key, val = line.strip().split()
		settings[key] = val

	client = CodeforcesClient(settings['login'], settings['pass'])
	#print client.get_index()
	#client.submit_solution('166', 'B', './solutions/solution.cpp')
	client.get_status(166)
