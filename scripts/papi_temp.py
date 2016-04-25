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


# file name info stuff
fileNameInfo = re.compile('(.+)-pin\.log')

# containing data
eventInfo = re.compile('Event (\d+) \((.+)\): ([0-9.]+)')
gcInfo = re.compile('GC INFO -- Type: (Full|Young), ' +
                    'start: (\d+), finish: (\d+)')

# containing state info
samplingRate = re.compile('Sample Rate: (\d+)')
samplingStart = re.compile('Start Sample Num (\d+)')
finalStart = re.compile('Final Results')
threadInfoName = re.compile('Thread Name: (.+)')
threadInfoNum = re.compile('Thread Num: (.+)')

# state information
threadNum = 0
sampleNum = 0
threadName = 0
finalNum = 0

threadData = dict()
gcData = list()

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
    global threadData, gcData
    threadData = dict()
    gcData = list()


def performPapiEval(line):
    global threadData, gcData
    result = searchForMatch(line, eventInfo)
    if result:
        # papiEntryNum = result.group(1)
        papiName = result.group(2)
        papiValue = result.group(3)
        threadData[sampleNum][threadName][papiName] = float(papiValue)

    result = searchForMatch(line, gcInfo)
    if result:
        gcType = result.group(1)
        gcStart = int(result.group(2))
        gcFinish = int(result.group(3))
        gcData.append((gcType, gcStart, gcFinish))


def checkForTransition(line):
    global sampleNum, finalNum, threadNum, threadName
    global threadData
    result = searchForMatch(line, samplingStart)
    if result:
        sampleNum = int(result.group(1))
        threadData[sampleNum] = dict()

    result = searchForMatch(line, finalStart)
    if result:
        sampleNum = sampleNum + 1
        finalNum = sampleNum
        threadData[finalNum] = dict()

    result = searchForMatch(line, threadInfoNum)
    if result:
        threadNum = int(result.group(1))

    result = searchForMatch(line, threadInfoName)
    if result:
        threadName = result.group(1)
        threadData[sampleNum][threadName] = dict()


def processData(line):
    checkForTransition(line)
    performPapiEval(line)


def tempmain():
    for filename in glob.glob("*.txt"):
        print filename
        processNewFile(filename)
        with open(filename) as f:
            for line in f:
                processData(line)
        print threadData
        print gcData
        print "num samples ", finalNum


if __name__ == '__main__':
    tempmain()

# print data
