# ForIocCrawler - A forensic ioc crawler.

This project aims to find IoCs in files, directories and mounted images. The core of the program is the use of pre defined regex to match common ioc types.
It also have a whitelisting feature to prevent false positives like version numbers, local ip addresses etc. You can use a individual whitelist config to adjust
the results to your need. You can also define individual pattern files. The result will be presented either as console output or as csv export.
The program provides two modes: *stdout* mode and a detailed *forensics* mode.
The IoC Crawler for example can be used, to get an overview of linux server images to extract possible attack vectors.

## Features:

- pure python3 no dependencies
- finds IP-Adresses, URLs, Domains, E-mail-Adresses, Windows Regestry Keys etc. in
- singe files,
- directories and mount points.
- multiprocessing
- supports large files
- supports to filter for single IoCs like only IPs
- Output to stdout or export data to csv-file 
- match highligting
- match offset
- individual whitelisting
- individual pattern
- set a maximum match size
- verbose mode (see which files are whitelisted etc.)

## Installation

Install using pip3:<br>
`pip3 install forioccrawler`

Upgrade using pip3:<br>
`pip3 install forioccrawler -U`

## Quick Start

Simple run over a file. The output of the results will printed to *stdout*.<br>
`forioccrawler evil.exe`

For show matches only, you have to use the *format* argument and the match keyword.<br>
`forioccrawler file.txt --format match`

You can also add more *format* options if you like. Its also possible to mix them up. The following command outputs the match and the offset of the match in the file<br>
`forioccrawler evil.exe --format match offset`

To search only for urls, you can use the *sections* arguments. Multiple options are allowed.<br>
`forioccrawler iocs.txt --sections url`

Print the matches on stdout and write them to file.<br>
`forioccrawler iocs.txt --format ioc match offset -o output_file.csv`

All mentioned arguments are usable with huge directories or mount points with a lot of files using the forensics mode.<br>
`forioccrawler /mnt/server_image --format ioc match offset --mode forensics -o output_file.csv`

Set a individual pattern and whitelist file:<br>
`forioccrawler /home/user/Downloads -w mywhitelist.ini -p mypattern.ini`

To enable whitelisting use the `-e` argument.<br>
`forioccrawler iocs.txt -e`

For processing large files you can use the verbose flag to check the crawler status:<br>
`forioccrawler large.txt -e -v`

## Program modes

The programm provides two modes:
* stdout printing mode (default)
* forensics

The *stdout* modes is discribed above in the Quick Start section. The *forensics* mode is a good choise for processing large 
directories or mount points. Its also good to use for processing large files. 
It comes with a better overview: file count, processing status and an ioc summary.

***Example output of the forensics mode***
```
[+] Init Crawler
[+] Whitelisting is enabled
[+] Checking files
 |- 42 files found, 0 whitelisted.
[+] Start processing files
 |- Processed files: 10 / 42 [23.81 %]
 |- Processed files: 12 / 42 [28.57 %]
 |- Processed files: 22 / 42 [52.38 %]
 |- Processed files: 32 / 42 [76.19 %]
 |- Processed files: 42 / 42 [100.0 %]
[+] Finished processing
[+] Writing Export
[+] Results written to: tests/out.csv
[+] Summary of matches
 |- Filtered matches trough whitelisting: 9896
 |- URL: 1
 |- DOMAIN: 3
 |- IP: 575
 |- WIN_REGISTRY: 16
[+] Done
```

## Verbose mode

The verbose mode *-v* provides a more detailed output. In addition debug file will be written to the current directory.
In verbose mode whitelisted files (path + name), loaded pattern count, errors, a detailed processing log etc. is printed.
It also tells you which file and process causes a long runtime.

## Whitelisting and Pattern

The machanism is based of *ini* files. There is one *ini* file for whitelisting and one for pattern by default. The basic functionality 
is based of regular expressions and supports by default IoCs like IP, URL etc. and a tailored whitelisting. You can either edit the 
default pattern and whitelist file or create a individual file by your own.

## Writing a personal whitelisting and pattern file

###### Whitelisting

Whitelisting is disabled by default. To enable whitelisting use the `-e` argument. Trough whitelisting the amount of false positives and unwanted matches will be noticeable decreaced.
To create your own whitelist file, define a section and add an key and a value.

To use your whitelist file type: `forioccrawler -f file.bin -w mywhitelist.ini -e`

```
# my whitelist file
[WHITELIST_MY_SECTION]
value : myValue

[WHITELIST_NOT_THIS_DIRECTORIES]
linux : /not/here
        /and/not/here
windows: C:\Windows
         Users/user/Desktop
```

Using the `--print-whitelist` argument, you can print the path and the content of the default whitelist.

###### Pattern

Patterns are the core functionality of the ioc crawler. Is one of your expressions are incorrect an error message will be written into the log file. To create a log file use the verbose mode. 
To create a individual pattern file, you have to define a Section. Every Section consists of one or more key and value pairs.

In the following an example for an individual pattern file is shown.
```
# my pattern file
[DATE_OF_INTEREST]
datetime : (2018\-[0-9]{2}\-[0-9]{2} [01][0-9]\:[0-9]{2}:[0-9]{2})

[SPEZIAL_REQUEST]
value : (GET\srequest\sfor\member.php\s.{3,})"
```
To use your own pattern file execute: `forioccrawler -f file.bin -p mypattern.ini`

Using the `--print-pattern` argument, you can print the path and the content of the default whitelist.

## Program help

The `--help` command shows you the following help message:

```
usage: forioccrawler [options] <file/folder>, type -h for help

IoC crawler for files, directories or mount points.

positional arguments:
  source_file_or_dir    Source file, directory or mount point.

optional arguments:
  -h, --help            show this help message and exit
  --mode {stdout,forensics}
                        Output mode. Print results to stdout (default) or run in forensics mode with processing status and summary.
  --format {file,ioc,match,offset,all} [{file,ioc,match,offset,all} ...]
                        Output columns. On default all columns will be printed.
  --sections SECTIONS [SECTIONS ...]
                        Print results for specific section(s) of the pattern file. Default sections are: "ip url domain mail win_registry crypto"
  -o OUTPUT_FILE_NAME   Output file name (works also in stdout mode).
  -p INDIVIDUAL_PATTERN_FILE
                        Use personal pattern file.
  -e                    Enables whitelisting. Use ".forioccrawler --print-whitelist" to view the content.
  -w INDIVIDUAL_WHITELIST_FILE
                        Use personal whitelist file
  -t THREADS, --threads THREADS
                        Max process count for multi processing (default=4, max=16)
  -n                    No match highligting
  -s MATCH_SIZE         Set maximal match size (default=256). Have to be greater then 5.
  -v, --verbose         Show debug messages and write debug log
  --print-whitelist     Prints the path and the content of the default whitelist.
  --print-pattern       Prints the path and the content of the default pattern file.
  --time                Show run time.
  --version             Show program version
```

## ToDo

Version 1.1
- [X] Implement support for personal whitelists
- [X] Implement support for personal pattern file
- [X] Rename program CSV mode to forensic
- [X] Implement max match size

Version 1.1.1
- [X] Fixed a bug which was caused if the source was a absolute path
- [X] Added better debug view. Verbose mode shows now a status of long running tasks
- [X] Changed format of the printing of the runtime
- [X] Only show relative path (the crawled data) in result

Version 1.1.2
- [X] Fixed a bug which causes that not all results were printet/exported
- [X] Removed the -f argument. The source file or folder is now a standard argument
- [X] Whitelisting is disabled by default now. It can be activated using the -e argument
- [X] Added Regex to find Crypto adresses and Domains
- [X] Added two arguments to print the pattern and the whitelist file (path and content)
- [X] Help message improved

For version 1.2
- [ ] Search in compressed file formats like zip etc.
- [ ] Search in file formats like pdf word etc.
- [ ] Add more export features like json output
- [ ] Optimize multiprocessing based on file size etc.
- [ ] Rewrite how configurations (user settings like format, blocksize for reading etc) will passed to the crawler
- [ ] Implement switch for printing offset as hex or decimal
- [ ] Implement switch to output/export only unique matches
- [ ] Implement a whitelist contains feature. Whitelisting for files or matches which contains a specific string.
- [ ] Implement support for personal regex
- [ ] Implement a feature to print bytes before and after a match

## Contact

rsdevelop.contact@gmail.com