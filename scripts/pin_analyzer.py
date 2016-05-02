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


numAccesses = re.compile('Total Accesses: (\d+)')
numHits = re.compile('Total Hits: (\d+)')
numMisses = re.compile('Total Misses: (\d+)')
hitRate = re.compile('Hit Rate: (.+)')
missRate = re.compile('Miss Rate: (.+)')
memInfo = re.compile('(.+) (IFETCH|READ|WRITE)')
cacheType = re.compile('Cache Type: (.+)')
footprintInfo = re.compile(' *([a-z+]+) * (\d+) Bytes * ([0-9\.]+) KB')
gcSectionStart = re.compile('Start GC Section Info: Type = (FULL|YOUNG)')
gcSectionEnd = re.compile('End GC Section Info')
finalSection = re.compile('Start Overall Info')
cacheSection = re.compile('CACHE INFO')
footprintSection = re.compile('FOOTPRINT INFO')

filenameInfo = re.compile('(.+)-pin\.log')

# options are mem info, cache info, footprint info
info_type = 'mem info'
# options are Loads, Stores, Instructions, Everything
cache_type = 'Loads'
# options are mem_eval, gc, overall
stage = 'mem_eval'

# used for reading the memory values
# TODO will have to re-initialize this occassionally
chunksize = 64
addressesSeen = dict()

# used for cache info
# this changes occassionally
gcCount = 0

overallCacheData = dict()
gcCacheData = dict()
gcFootprintData = dict()

totalOverallCacheData = dict()
totalGcCacheData = dict()
totalGcFootprintData =dict()
totalFootprintSize =dict()

gcCollectionOverallCacheData = dict()
gcCollectionGcCacheData = dict()
gcCollectionGcFootprintData =dict()
gcCollectionFootprintSize = dict()

gcCollectionTypes = ['serial_serial_gc', 'parallel_both_gc']

# used for footprintInfo
# this is the current set
# overallFootprint = dict()



def readCommandline():
    global args
    parser = argparse.ArgumentParser(prog='Plot generator')
    parser.add_argument('folder', help='example')
    parser.add_argument('-output', help='output name')
    parser.add_argument('-colors', dest='colors', help='example')
    args = parser.parse_args()


def searchForMatch(line, query):
    result = query.search(line)
    if result:
        return result
    return None


def finishProcessingGC(gc_type):
    totalOverallCacheData[gc_type] = gcCollectionOverallCacheData
    totalGcCacheData[gc_type] = gcCollectionGcCacheData
    totalGcFootprintData[gc_type] = gcCollectionGcFootprintData
    totalFootprintSize[gc_type] = gcCollectionFootprintSize


def finishProcessingFile(filename):
    global gcCollectionOverallCacheData
    global gcCollectionGcCacheData
    global gcCollectionGcFootprintData
    global gcCollectionFootprintSize
    result = searchForMatch(filename, filenameInfo)
    if result:
        name = result.group(1)
        gcCollectionOverallCacheData[name] = overallCacheData
        gcCollectionGcCacheData[name] = gcCacheData
        gcCollectionGcFootprintData[name] = gcFootprintData
        gcCollectionFootprintSize[name] = len(addressesSeen)
    else:
        print "unable to parse filename"
        sys.exit(1)


# this for all of the things that need to be initialize at the beginning
# of the file
def processNewFile(filename):
    global overallCacheData, gcCacheData, gcFootprintData
    global info_type, cache_type, stage
    #clearing per gc info
    addressesSeen.clear()
    overallCacheData = {}
    gcCacheData = {}
    gcFootprintData = {}
    # resetting the fsm state
    info_type = 'mem info'
    cache_type = 'Loads'
    stage = 'mem_eval'

def processNewGC(gc_type):
    global gcCollectionOverallCacheData, gcCollectionGCCacheData
    global gcCollectionGcFootprintData
    gcCollectionOverallCacheData = {}
    gcCollectionGcCacheData = {}
    gcCollectionGcFootprintData = {}


def performMemEval(line):
    global addressesSeen
    result = searchForMatch(line, memInfo)
    if result:
        # print result.group(1)
        value = int(result.group(1), 16)
        # print "int value ", value
        # TODO need to make sure this is correct
        value = value & (~(chunksize - 1))
        # print "masked value ", value
        addressesSeen[value] = 1


def getCacheDict():
    global gcCacheData, overallCacheData

    temp_dict = None

    if stage == 'gc':
        temp_dict = gcCacheData[gcCount]
    elif stage == 'overall':
        temp_dict = overallCacheData
    else:
        print "problem in getCacheDict"
        sys.exit(1)

    if cache_type not in temp_dict.keys():
        temp_dict[cache_type] = dict()

    return temp_dict[cache_type]


def performCacheEval(line):
    global cache_type
    cacheData = getCacheDict()

    result = searchForMatch(line, cacheType)
    if result:
        cache_type = result.group(1)

    category = 'accesses'
    result = searchForMatch(line, numAccesses)
    if result:
        cacheData[category] = result.group(1)

    category = 'hits'
    result = searchForMatch(line, numHits)
    if result:
        cacheData[category] = result.group(1)

    category = 'misses'
    result = searchForMatch(line, numMisses)
    if result:
        cacheData[category] = result.group(1)

    category = 'hit_rate'
    result = searchForMatch(line, hitRate)
    if result:
        cacheData[category] = result.group(1)


def retrieveGCCount(isFull, data):
    count = 0
    expectedType = ("FULL" if isFull else "YOUNG")
    for key in data.keys():
        gcEntry = data[key]
        if gcEntry["gc_type"] == expectedType:
            count += 1
    return count


def retrieveFootprint(isFull, data):
    sumFootprint = float(0)
    numValues = 0
    expectedType = ("FULL" if isFull else "YOUNG")
    for key in data.keys():
        gcEntry = data[key]
        if gcEntry["gc_type"] != expectedType:
            continue
        individualSum = float(0)
        for keyTwo in gcEntry.keys():
            if keyTwo == "gc_type":
                continue
            individualSum += float(gcEntry[keyTwo])
        sumFootprint += individualSum
        numValues += 1
    result = "N/A"
    if numValues != 0:
        result = sumFootprint / numValues
    return result


def printGCCountData():
    f = sys.stdout
    f.write('\ngc count  info\n')
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
    benchmarks = totalFootprintSize[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            young = retrieveGCCount(False, totalGcFootprintData[gc][bench])
            old = retrieveGCCount(True, totalGcFootprintData[gc][bench])
            total = young + old
            result = " & " + str(young) + " & " + str(old) + " & " + str(total)
            f.write(result)
        f.write('\n')


def printFootprintInfo():
    f = sys.stdout
    f.write('\nmemory footprint info\n')
    gc_types = gcCollectionTypes
    f.write('gc_types')
    for key in gc_types:
        for x in range(0,3):
            f.write(' & ')
            f.write(key)
    f.write('\n')
    f.write('benchmarks')
    for key in gc_types:
        vals = ['young', 'full', 'overall']
        for v in vals:
            f.write(' & ')
            f.write(v)
    f.write('\n')
    benchmarks = totalFootprintSize[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            overall = float(chunksize) * totalFootprintSize[gc][bench]
            young = retrieveFootprint(False, totalGcFootprintData[gc][bench])
            old = retrieveFootprint(True, totalGcFootprintData[gc][bench])
            # TODO probably convert bytes to KBs or MBs here
            overall = overall if float(overall) != 0.0 else "N/A"
            result = " & " + str(young) + " & " + str(old) + " & " + str(overall)
            f.write(result)
        f.write('\n')


def retrieveCache(isFull, data):
    sumFootprint = float(0)
    numValues = 0
    expectedType = ("FULL" if isFull else "YOUNG")
    for key in data.keys():
        gcEntry = data[key]
        if gcEntry["gc_type"] != expectedType:
            continue
        individualSum = gcEntry['Everything']['hit_rate']
        sumFootprint += float(individualSum)
        numValues += 1
    result = "N/A"
    if numValues != 0:
        result = sumFootprint / numValues
    return result


def printCacheInfo():
    f = sys.stdout
    f.write('\ncache hit rate info\n')
    gc_types = gcCollectionTypes
    f.write('gc_types')
    for key in gc_types:
        for x in range(0,3):
            f.write(' & ')
            f.write(key)
    f.write('\n')
    f.write('benchmarks')
    for key in gc_types:
        vals = ['young', 'full', 'overall']
        for v in vals:
            f.write(' & ')
            f.write(v)
    f.write('\n')
    benchmarks = totalFootprintSize[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            # TODO need to finish this
            # print "gc : ", gc, " bench: ", bench
            overall = totalOverallCacheData[gc][bench]['Everything']['hit_rate']
            if overall == "-nan":
                overall = "N/A"
            young = retrieveCache(False, totalGcCacheData[gc][bench])
            old = retrieveCache(True, totalGcCacheData[gc][bench])
            # TODO probably convert bytes to KBs or MBs here
            result = " & " + str(young) + " & " + str(old) + " & " + str(overall)
            f.write(result)
        f.write('\n')




def getFootprintDict():
    global gcFootprintData
    return gcFootprintData[gcCount]


def performFootprintEval(line):
    footprintData = getFootprintDict()
    category = ''
    result = searchForMatch(line, footprintInfo)
    if result:
        # the type
        key = result.group(1)
        # the amount of bytes
        value = result.group(2)
        footprintData[key] = value

def checkForTransition(line):
    global info_type, stage
    global cacheData, footprintData
    global gcCacheData, gcFootprintData, gcCount, overallCacheData
    result = searchForMatch(line, gcSectionStart)
    if result:
        stage = 'gc'
        gcCacheData[gcCount] = dict()
        gcFootprintData[gcCount] = dict()
        gc_type = result.group(1)
        gcCacheData[gcCount]['gc_type'] = gc_type
        gcFootprintData[gcCount]['gc_type'] = gc_type

    if searchForMatch(line, gcSectionEnd):
        stage = 'mem_eval'
        info_type = 'mem info'
        gcCount += 1

    if searchForMatch(line, finalSection):
        stage = 'overall'
        info_type = 'cache info'

    if searchForMatch(line, cacheSection):
        info_type = 'cache info'

    if searchForMatch(line, footprintSection):
        info_type = 'footprint info'


def getEvalRoutine():
    return {
        'mem info': performMemEval,
        'cache info': performCacheEval,
        'footprint info': performFootprintEval
    }[info_type]


def processData(line):
    checkForTransition(line)
    routine = getEvalRoutine()
    routine(line)


def main():
    readCommandline()
    os.chdir(args.folder)
    parDir = os.getcwd()
    for gc_type in glob.glob("*"):
        print "gc type ", gc_type
        os.chdir(gc_type)
        processNewGC(gc_type)
        for filename in glob.glob("*.log"):
            print "filename: ", filename
            processNewFile(filename)
            with open(filename) as f:
                for line in f:
                    processData(line)
                #print "addresses seen" , len(addressesSeen)
            finishProcessingFile(filename)
        finishProcessingGC(gc_type)
        # going back to parent dir
        os.chdir(parDir)
    print totalOverallCacheData
    print totalGcCacheData
    #print totalGcFootprintData
    #print totalFootprintSize
    printGCCountData()
    printFootprintInfo()
    printCacheInfo()


if __name__ == '__main__':
    main()

# print data
