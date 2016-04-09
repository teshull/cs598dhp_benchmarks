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


numInst = re.compile('Number of Instructions: (\d+)')
numFTL = re.compile('Number of FTL Instructions: (\d+)')
typeCheckInfo = re.compile('TypeCheck\[(.+)\]= (\d+)')
fileNameInfo = re.compile('(.+)-pin\.log')
numAccesses = re.compile('Total Accesses: (\d+)')
numHits = re.compile('Total Hits: (\d+)')
numMisses = re.compile('Total Misses: (\d+)')
hitRate = re.compile('Hit Rate: ([0-9\.]+)')
memInfo = re.compile('(.+) (READ|WRITE)')

valuesSeen = dict()




def initializeData(dictionary):
    addElementToDictionary(dictionary, "ftl_count", 0)
    addElementToDictionary(dictionary, "inst_count", 0)


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
        # initializeData(data[filename])
        with open(filename) as f:
            for line in f:
                parseData(line, data[name])
        numBytes = len(valuesSeen.keys()) * 64
        addElementToDictionary(data[name], 'memory_touched', numBytes)
    print data
    printFormattedData()


if __name__ == '__main__':
    main()

# print data
