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

## Exception for file handling errors
class CrawlerFileReadError(CrawlerError):
	def __init__(self, fileNameSrc, what):
		self.msg = "[!] Error while reading file : %s. Message: %s" % (fileNameSrc, what)

## Exception for processing errors
class CrawlerProcessError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while processing files. Message: " + what

## Exception for export errors
class CrawlerExportError(CrawlerError):
	def __init__(self, what):
		self.msg = "[!] Error while export. Message: " + what