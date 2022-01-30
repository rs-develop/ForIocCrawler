#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

## Cralwer base exception
class CrawlerError(Exception):
	"Base class for exception"
	def __init__(self, what):
		self.msg = "[!] CrawlerError. Error message: " + what

## Exception for config errors
class CrawlerConfigError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while loading config file. Error message: " + what

## Exception for pattern errors
class CrawlerPatternError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while loading pattern file. Error message: " + what

class CrawlerMatchError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while processing pattern match. Error message: " + what

## Exception for file handling errors
class CrawlerFileReadError(CrawlerError):
	def __init__(self, what, fileNameSrc=None):
		if fileNameSrc:
			self.msg = "[!] Error while reading file : %s. Error message: %s" % (fileNameSrc, what)
		else:
			self.msg = "[!] Error while reading source. Error message: %s" % (what)

## Exception for processing errors
class CrawlerProcessError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while processing files. Message: " + what

## Exception for export errors
class CrawlerExportError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while export. Message: " + what