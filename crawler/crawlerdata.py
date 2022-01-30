#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

import os

## --------------------------------------------------------------------------------------------------------------------

## Crawler value object
#  The Crawler Value Object (CrawlerVo) represents all ioc matches for a file.
#  If the forioccrawler analysis more then one file objects, every file has its own "result" CrawlerVo object.
#
#  The following member variables are used in the data object:
#  - path - string with the path to the file object
#  - fileName - string with the file name
#  - mResult is a Dictionary for the match results, with the following structure
#    [KEY - IoC-Type] : VALUE - [KEY - Item : List of Offsets]
#  - mCount is 
class CrawlerVo:
    def __init__(self, filePathSrc:str) -> None:
        self.path     = filePathSrc
        self.fileName = os.path.basename(filePathSrc)
        self.mResults = {}
        self.mCount   = {}
    
    ## Adds matches to the structure
    #  iocTypeSrc - string - describes the ioc type
    #  matchDictSrc - dict - holds a set of matches and a list of offsets where the item was found
    #               -> Structure: [KEY - Match-Items : VALUE - List of Offsets]
    def addMatchResults(self, iocTypeSrc:str, matchDictSrc:dict) -> None:
        if matchDictSrc:
            # if ioc type is new, create it and add the values to the data object
            if iocTypeSrc not in self.mResults:
                self.mResults[iocTypeSrc] = matchDictSrc
                
                # add the count of the entries to the match count
                for item in matchDictSrc:
                    if iocTypeSrc in self.mCount.keys():
                        self.mCount[iocTypeSrc] = self.mCount[iocTypeSrc] + len(matchDictSrc[item])
                    else:
                        self.mCount[iocTypeSrc] = len(matchDictSrc[item])
            else:
                # if the ioc type already exists,
                for item in matchDictSrc:
                    # and if the current item already exists: extend the offset list
                    if item in self.mResults[iocTypeSrc]:
                        self.mResults[iocTypeSrc][item].extend(matchDictSrc[item])
                        self.mCount[iocTypeSrc] = self.mCount[iocTypeSrc] + len(matchDictSrc[item])
                    else:
                        # if the item is not in the data object, create it and store the values
                        self.mResults[iocTypeSrc][item] = matchDictSrc[item]
                        self.mCount[iocTypeSrc] = self.mCount[iocTypeSrc] + len(matchDictSrc[item])
                # end for
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