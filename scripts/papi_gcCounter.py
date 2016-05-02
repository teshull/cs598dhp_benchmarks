import argparse
import re
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

args = dict()
data = dict()
origDir = os.getcwd()

#plt.style.use('ggplot')
## plt.style.use('grayscale')
## plt.style.use('fivethirtyeight')
#print plt.style.available


# containing data
gcInfo = re.compile('GC INFO -- Type: (Full|Young), ' +
                    'start: (\d+), finish: (\d+)')

# file name info stuff
filenameInfo = re.compile('(.+)-papi\.log')

# state information
threadNum = 0
sampleNum = 0
threadName = 0

gcData = list()
gcCollectionGCData = dict()
totalGCData = dict()
perPapiTotalGCData = dict()

gcCollectionTypes = ['serial_serial_gc', 'parallel_serial_gc',
                     'parallel_both_gc', 'conc_mark_sweep_gc', 'g1_gc']
currentGCPhase = "nothing"

def parseFilename(filename):
    result = fileNameInfo.match(filename)
    if result:
        return result.group(1)
    else:
        print "oops"
    return None
    sys.exit(1)


def readCommandline():
    global args
    parser = argparse.ArgumentParser(prog='Plot generator')
    parser.add_argument('folder', help='example')
    parser.add_argument('-allThreads', default='Yes', help='example')
    parser.add_argument('-papiType', default='L2', help='example')
    parser.add_argument('-output', help='output name')
    parser.add_argument('-colors', dest='colors', help='example')
    args = parser.parse_args()


def inclusiveRange(start, stop):
    return range(start, stop + 1)


def validThreadName(name):
    #I think I care about all threads during this time
    if args.allThreads == "Yes":
        return True

    #But also have this option
    mainThread = re.compile('(Main Thread)|(VM Thread)')
    garbageThreads = re.compile('GC Thread')
    if currentGCPhase == "serial_serial_gc":
        return mainThread.search(name)
    else:
        return garbageThreads.search(name)


def retrieveNumGCs(isYoung, gc_data, gc, bench):
    count = 0
    numCacheTypes = 0
    for key in gc_data.keys():
        #print key, gc, bench
        data = []
        try:
            data = gc_data[key][gc][bench]
            numCacheTypes += 1
        except KeyError:
            pass
        for i in range(len(data)):
            gcType = data[i][0]
            young = gcType == "Young"
            if young == isYoung:
                count += 1
    return float(count)/numCacheTypes


def printPapiOverallInfo():
    global currentGCPhase
    f = sys.stdout

    message = "\npapi **Overall Count**\n"
    f.write(message)
    gc_types = gcCollectionTypes
    f.write('gc_types')
    for key in gc_types:
        for x in range(0,3):
            f.write(' & ')
            f.write(key)
    f.write('\n')
    f.write('benchmarks')
    for key in gc_types:
        vals = ['young', 'full', 'total']
        for v in vals:
            f.write(' & ')
            f.write(v)
    f.write('\n')
    papiTypeKey = perPapiTotalGCData.keys()[0]
    benchmarks = perPapiTotalGCData[papiTypeKey][gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            young = retrieveNumGCs(True, perPapiTotalGCData, gc, bench)
            old = retrieveNumGCs(False, perPapiTotalGCData, gc, bench)
            total = young + old
            result = " & " + str(young) + " & " + str(old) + " & " + str(total)
            f.write(result)
        f.write('\n')
    f.write("\ndone\n")


def searchForMatch(line, query):
    result = query.search(line)
    if result:
        return result
    return None

def finishProcessingGC(gc_type):
    totalGCData[gc_type]= gcCollectionGCData


def finishProcessingFile(filename):
    result = searchForMatch(filename, filenameInfo)
    if result:
        name = result.group(1)
        gcCollectionGCData[name] = gcData
    else:
        print "unable to parse filename"
        sys.exit(1)

def finishProcessingCacheType(cache_type):
    perPapiTotalGCData[cache_type] = totalGCData

# this for all of the things that need to be initialize at the beginning
# of the file
def processNewFile(filename):
    global gcData
    gcData = list()

def processNewGC(gc_type):
    global gcCollectionGCData
    gcCollectionGCData = dict()


def processNewCacheType(cache_type):
    global totalGCData
    totalGCData = dict()
    pass


def performPapiEval(line):
    global gcData

    result = searchForMatch(line, gcInfo)
    if result:
        gcType = result.group(1)
        gcStart = int(result.group(2))
        gcFinish = int(result.group(3))
        gcData.append((gcType, gcStart, gcFinish))



def processData(line):
    performPapiEval(line)


def main():
    readCommandline()
    os.chdir(args.folder)
    parDir = os.getcwd()
    for cache_type in glob.glob("*"):
        print "cache type ", cache_type
        os.chdir(cache_type + "/max_size")
        parDir2 = os.getcwd()
        processNewCacheType(cache_type)
        for gc_type in glob.glob("*"):
            print "gc type ", gc_type
            os.chdir(gc_type)
            processNewGC(gc_type)
            for filename in glob.glob("*.log"):
                # print "filename: ", filename
                processNewFile(filename)
                with open(filename) as f:
                    for line in f:
                        processData(line)
                    #print "addresses seen" , len(addressesSeen)
                finishProcessingFile(filename)
            finishProcessingGC(gc_type)
            os.chdir(parDir2)
        # going back to parent dir
        finishProcessingCacheType(cache_type)
        os.chdir(parDir)
    #readCommandline()
    #print gcData
    #print "num samples ", finalNum
    #print totalGCData
    #print printPapiInfo()
    print printPapiOverallInfo()


if __name__ == '__main__':
    main()

# print data
