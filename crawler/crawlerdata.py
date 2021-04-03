#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

import os

## --------------------------------------------------------------------------------------------------------------------

## Crawler value object
#  represents a file object and all matches of it
class CrawlerVo:
    def __init__(self, filePathSrc:str) -> None:
        self.path     = filePathSrc
        self.fileName = os.path.basename(filePathSrc)
        self.mResults = {}
        self.mCount   = {}
    
    def addMatchResults(self, iocTypeSrc:str, matchDictSrc:dict) -> None:
        if matchDictSrc:
            if iocTypeSrc not in self.mResults:
                self.mResults[iocTypeSrc] = matchDictSrc
                self.mCount[iocTypeSrc] = len(matchDictSrc.values())
            else:
                self.mResults[iocTypeSrc].update(matchDictSrc)
                self.mCount[iocTypeSrc] = self.mCount[iocTypeSrc] + len(matchDictSrc.values())
# end class CrawlerVo

## --------------------------------------------------------------------------------------------------------------------
## Crawler white list data object
class CrawlerWhitelistData:
    def __init__(self) -> None:
        self.wh_data = {}
        self.wh_list = []
    
    def addWhiteListItem(self, sectionNameSrc, optionNameSrc, option_data) -> None:
        if sectionNameSrc and optionNameSrc and option_data:
            if option_data:
                for value in option_data:
                    self.wh_list.append(value)
            if sectionNameSrc not in self.wh_data:
                self.wh_data[sectionNameSrc] = dict({optionNameSrc:option_data})
            else:
                self.wh_data[sectionNameSrc].update(dict({optionNameSrc:option_data}))

    def __contains__(self, value) -> bool:
        for item in self.wh_list:
            if value.startswith(item):
                return True

# end class CrawlerWhitelistData

## --------------------------------------------------------------------------------------------------------------------