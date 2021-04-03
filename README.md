# ForIocCrawler - A forensic ioc crawler.

This project aims to find IoCs in files, Directories and mounted images. The program uses Regex-Pattern as preset. 
It also have a whitelisting to prevent false positives like version numbers.

## Features:
- pure python3 no dependencies
- finds IP-Adresses, URLs, E-mail-Adresses and Windows Regestry Keys in
- singe files,
- directories and mount points.
- multiprocessing
- supports large files
- supports to filter for single IoCs like only IPs
- Output to stdout or export data to csv-file
- match highligting
- match offset
- whitelisting

## Installation

Install using pip3:<br>
`pip3 install forioccrawler`

## Quick Start

Simple run over a file. The output of the results will printed to *stdout*.<br>
`forioccrawler -f executable.bin`

For show matches only, you have to use the *format* argument and the match keyword.<br>
`forioccrawler -f test.txt --format match`

You can also add more *format* options if you like. Its also possoble to mix them up.<br>
`forioccrawler -f word.exe --format match offset`

To search only for urls, you can use the *sections* arguments. Multiple options are allowed.<br>
`forioccrawler -f new.txt --sections url`

Print the matches on stdout and write them to file:<br>
`forioccrawler -f new.txt --format ioc match offset -o output_file.csv`

All mentioned arguments are usable with huge directories or mount points with a lot of files:<br>
`forioccrawler -f /mnt/image01 --format ioc match offset -o output_file.csv`

## Program modes

The programm comes with two modes:
* stdout printing mode (default)
* csv

The *stdout* modes is discribed above. The csv mode is better for processing large directories or mount points.
It comes with a better overview: file count, processing status and an ioc summary.

```
+] Init Crawler
[+] Checking files
 |- 246 files found
[+] Start processing files
 |- Processed files: 31 / 246 [12.6 %]
 |- Processed files: 62 / 246 [25.2 %]
 |- Processed files: 93 / 246 [37.8 %]
 |- Processed files: 124 / 246 [50.41 %]
 |- Processed files: 155 / 246 [63.01 %]
 |- Processed files: 186 / 246 [75.61 %]
 |- Processed files: 217 / 246 [88.21 %]
 |- Processed files: 246 / 246 [100.0 %]
[+] Finished processing.
[+] Results written to: out.csv
[+] Summary of unique matches
 |- Whitelisted files: 1
 |- Whitelisted matches: 112
 |- URL: 122
 |- IP: 1979
 |- MAIL: 4
[+] Done
```

## Program help
```
usage: forioccrawler.py [-h] -f FILE_OR_DIR [--mode {stdout,csv}] [--format {file,ioc,match,offset,all} [{file,ioc,match,offset,all} ...]] [--sections {ip,url,mail,reg,all} [{ip,url,mail,reg,all} ...]] [-o OUTPUT_FILE_NAME] [-t THREADS] [-n] [-v]
                        [--time] [--version]

IoC crawler for files, directories or mount points.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_OR_DIR        File, directory or mount point.
  --mode {stdout,csv}   Output mode. Print results to stdout (default) or write them to file.
  --format {file,ioc,match,offset,all} [{file,ioc,match,offset,all} ...]
                        Printed columns. On default all columns will be printed.
  --sections {ip,url,mail,reg,all} [{ip,url,mail,reg,all} ...]
                        Print results for specific section(s) only.
  -o OUTPUT_FILE_NAME   Output file name (works also in stdout mode).
  -t THREADS, --threads THREADS
                        Max process count (default=4, max=16)
  -n                    No match highligting
  -v, --verbose         Show debug messages and write debug log
  --time                Show run time.
  --version             Show program version

```

## ToDo
For version 1.1
- [ ] Implement support for personal whitelists
- [ ] Implement support for personal pattern file
- [ ] Implement support for personal regex

For version 1.2
- [ ] Search in compressed file formats like zip etc.
- [ ] Search in file formats like pdf word etc.
- [ ] Add mor export features like json output
- [ ] Optimize multiprocessing based on file size etc.
- [ ] Rewrite how configurations (user settings like format, blocksize for reading etc) will passed to the crawler
- [ ] Implement switch for printing offset as hex or decimal
- [ ] Implement switch to output/export only unique matches
