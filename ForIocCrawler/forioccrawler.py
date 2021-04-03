#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------
#
# Copyright (c) 2021, rs-develop (rsdevelop.contact@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
## --------------------------------------------------------------------------------------------------------------------
#
# File:             ioccrawler.py
# Description:      The forensic ioc crawler extract iocs from directorys and files.
# Usage:            ioccrawler.py [-h]
# Author:           rs-develop
#
## --------------------------------------------------------------------------------------------------------------------

import logging         # for output
import os			   # for path, exit
import sys			   # for exit
import argparse		   # for program arguments
import timeit		   # for run time

from configparser import ConfigParser, ExtendedInterpolation # for loading config files
from crawler import crawler
from crawler.crawlererr import CrawlerError, CrawlerConfigError, CrawlerExportError, CrawlerFileReadError
from crawler.exporter import CrawlerExporter

## --------------------------------------------------------------------------------------------------------------------

# init root logger
logging.root.setLevel(logging.NOTSET)

# Create logger
LOG = logging.getLogger('IocCrawlerLog')
LOG.setLevel(logging.NOTSET)

## --------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

	try:

		printToStdout  = False
		basedir        = os.path.dirname(os.path.abspath(__file__))
		result_columns = []

		# configs
		config_file    = os.path.join(basedir, 'data/config.ini')
		pattern_file   = os.path.join(basedir, 'data/pattern.ini')
		whitelist_file = os.path.join(basedir, 'data/whitelist.ini')
		
		# read config
		try:
			config = ConfigParser(interpolation=ExtendedInterpolation())
			config.read(config_file)
			result_columns.extend(config["settings"]["result_columns"].strip().split('\n'))
		except Exception as e:
			raise CrawlerConfigError(getattr(e, 'message', repr(e)))

		# parse arguments
		argparser = argparse.ArgumentParser(description="IoC crawler for files, directories or mount points.")
		argparser.add_argument('-f', dest='FILE_OR_DIR', required=True, action='store', help='File, directory or mount point.')
		argparser.add_argument("--mode", choices=["stdout","csv"], dest='output_mode', default='stdout', help='Output mode. Print results to stdout (default) or write them to file.')
		argparser.add_argument('--format', choices=result_columns + ["all"], default="all", nargs='+', help='Printed columns. On default all columns will be printed.')
		argparser.add_argument('--sections', choices=["ip", "url", "mail", "reg", "all"], default="all", nargs='+', help="Print results for specific section(s) only.")
		argparser.add_argument('-o', dest='output_file_name', help='Output file name (works also in stdout mode).')
		#argparser.add_argument('-p', dest='pattern_file', default=pattern_file, help='personal pattern file')
		#argparser.add_argument('-w', dest='whitelist_file', default=whitelist_file, help='personal whitelist file')
		#argparser.add_argument('-E', dest='expresion', help='regex')
		argparser.add_argument("-t", "--threads", type=int, default=4, help='Max process count (default=4, max=%d)' % int(config['settings']['max_processes']))
		argparser.add_argument('-n', action='store_false', dest='match_highlighting', default=True, help="No match highligting")
		argparser.add_argument("-v", "--verbose", action = "store_true", help='Show debug messages and write debug log')
		argparser.add_argument("--time", action = "store_true", help='Show run time.')
		argparser.add_argument("--version", action='version', version=config['settings']['version'], help='Show program version')
		args = argparser.parse_args()

		# if verbose flag is set, set logging to debug
		if args.verbose:
			LOG.setLevel(logging.DEBUG)

			# Create debug log handler for console
			debug_log = logging.StreamHandler()
			debug_log.setLevel(logging.DEBUG) # log only debug
			debug_log.setFormatter(logging.Formatter('DEBUG %(asctime)-15s %(processName)s %(module)s %(lineno)d %(message)s'))

			# Create file log handler for debug
			if os.path.exists('debug.log'):
				os.remove('debug.log')
			fh_debug = logging.FileHandler('debug.log')
			fh_debug.setLevel(logging.DEBUG) # log only debug
			fh_debug.setFormatter(logging.Formatter('DEBUG %(asctime)-15s %(processName)s %(module)s %(lineno)d %(message)s'))

			# Add log handler
			LOG.addHandler(debug_log)
			LOG.addHandler(fh_debug)
			
			# set timer for run time
			start = timeit.default_timer()

			LOG.debug("Debug initialisation finished")
			LOG.debug("Arguments: %s" %str(args))

		# if time arg, show run time at the end
		elif args.time:
			start = timeit.default_timer()

		# check mode
		if args.output_mode not in ["csv", "stdout"]:
			argparser.print_help()
			raise CrawlerError("Unknown format: %s." %args.output_mode)
		elif args.output_mode == "csv" and args.output_file_name == None:
			argparser.print_help()
			raise CrawlerError("CSV-Mode requires a output file name.")

		# check for stdout option and reset output path
		if args.output_mode == "stdout":
			printToStdout = True

		# check format options for reslult columns
		if args.format != "all":
			result_columns = args.format

		if args.sections == "all":
			args.sections = ["ip", "url", "mail", "reg"]

		## -------------------------------------------------------------------
		# run crawler
		ioccrawler = crawler.Crawler(args.FILE_OR_DIR, args.threads, pattern_file, printToStdout, result_columns, 
									 args.sections, args.match_highlighting, whitelist_file)
		ioccrawler.do()
		## -------------------------------------------------------------------

		# check the export option
		if args.output_file_name:
			CrawlerExporter.csvExport(args.output_file_name, ioccrawler.resultList, result_columns)
			print('[+] Results written to: %s' %(args.output_file_name))

		# show run time
		if args.time or args.verbose:
			stop = timeit.default_timer()
			print('[+] Jobs finished in: ', stop - start)

		# show summary if not printed to stdout
		if not printToStdout:
			
			summary = ioccrawler.getResultSummary()
			print("[+] Summary of unique matches")
			for ioc in summary:
				print(" |- %s: %s" %(ioc, summary[ioc]))
		
			# show run time
			if args.time or args.verbose:
				stop = timeit.default_timer()
				print('[+] Jobs finished in: ', stop - start)
		
			print("[+] Done")
		# end if

	# Handle errors
	except CrawlerConfigError as cerr:
		print(cerr.msg)
	except CrawlerFileReadError as ferr:
		print(ferr.msg)
	except CrawlerError as err:
		print(err.msg)
	except KeyboardInterrupt:
		print("[!] User interrupt.")
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
	except Exception as e:
		print("[!] Unhandled error: " + str(e))

# end main