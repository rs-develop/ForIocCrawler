#!/usr/bin/python3

## --------------------------------------------------------------------------------------------------------------------

import csv # for csv export

from .crawlererr  import CrawlerExportError

## --------------------------------------------------------------------------------------------------------------------
## Export class for ioc crawler
class CrawlerExporter:

    ## export data to csv file
    def csvExport(exportFileNameSrc:str, exportListSrc:list, formatSrc:list):
        try:
            with open(exportFileNameSrc, 'w', newline='') as csvfile:
                
                # create csv writer
                fieldNames = formatSrc
                csvwriter = csv.DictWriter(csvfile, fieldnames=fieldNames, delimiter='|')
                csvwriter.writeheader()

                # get and write results
                for fileResult in exportListSrc:
                    tmpDict = {"file" : fileResult.path}
                    for ioc in fileResult.mResults:
                        tmpDict["ioc"] = ioc
                        for entry in fileResult.mResults[ioc]:
                            tmpDict["match"] = entry
                            for offset in fileResult.mResults[ioc][entry]:
                                tmpDict["offset"] = offset
                                printDict = {}
                                for field in fieldNames:
                                    # build dict for writing depending of the user selected columns
                                    printDict[field] = tmpDict[field]
                                # write data
                                csvwriter.writerow(printDict)
                            # end for offset
                        # end for entry
                    # end for ioc
                # end for fileResult
            # end try
                
        except Exception as e:
            raise CrawlerExportError(getattr(e, 'message', repr(e)))
    # end def csvExport

    ## export data
    def jsonExport(exportListSrc):
        CrawlerExportError("Not implemented.")

# end CrawlerExporter