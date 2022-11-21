# ForIocCrawler (fic) - A forensic ioc crawler.

This project aims to find IoCs in files, directories and mounted image directories to get an overview of a large amount of unknown data. 
The core of the crawler is the use of pre defined regex to match common IoC types.
It also has a whitelisting feature to prevent common false positives like version numbers, local IP addresses etc. 
Using the whitelisting feature it is possible to hide known good indicators and to reduce a huge amount of data and matches to a manageable count for analysis. 
To adjust the *forioccrawler* and its output to your needs in a specific case, you can use a individual whitelist config.
It is also possible to define individual pattern files to find additional IoCs.
The program provides two modes: 
- the *stdout* mode and 
- a detailed *forensics* mode.

A conceivable use case of the *forioccrawler* is to get an overview of linux server images or a logical copy of a filesystem. It extracts IoCs and provides an simple overview of the data. 
On every matched IoC the path and the offset is specified. The whitelist feature can be used to prevent to search for IoCs in irrelevant directories like `/lib/firmware` or `/dev`.

## Features

- pure python3 no dependencies
- finds IP-Adresses, URLs, Domains, E-mail-Adresses, Windows Regestry Keys etc. in
- singe files,
- directories and mount points.
- multiprocessing
- supports large files
- supports to filter for single IoCs like only IPs
- Output to stdout or export data to csv-file 
- match highligting
- match file offset
- individual whitelisting
- individual pattern
- set a maximum match size
- verbose mode (see which files are whitelisted etc.)

## Installation

Install using pip3:<br>
`pip3 install forioccrawler`

Upgrade using pip3:<br>
`pip3 install forioccrawler -U`

## Main Commands

The forioccrawler has three main commands:
- parse - Subcommand for parsing files and directories
- config - Subcommand for showing the content of the default pattern and whitelist file
- version - Subcommand for showing the program version

## Quick Start Guide for parsing

Simple run over a file. The output of the results will printed to *stdout*.<br>
`fic parse evil.exe`

Print matches only. Specify the column. Available columns are: [file, ioc, match, offset]. On default all columns are printed.<br>
`fic parse file.txt -c match`

It is also possible to ajust the columns to your needs.<br>
`fic parse evil.exe -c match offset`

To search only for urls, you can use the *type* argument. Multiple options are allowed.<br>
`fic parse iocs.txt --type url`
`fic parse iocs.txt --t url`

Print the matches on stdout and write them to file.<br>
`fic parse iocs.txt --columns ioc match -o output_file.csv`
`fic parse iocs.txt -c ioc match -o output_file.csv`

All mentioned arguments can also be used with directories or mount points. For better processing overview the forensic mode can be used.<br>
`fic parse /mnt/server_image -c ioc match offset --mode forensics -o output_file.csv`

Enable whitelisting (Default whitelist).<br>
`fic parse /mnt/server_image --whitelist`

Set a individual pattern and/or whitelist file.<br>
`fic parse /home/user/Downloads --load-whitelist myWhitelist.ini --load-pattern mypattern.ini`
`fic parse /home/user/Downloads --load-pattern mypattern.ini`
`fic parse /home/user/Downloads --load-whitelist myWhitelist.ini`

For processing large files, you can use the forensics mode and the verbose flag to check the status of the crawler.<br>
`fic parse large.txt -m forensics -v -o out.txt`

## Program modes

The programm provides two modes:
* stdout printing mode (default)
* forensics

The *stdout* mode is demonstrated above in the Quick Start section. The *forensics* mode is a good choise for processing large files,
directories or mount points.
It shows a better overview: file count, processing status and an ioc summary after finishing the processing.

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
[+] Results written to: results.csv
[+] Summary of matches
 |- Filtered matches trough whitelisting: 9896
 |- URL: 1
 |- DOMAIN: 3
 |- IP: 575
 |- WIN_REGISTRY: 16
[+] Done
```

## Verbose mode

The verbose mode `-v`, `--verbose` provides a more detailed output. In addition, a debug file will be written to the current directory.
In verbose mode whitelisted files (path + name), loaded pattern count, errors, a detailed processing log etc. is printed.
It also tells you which file and process causes a long runtime.

## Whitelisting and Pattern

The pattern and whitlisting files are based of *ini* files. There is one *ini* file for whitelisting and one for pattern by default. The functionality 
is based on regular expression and supports by default IoCs like IP, URL etc. and a whitelisting for known good or files, which causes a high false positive risk. 

## Writing a personal whitelisting and pattern file

###### Whitelisting

Whitelisting is disabled by default. To enable whitelisting use the `-w`, `--whitelist` argument. Using whitelisting the amount of false positives and known good matches will be decreaced.
If whitelisting is enabled, the crawler checks if a part of the path of the current file or part of the current match is found in the whitelist.

**Example 1**
You have the match `192.168.1.122` for the IP pattern. The crawler checks the whitelist and finds the string `192.168.`. Because the crawler looks not for full whitelist matches but for parts, the match will not counted and is whitelisted. If you only wanna whitelist adresses like `192.168.2.xxx`, you have to change the whitelist entry to `192.168.2`

To create your own whitelist file, define a section and add entries to the section.

To use your whitelist file, add the `--load-whitelist` argument: `fic parse file.bin --load-whitelist myWhitelist.ini`. 
If you load your own whitelist, you dont have to enable whitelisting seperately.
Alternativ you can permanently add your whitelist to the crawler for using it by default `fic config --set-whitelist myWhitelist.ini`.

Below you can find an example for a whitelist file. Using the `fic config --print-whitelist` command, you can print the default whitelist.

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

Patterns are the core functionality of the ioc crawler. Is one of your match expressions are incorrect an error message will be written into the log file. 
To create a log file use the verbose mode (`-v`, `--verbose`).
To create a individual pattern file, you have to define pattern sections. Every section consists of one or more key:value pairs.

To use your personal pattern file, add the `--load-pattern` argument: `fic parse file.bin --load-pattern myPattern.ini`.
To use your pattern everytime you use the crawler, add it as default: `fic config --set-pattern myPattern.ini`.

Using the `fic config --print-pattern` argument, you can print the path and the content of the default pattern.

In the following an example for an individual pattern file is shown.
```
# my pattern file
[DATE_OF_INTEREST]
datetime : (2018\-[0-9]{2}\-[0-9]{2} [01][0-9]\:[0-9]{2}:[0-9]{2})

[SPECIAL_REQUEST]
value : (GET\srequest\sfor\member.php\s.{3,})"
```

## Config Menu

The config menu allows you to change crawler settings, the default whitelist and pattern file and the default thread count.
You can print the current configuration using `fic config --show`.
In addition to change the default pattern und whitelist file, you can restore the default configuration of the crawler.

## Program help

The crawler have two main sub menus: `parse` and `config`.
To see the help for the parse menu type: `fic parse -h`.
To see the help for the config menu type: `fic config`.

## Version

Current version is 1.2.1

## ToDo

For version 1.3
- [ ] Search in compressed file archives like zip etc.
- [ ] Search in file formats like pdf word etc.
- [ ] Add more export features like json output
- [ ] Optimize multiprocessing based on file size etc.
- [ ] Implement switch for printing offset as hex or decimal
- [ ] Implement switch to output/export only unique matches
- [ ] Implement a feature to print bytes before and after a match
- [ ] Test the Crawler on Windows images

## Contact

rsdevelop.contact@gmail.com