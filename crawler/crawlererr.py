#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

## Cralwer base exception
class CrawlerError(Exception):
	"Base class for exception"
	def __init__(self, what):
		self.msg = "[!] CrawlerError. Message: " + what

## Exception for config errors
class CrawlerConfigError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while loading config. Message: " + what

## Exception for pattern errors
class CrawlerPatternError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while loading pattern file. Message: " + what

class CrawlerMatchError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while processing pattern match. Message: " + what

## Exception for file handling errors
class CrawlerFileReadError(CrawlerError):
	def __init__(self, what, fileNameSrc=None):
		if fileNameSrc:
			self.msg = "[!] Error while reading file : %s. Message: %s" % (fileNameSrc, what)
		else:
			self.msg = "[!] Error while reading source. Message: %s" % (what)

## Exception for processing errors
class CrawlerProcessError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while processing files. Message: " + what

## Exception for export errors
class CrawlerExportError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while export. Message: " + what