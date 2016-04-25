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


fileNameInfo = re.compile('(.+)-pin\.log')
numAccesses = re.compile('Total Accesses: (\d+)')
numHits = re.compile('Total Hits: (\d+)')
numMisses = re.compile('Total Misses: (\d+)')
hitRate = re.compile('Hit Rate: ([0-9\.]+)')
missRate = re.compile('Miss Rate: ([0-9\.]+)')
memInfo = re.compile('(.+) (IFETCH|READ|WRITE)')
cacheType = re.compile('Cache Type: (.+)')
footprintInfo = re.compile(' *([a-z+]+) * (\d+) Bytes * ([0-9\.]+) KB')
gcSectionStart = re.compile('Start GC Section Info: Type = (FULL|YOUNG)')
gcSectionEnd = re.compile('End GC Section Info')
finalSection = re.compile('Start Overall Info')
cacheSection = re.compile('CACHE INFO')
footprintSection = re.compile('FOOTPRINT INFO')

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

# used for footprintInfo
# this is the current set
gcFootprintData = dict()
# overallFootprint = dict()


def parseFilename(filename):
    result = fileNameInfo.match(filename)
    if result:
        return result.group(1)
    else:
        print "oops"
    return None
    sys.exit(1)


def parseData(line, dictionary):
    # this is for the reading of file info
    category = 'memInfo'
    result = memInfo.match(line)
    if result:
        # print "matched on mem info ", result.group(1)
        value = int(result.group(1), 16)
        # print "int value ", value
        value = value & (~63)
        # print "masked value ", value
        valuesSeen[value] = 1
        return None

    category = 'accesses'
    result = numAccesses.match(line)
    if result:
        addElementToDictionary(dictionary, category,
                               result.group(1))
    category = 'hits'
    result = numHits.match(line)
    if result:
        addElementToDictionary(dictionary, category,
                               result.group(1))
    category = 'misses'
    result = numMisses.match(line)
    if result:
        addElementToDictionary(dictionary, category,
                               result.group(1))
    category = 'hit_rate'
    result = hitRate.match(line)
    if result:
        addElementToDictionary(dictionary, category,
                               result.group(1))


def parseAndAdd(expression, line, dictionary, name):
    result = expression.match(line)
    if result:
        addElementToDictionary(dictionary, name,
                               result.group(1))


def addElementToDictionary(dictionary, key, value):
    dictionary[key] = value


def readCommandline():
    global args
    parser = argparse.ArgumentParser(prog='Plot generator')
    parser.add_argument('folder', help='example')
    parser.add_argument('output', help='output name')
    parser.add_argument('-colors', dest='colors', help='example')
    args = parser.parse_args()


def printFormattedData():
    os.chdir('/home/tshull226/Documents/school/CS598DHP/project/git/benchmarks')
    f = open(args.output, 'w')
    columnOrder = ['accesses', 'hits', 'misses', 'hit_rate', 'memory_touched']
    f.write('benchname | accesses | hits | misses | hit rate | uniquemem\n')
    for filename in sorted(data.keys()):
        f.write(filename)
        for category in columnOrder:
            f.write(' | ')
            f.write(str(data[filename][category]))
        f.write("\n")


def main():
    global data, valuesSeen
    readCommandline()
    os.chdir(args.folder)
    for filename in glob.glob("*.log"):
        print filename
        valuesSeen = dict()
        name = parseFilename(filename)
        addElementToDictionary(data,name,dict())
        with open(filename) as f:
            for line in f:
                parseData(line, data[name])
        numBytes = len(valuesSeen.keys()) * 8
        addElementToDictionary(data[name], 'memory_touched', numBytes)
    print data
    printFormattedData()


def searchForMatch(line, query):
    result = query.search(line)
    if result:
        return result
    return None


# this for all of the things that need to be initialize at the beginning
# of the file
def processNewFile(filename):
    global addressesSeen
    addressesSeen = dict()


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


def tempmain():
    for filename in glob.glob("*.log"):
        print filename
        processNewFile(filename)
        with open(filename) as f:
            for line in f:
                processData(line)
            print "addresses seen" , len(addressesSeen)
    print overallCacheData
    print gcCacheData
    print gcFootprintData


if __name__ == '__main__':
    tempmain()

# print data
