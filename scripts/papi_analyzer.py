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
eventInfo = re.compile('Event (\d+) \((.+)\): ([0-9.]+)')
gcInfo = re.compile('GC INFO -- Type: (Full|Young), ' +
                    'start: (\d+), finish: (\d+)')

# containing state info
samplingRate = re.compile('Sample Rate: (\d+)')
samplingStart = re.compile('Start Sample Num (\d+)')
finalStart = re.compile('Final Results')
threadInfoName = re.compile('Thread Name: (.+)')
threadInfoNum = re.compile('Thread Num: (.+)')

deadThreadStart = re.compile('Starting Dead Threads Report')
deadThreadEnd = re.compile('End Dead Threads Report')

# file name info stuff
filenameInfo = re.compile('(.+)-papi\.log')

# state information
threadNum = 0
sampleNum = 0
threadName = 0

threadData = dict()
gcData = list()

totalThreadData = dict()
totalGCData = dict()

gcCollectionThreadData = dict()
gcCollectionGCData = dict()

gcCollectionTypes = ['serial_serial_gc', 'parallel_both_gc']
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


def retrieveIL1Rate(data):
    misses = float(data['ICACHE:MISSES'])
    hits = float(data['ICACHE:HIT'])
    accesses = misses + hits
    # print "m ", misses, "\ta ", accesses
    return(hits, accesses)


def retrieveDL1Rate(data):
    ld = float(data['perf::L1-DCACHE-LOADS'])
    ld_miss = float(data['perf::L1-DCACHE-LOAD-MISSES'])
    st = float(data['perf::L1-DCACHE-STORES'])
    st_miss = float(data['perf::L1-DCACHE-STORE-MISSES'])
    # print "m ", misses, "\ta ", accesses
    accesses = ld + st
    misses = ld_miss + st_miss
    return(accesses-misses, accesses)


def retrieveL2Rate(data):
    misses = float(data['L2_RQSTS:ALL_DEMAND_MISS'])
    accesses = float(data['L2_RQSTS:ALL_DEMAND_REFERENCES'])
    # print "m ", misses, "\ta ", accesses
    return(accesses-misses, accesses)


def retrieveLLCRate(data):
    misses = float(data['ix86arch::LLC_MISSES'])
    accesses = float(data['ix86arch::LLC_REFERENCES'])
    return(accesses-misses, accesses)


def retrieveRates(data):
    return{
        'IL1': retrieveIL1Rate,
        'DL1': retrieveIL1Rate,
        'L2': retrieveL2Rate,
        'LLC': retrieveLLCRate
    }[args.papiType](data)


def getSampleRates(sample_num, thread_data):
    thread_accesses = 0.0
    thread_hits = 0.0
    for thread_name in thread_data[sample_num].keys():
        if validThreadName(thread_name):
            (hits, accesses) = retrieveRates(thread_data[sample_num][thread_name])
            thread_hits += hits
            thread_accesses += accesses
    return (thread_hits, thread_accesses)

def retrieveGCSamples(duringGC, thread_data, gc_data):
    youngGCSamples = set()
    fullGCSamples = set()
    overallGCSamples = set()
    # figuring out which samples are relevant
    for i in range(len(gc_data)):
        (gcType, start, end) = gc_data[i]
        if duringGC:
            for j in inclusiveRange(start, end):
                overallGCSamples.add(j)
                if gcType == "Young":
                    youngGCSamples.add(j)
                else:
                    fullGCSamples.add(j)
        else:
            for j in inclusiveRange(end+1, end+2):
                overallGCSamples.add(j)
                if gcType == "Young":
                    youngGCSamples.add(j)
                else:
                    fullGCSamples.add(j)
    # going through the samples to get the average hit rates
    sampleSets = (youngGCSamples, fullGCSamples, overallGCSamples)
    total_hits = [0.0,0.0,0.0]
    total_samples = [0,0,0]
    for i in range(len(thread_data) - 2):
        previous = (0.0, 0.0) if i == 0 else getSampleRates(i-1, thread_data)
        current = getSampleRates(i, thread_data)
        #calculating the accesses for this sample
        thread_hits = current[0] - previous[0]
        thread_accesses = current[1] - previous[1]
        # adding this sample (if there is one) to the proper sets
        if thread_accesses != 0.0:
            hit_rate = thread_hits/thread_accesses*100.0
            for j in range(3):
                if i in sampleSets[j]:
                    total_samples[j] += 1
                    total_hits[j] += hit_rate
    results = ["N/A", "N/A", "N/A"]
    for i in range(3):
        if total_samples[i] != 0:
            results[i] = total_hits[i]/total_samples[i]
    return results


def printPapiHeader(f):
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


def printPapiInfo():
    global currentGCPhase
    f = sys.stdout

    message = "\npapi **During GC** info type: " + args.papiType + "\n"
    f.write(message)
    printPapiHeader(f)
    gc_types = gcCollectionTypes
    benchmarks = totalThreadData[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            currentGCPhase = gc
            info = retrieveGCSamples(True, totalThreadData[gc][bench], totalGCData[gc][bench])
            for i in range(len(info)):
                f.write(' & ')
                f.write(str(info[i]))
        f.write('\n')
    f.write("\ndone\n")

    message = "\npapi **After GC** info type: " + args.papiType + "\n"
    f.write(message)
    printPapiHeader(f)
    gc_types = gcCollectionTypes
    benchmarks = totalThreadData[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            currentGCPhase = gc
            info = retrieveGCSamples(True, totalThreadData[gc][bench], totalGCData[gc][bench])
            for i in range(len(info)):
                f.write(' & ')
                f.write(str(info[i]))
        f.write('\n')
    f.write("\ndone\n")


def retrieveOverallCount(thread_data, gc_data):
    length = len(thread_data)
    thread_accesses = 0.0
    thread_hits = 0.0
    for i in range(length - 2, length):
        for thread_name in thread_data[i].keys():
            if validThreadName(thread_name):
                (hits, accesses) = retrieveRates(thread_data[i][thread_name])
                thread_hits += hits
                thread_accesses += accesses
    hit_rate = 0.0 if thread_accesses == 0 else thread_hits/thread_accesses*100.0
    return hit_rate


def printPapiOverallInfo():
    global currentGCPhase
    f = sys.stdout

    message = "\npapi **Overall** info type: " + args.papiType + "\n"
    f.write(message)
    gc_types = gcCollectionTypes
    f.write('benchmarks')
    for key in gc_types:
        f.write(' & ')
        f.write(key)
    f.write('\n')
    benchmarks = totalThreadData[gc_types[0]].keys()
    for bench in sorted(benchmarks):
        f.write(bench)
        for gc in gc_types:
            currentGCPhase = gc
            overall = retrieveOverallCount(totalThreadData[gc][bench], totalGCData[gc][bench])
            f.write(' & ')
            f.write(str(overall))
        f.write('\n')
    f.write("\ndone\n")


def searchForMatch(line, query):
    result = query.search(line)
    if result:
        return result
    return None

def finishProcessingGC(gc_type):
    totalThreadData[gc_type] = gcCollectionThreadData
    totalGCData[gc_type]= gcCollectionGCData


def finishProcessingFile(filename):
    result = searchForMatch(filename, filenameInfo)
    if result:
        name = result.group(1)
        gcCollectionThreadData[name] = threadData
        gcCollectionGCData[name] = gcData
    else:
        print "unable to parse filename"
        sys.exit(1)

# this for all of the things that need to be initialize at the beginning
# of the file
def processNewFile(filename):
    global threadData, gcData
    threadData = dict()
    gcData = list()

def processNewGC(gc_type):
    global gcCollectionThreadData
    global gcCollectionGCData
    gcCollectionThreadData = dict()
    gcCollectionGCData = dict()


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
    global sampleNum, threadNum, threadName
    global threadData
    result = searchForMatch(line, samplingStart)
    if result:
        sampleNum = int(result.group(1))
        threadData[sampleNum] = dict()

    result = searchForMatch(line, deadThreadStart)
    if result:
        sampleNum = sampleNum + 1
        threadData[sampleNum] = dict()

    result = searchForMatch(line, finalStart)
    if result:
        sampleNum = sampleNum + 1
        threadData[sampleNum] = dict()

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


def main():
    readCommandline()
    os.chdir(args.folder)
    parDir = os.getcwd()
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
        # going back to parent dir
        os.chdir(parDir)
    #readCommandline()
    #print threadData
    #print gcData
    #print "num samples ", finalNum
    #print totalThreadData
    #print totalGCData
    print printPapiInfo()
    print printPapiOverallInfo()
    #print totalThreadData["serial_serial_gc"]["xalan"][3]


if __name__ == '__main__':
    main()

# print data
