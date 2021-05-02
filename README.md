# ForIocCrawler - A forensic ioc crawler.

This project aims to find IoCs in files, Directories and mounted images. The program uses Regex-Pattern as preset.
It also have a whitelisting to prevent false positives like version numbers. You can use personal whitelists and
pattern files. It offers a grep like *stdout* mode and a detailed *forensics* mode.

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
- individual whitelisting
- individual pattern
- set a maximum match size
- verbose mode (see which files are whitelisted etc.)

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

Set a individual pattern and whitelist file:<br>
`forioccrawler -f /home/user/Downloads -w mywhitelist.ini -p mypattern.ini`

## Program modes

The programm comes with two modes:
* stdout printing mode (default)
* forensics

The *stdout* modes is discribed above in the Quick Start section. The *forensics* mode is a good choise for processing large 
directories or mount points. It comes with a better overview: file count, processing status and an ioc summary.

```
[+] Init Crawler
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

## Verbose mode

If u use the *-v* argument a more detailed output will be printed. Also a debug file will be written to the current directory.
In verbose mode whitelisted files (path + name), loaded pattern count, errors, a detailed processing log etc. will be written.

## Whitelisting and Pattern

The machanism is based of *ini* files. There is one *ini* file for whitelisting and one for pattern by default. The basic functionality 
is based of regular expressions and supports out of the box IoCs like IP, URL etc. and a tailored whitelisting. You can either edit the 
default pattern and whitelist files or create your personal.

## Writing a personal whitelisting and pattern file

###### Whitelisting

For creating you own whitelist file, simply create a section and add a option and a value. Possible values are single values or lists 
(see the default whitelist file for an example).

Use your whitelist file: `forioccrawler -f file.bin -w mywhitelist.ini`

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

###### Pattern

Patterns are based of regular expressions. If one of your expressions are incorrect an error message will be written into log (use verbose mode for testing). 
For creating a personal pattern file use the followning example.

Use your pattern file: `forioccrawler -f file.bin -p mypattern.ini`

```
# my pattern file
[DATE_OF_INTEREST]
datetime : (2018\-[0-9]{2}\-[0-9]{2} [01][0-9]\:[0-9]{2}:[0-9]{2})

[SPEZIAL_REQUEST]
value : (GET\srequest\sfor\member.php\s.{3,})"
```

## Program help
```
usage: forioccrawler [-h] -f FILE_OR_DIR [--mode {stdout,forensics}] [--format {file,ioc,match,offset,all} [{file,ioc,match,offset,all} ...]] [--sections SECTIONS [SECTIONS ...]] [-o OUTPUT_FILE_NAME]
                     [-p INDIVIDUAL_PATTERN_FILE] [-w WHITELIST_FILE] [-t THREADS] [-n] [-s MATCH_SIZE] [-v] [--time] [--version]

IoC crawler for files, directories or mount points.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_OR_DIR        File, directory or mount point.
  --mode {stdout,forensics}
                        Output mode. Print results to stdout (default) or run in forensics mode with processing status and summary.
  --format {file,ioc,match,offset,all} [{file,ioc,match,offset,all} ...]
                        Printed columns. On default all columns will be printed.
  --sections SECTIONS [SECTIONS ...]
                        Print results for specific section(s). Available sections are depending of the pattern file. Default sections: "ip url mail win_registry"
  -o OUTPUT_FILE_NAME   Output file name (works also in stdout mode).
  -p INDIVIDUAL_PATTERN_FILE
                        Use individual pattern file.
  -w WHITELIST_FILE     Use individual whitelist file
  -t THREADS, --threads THREADS
                        Max process count (default=4, max=16)
  -n                    No match highligting
  -s MATCH_SIZE         Set maximal match size (default=256). Have to be greater then 5.
  -v, --verbose         Show debug messages and write debug log
  --time                Show run time.
  --version             Show program version
```

## ToDo

For version 1.1
- [X] Implement support for personal whitelists
- [X] Implement support for personal pattern file
- [X] Rename program CSV mode to forensic
- [X] Implement max match size

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