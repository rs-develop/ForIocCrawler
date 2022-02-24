#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

import logging         # for log 
import os              # for file handling, exit
import sys             # for exit
import multiprocessing # for multiprocessing purpose
import re              # for pattern

from configparser    import ConfigParser, ExtendedInterpolation # for loading config files
from .crawlererr     import CrawlerConfigError, CrawlerError, CrawlerFileReadError, CrawlerProcessError, CrawlerMatchError # ioc crawler error handling
from .crawlerdata    import CrawlerVo, CrawlerWhitelistData # data objects

## --------------------------------------------------------------------------------------------------------------------

LOG = logging.getLogger('IocCrawlerLog')

## --------------------------------------------------------------------------------------------------------------------

## Class for ioc crawling
class Crawler():

    ## constructor
    #  Init variables and read all files
    def __init__(self, pathSrc:str, threadsSrc:int, patternSrc:str, printToStdoutSrc:bool, 
                 resultColumnFormatSrc:list, sectionsSrc:list, matchHighlightingSrc:bool, 
                 matchSizeSrc:int, whitelistSrc:str=None, beforeSrc:int=0, afterSrc:int=0) -> None:
        try:
            # init
            self.blockQueue         = multiprocessing.Queue()
            self.sharedQueue        = multiprocessing.Queue()
            self.processCount       = threadsSrc
            self.processedFileCount = multiprocessing.Value('i', 0)
            self.whiteListedMatches = multiprocessing.Value('i', 0)
            self.overMaxMatchSize   = multiprocessing.Value('i', 0)
            self.rootFilePath       = ""
            self.rootRelPath        = ""
            self.printToStdOut      = printToStdoutSrc
            self.resultList         = []
            self.whitlist           = None
            self.whitlistedFiles    = 0
            self.result_columns     = resultColumnFormatSrc
            self.sectionsForResult  = sectionsSrc
            self.matchHighligting   = matchHighlightingSrc
            self.before             = beforeSrc
            self.after              = afterSrc
            self.matchSize          = matchSizeSrc
            self.beginnRootRelPath  = 0

            self._printCrawlerMessage('[+] Init Crawler')
            LOG.debug("Init Crawler")

            # check path of source dir
            if not os.path.exists(pathSrc):
                raise CrawlerFileReadError("File not found.", pathSrc)
            if not os.path.isabs(pathSrc):
                self.rootFilePath = os.path.abspath(pathSrc)
            else:
                self.rootFilePath = pathSrc

            # set relative path
            if self.rootFilePath != pathSrc and pathSrc != '.':
                self.rootRelPath = os.path.relpath(pathSrc)
                self.beginnRootRelPath = len(self.rootFilePath) - len(self.rootRelPath)
            elif pathSrc == '.':
                self.rootRelPath = self.rootFilePath[self.rootFilePath.rfind('/') + 1:]
                self.beginnRootRelPath = len(self.rootFilePath)
            else:
                self.rootRelPath = pathSrc

            # Check match size
            if self.matchSize < 5:
                raise CrawlerConfigError("Match size have to be greater then 5")

            # load pattern
            self.patterns = self._loadPattern(patternSrc)
            LOG.debug('Pattern loaded: ' + str(len(self.patterns)))
            
            # load whitelist
            if whitelistSrc:
                self.whitlist = self._loadWhitelist(whitelistSrc)
                self._printCrawlerMessage('[+] Whitelisting is enabled')
            else:
                self._printCrawlerMessage('[+] Whitelisting is disabled')
            
            # check files
            self._printCrawlerMessage('[+] Checking files')
            self.fileList = self._readFiles(self.rootFilePath, self.rootRelPath)
            self.fileListSize = len(self.fileList)
            if self.whitlist:
                self._printCrawlerMessage(" |- %d files found, %d whitelisted." %(self.fileListSize, self.whitlistedFiles))
            else:
                self._printCrawlerMessage(" |- %d files found." %(self.fileListSize))
            LOG.debug("%d files found for processing" %(self.fileListSize))

        except CrawlerFileReadError as re:
            raise re
        except CrawlerConfigError as ce:
            raise ce
        except Exception as e:
            raise CrawlerError("Initialisation error. " + getattr(e, 'message', repr(e)))
    # end init

    ## Loads pattern from config or personal file
    #  - patterns will only loaded if they are selected from user
    #  @param patternFileSrc - all search pattern
    #  @return - a patterns dict
    def _loadPattern(self, patternFileSrc) -> list:
        try:
            LOG.debug('Load patterns')
            patternCfg = ConfigParser(interpolation=None)
            patternCfg.read(patternFileSrc)
            
            patterns = {}
            for ioc_type in patternCfg.sections():
                if ioc_type.lower() in self.sectionsForResult:
                    for option in patternCfg.options(ioc_type):
                        ioc_pattern = patternCfg[ioc_type][option]
                        if ioc_pattern:
                            if ioc_type not in patterns:
                                patterns[ioc_type] = [re.compile(b'%b' % bytearray(ioc_pattern.encode('utf-8')))]
                            else:
                                patterns[ioc_type].append(re.compile(b'%b' % bytearray(ioc_pattern.encode('utf-8'))))
                        # end if
                    # end if
                # end for
            # end for

            return patterns
        except Exception as e:
            raise CrawlerConfigError(getattr(e, 'message', repr(e)))
    # end _loadPattern

    ## Loads whitelist from config or personal file
    #  @param whitelistFileSrc
    #  @return - a patterns dict
    def _loadWhitelist(self, whitelistFileSrc) -> CrawlerWhitelistData:
        try:
            LOG.debug('Load whitelist')
            whitelistCfg = ConfigParser(interpolation=ExtendedInterpolation())
            whitelistCfg.read(whitelistFileSrc)
            
            whitelistObj = CrawlerWhitelistData()
            for wh_section in whitelistCfg.sections():
                for option in whitelistCfg.options(wh_section):
                    whitelistObj.addWhiteListItem(wh_section, option, whitelistCfg[wh_section][option].strip().split('\n'))
                # end for
            # end for
            return whitelistObj
        except Exception as e:
            raise CrawlerConfigError(getattr(e, 'message', repr(e)))
    # end _loadWhitelist

    ## Reads all files from the directory
    #  If the file/directory is whitelisted, it will not added to the file list
    #  @param dirSrc root source
    #  @return file list to read
    def _readFiles(self, rootFilePathSrc, relPathSrc) -> list:
        try:
            filesList = []
            filename = ""
            if os.path.isfile(rootFilePathSrc):
                filesList.append(rootFilePathSrc)
            else:
                for root, dirs, files in os.walk(rootFilePathSrc):
                    for filename in files:
                        filePathStr = os.path.join(root, filename)
                        if self.whitlist:
                            # get the index of the relative beginning of the file to check whitelisting
                            idx = filePathStr.index(relPathSrc) + len(relPathSrc)
                            if filePathStr[idx:] in self.whitlist:
                                LOG.debug("%s whitelisted." %(filePathStr[idx:]))
                                self.whitlistedFiles +=1
                            else:
                                filesList.append(filePathStr)
                        else:
                            filesList.append(filePathStr)
                    # end for
                # end for
            # end rootFilePath is directory
        except IOError as io:
            raise CrawlerFileReadError(getattr(io, 'message', repr(io)), filename)
        except Exception as e:
            raise CrawlerError(getattr(e, 'message', repr(e)))
        return filesList
    # end _readFiles

    ## Returns a summary to all found ioc types and the count of matches
    #   - checks the white listed file count
    #   - checks the white listed matches count
    #   @return List of strings
    def getResultSummary(self) -> dict:
        summaryDict = {}

        if self.whitlist:
            if self.whitlistedFiles > 0:
                summaryDict["Whitelisted files"] = self.whitlistedFiles
            if self.whiteListedMatches.value > 0:
                summaryDict["Filtered matches trough whitelisting"] = self.whiteListedMatches.value
            if self.overMaxMatchSize.value > 0:
                summaryDict["Matchs above the max match size"] = self.whiteListedMatches.value

        for item in self.resultList:
            for ioc in item.mCount:
                if ioc in summaryDict.keys():
                    summaryDict[ioc] = summaryDict[ioc] + item.mCount[ioc]
                else:
                    summaryDict[ioc] = item.mCount[ioc]

        return summaryDict
    # end def getResultSummary

    ## Process files from block
    #  - do pattern search
    #  - check for whitelist etc
    #  @param blockFiles - the files to process
    def _processBlock(self, blockFiles, shared_list) -> None:
        try:
            for file in blockFiles:
                try:
                    # create value object for the results - save only the relative path to the results
                    cvo = CrawlerVo(file[self.beginnRootRelPath:])

                    with open(file, 'rb') as f:
                        LOG.debug("Processing %s" %(file))
                        fileSize = os.path.getsize(file)
                        bufSize  = 32384 # read buffer
                        overlap  = 1024  # overlap reading size
                        filePos  = 0     # current position in file
                    
                        # if file size is smaler then the buffer, do no overlap reading
                        if fileSize < bufSize:
                            bufSize = fileSize
                            overlap = 0
                        
                        # read the file in blocks
                        while filePos < fileSize:

                            # log status
                            if filePos > 0:
                                if (filePos/10) % 100 == 0:
                                    LOG.debug("Hanging on %s; read %d/%d bytes" %(file, filePos, fileSize))

                            buffer = None
                            buffer = f.read(bufSize+overlap)

                            for ioc_type in self.patterns:
                                for pattern in self.patterns[ioc_type]:

                                    matchDict = {}

                                    searchRes = re.finditer(pattern, buffer)
                                    
                                    for item in searchRes:
                                        if item.start() < bufSize:
                                            
                                            try:
                                                matchString = item.group(0).decode("utf-8")
                                                
                                                # Check match size
                                                if len(matchString) > self.matchSize:
                                                    raise CrawlerMatchError("Match for %s is greater then %d." %(item, self.matchSize))

                                                before = ""
                                                after  = ""

                                                if self.before > 0:
                                                    raise CrawlerError("self.before not implemented")
                                                elif self.after > 0:
                                                    raise CrawlerError("self.after not implemented")
                                                    #after = buffer[item.start() + len(matchString): item.start() + len(matchString) + self.after].decode("utf-8")
                                                
                                                # maybe feature in one of the next versions
                                                #printDict = {"file" : file, "ioc" : ioc_type, 
                                                #            "match": before + matchString + after, "offset": str(filePos + item.start())}

                                                # hint: save only relative path
                                                printDict = {"path" : file[self.beginnRootRelPath:], "ioc" : ioc_type, "match": matchString, "offset": str(filePos + item.start())}

                                                isWhiteListed = False

                                                if self.whitlist:
                                                    if matchString in self.whitlist:

                                                        isWhiteListed = True
                                                        with self.processedFileCount.get_lock():
                                                            self.whiteListedMatches.value +=1
                                                
                                                if not isWhiteListed:
                                                    if self.printToStdOut:
                                                        self._printCrawlerResult(printDict)
                                                    
                                                    if matchString not in matchDict:
                                                        matchDict[before + matchString + after] = [str(filePos + item.start())]
                                                    else:
                                                        matchDict[before + matchString + after].extend([str(filePos + item.start())])
                                            # end try
                                            except UnicodeDecodeError as ude:
                                                LOG.debug("Decoding error while Processing %s" %(item))
                                            except CrawlerMatchError as me:
                                                with self.processedFileCount.get_lock():
                                                    self.overMaxMatchSize.value +=1
                                                LOG.debug(me)
                                        # end if item.start() < pos + bufSize
                                    # end for item in searchRes

                                    # add match
                                    if matchDict:
                                        cvo.addMatchResults(ioc_type, matchDict)
                                # end for pattern
                            # end for ioc_type

                            # set new offset
                            if f.tell() < fileSize:
                                filePos = f.seek(f.tell() - overlap)
                            else:
                                filePos = f.tell()
                        
                        # end while filePos < fileSize:

                    # end with file

                    # add crawler file value object to the result list
                    shared_list.append(cvo)

                except IOError as ioe:
                    LOG.info("[!] " + getattr(ioe, 'message', repr(ioe)))
            # end for
    
            # set lock for the process counter and save the new status
            with self.processedFileCount.get_lock():
                self.processedFileCount.value += len(blockFiles)
            
            # log processing status for the user
            self._printCrawlerMessage(" |- Processed files: %d / %d [%s %%]" % (self.processedFileCount.value, 
                                                                                self.fileListSize, 
                                                                                self._getProcessStatus()))
        except Exception as e:
            raise CrawlerProcessError(getattr(e, 'message', repr(e)))
    # end processBlock

    ## Main function for processing
    #  - inhires the nested function "procesQueue" for getting tasks from queue
    def do(self) -> None:
        
        self._printCrawlerMessage("[+] Start processing files")
        manager = multiprocessing.Manager()
        shared_list = manager.list()
        processList = []

        ## Get Blocks from Queue and process them until queue is empty
        def _processQueue():
            while not self.blockQueue.empty():
                # process block
                LOG.debug("Get new block from queue")
                blockFiles = self.blockQueue.get()
                self._processBlock(blockFiles, shared_list)
        # end processBlock

        try:
            # check if there is anything to do
            if self.fileListSize < 1:
                raise CrawlerFileReadError("No files to read.")

            # Calc block size based on the file count
            blockSize = 0
            if self.fileListSize < 10:
                blockSize = self.fileListSize
                self.processCount = 1
            elif self.fileListSize < 100:
                blockSize = round(self.fileListSize / 4)
            elif self.fileListSize < 1000:
                blockSize = round(self.fileListSize / 8)
            elif self.fileListSize < 10000:
                blockSize = round(self.fileListSize / 10)

            fileCounter = 0
            blockList = []
            for item in self.fileList:
                blockList.append(item)
                fileCounter += 1

                if fileCounter >= blockSize:
                    self.blockQueue.put(blockList)
                    del blockList
                    blockList = []
                    fileCounter = 0
                # end if
            # add the remaining files to the queue
            if blockList:
                self.blockQueue.put(blockList)

            # create sub processes and start them
            LOG.debug("Using %d processes for processing." %(self.processCount))
            for process in range(1,self.processCount+1):
                LOG.debug("Create Process")
                process = multiprocessing.Process(target=_processQueue)
                process.daemon = True
                process.start()
                processList.append(process)
            # end for
            
            for process in processList:
                process.join()

            # do post processing
            self.resultList.extend(shared_list)
            self._printCrawlerMessage("[+] Finished processing")

        except Exception as e:
            raise CrawlerError("Error in do function. " + getattr(e, 'message', repr(e)))
        except CrawlerProcessError as pe:
            raise pe
        except KeyboardInterrupt:
            print("[!] User interrupt.")
            try:
                for process in processList:
                    process.terminate()
                sys.exit(0)
            except SystemExit:
                os._exit(0)
    # end do

    ## Calculates and returns the processing status
    #  @return string
    def _getProcessStatus(self) -> str:
        return str(round(self.processedFileCount.value / self.fileListSize * 100, 2))

    ## Print function for crawler program messages
    #  - message will be printed if stdout is disabled
    def _printCrawlerMessage(self, msg:str) -> None:
        if not self.printToStdOut:
            if msg:
                print(msg)
    # end def _printCrawlerMessage

    ## Print function for crawler results
    # - message will be printed if stdout is enabled
    def _printCrawlerResult(self, printDictSrc:dict) -> None:
        if self.printToStdOut:
            printStr = ""
            for item in self.result_columns:
                # colored output for match
                if item == "match" and self.matchHighligting:
                    printStr += "\x1b[0;30;41m" + printDictSrc[item] + "\x1b[0m "
                else:
                    printStr += printDictSrc[item] + " "
            print(printStr[:-1])
    # end _printCrawlerResult

# end class crawler