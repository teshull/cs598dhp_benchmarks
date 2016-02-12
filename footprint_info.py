import argparse
import re
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

args = dict()
data = dict()
origDir = os.getcwd()

plt.style.use('ggplot')
# plt.style.use('grayscale')
# plt.style.use('fivethirtyeight')
print plt.style.available


numInst = re.compile('Number of Instructions: (\d+)')
numFTL = re.compile('Number of FTL Instructions: (\d+)')
typeCheckInfo = re.compile('TypeCheck\[(.+)\]= (\d+)')
fileNameInfo = re.compile('.*___(.+)\.log')


def drawMultiData():
    numPoints = len(data)
    widthNum = len(data[data.keys()[0]])
    f, ax = plt.subplots()
    ax.set_title("Something")
    x = np.arange(numPoints)
    y = dict()

    labels = []
    for i in range(0, widthNum):
        y[i] = []

    for filename in data.keys():
        i = 0
        labels.append(filename)
        for category in data[filename].keys():
            y[i].append(int(data[filename][category]))
            i += 1

    width = 0
    color_cycle_length = len(plt.rcParams['axes.color_cycle'])
    for i in range(0, widthNum):
        ax.bar(x + width, y[i], .25,
               color=plt.rcParams['axes.color_cycle'][i % color_cycle_length])
        width += .25

    ax.set_xticks(x + .25)
    ax.set_xticklabels(labels, rotation='vertical')
    os.chdir(origDir)
    # plt.savefig(args.output + '.ps')
    plt.show()


def drawStackedData():
    numPoints = len(data)
    stackNum = len(data[data.keys()[0]])
    f, ax = plt.subplots()
    ax.set_title("Something")
    x = np.arange(numPoints)
    y = dict()
    plots = dict()

    labels = []
    for i in range(0, stackNum):
        y[i] = []


    for filename in sorted(data.keys()):
        i = 0
        labels.append(parseFilename(filename))
        for category in sorted(data[filename].keys()):
            y[i].append(int(data[filename][category]))
            i += 1

    # this for finding the bottom
    btm = dict()
    total = [0] * numPoints
    for i in range(0, stackNum):
        btm[i] = total
        total = [first + second for (first, second) in zip(total, y[i])]

    # this is for drawing
    width = .5
    colors = plt.get_cmap('jet')(np.linspace(0, 1.0, stackNum))
    # color_cycle_length = len(plt.rcParams['axes.color_cycle'])
    for i in range(0, stackNum):
        plots[i] = ax.bar(x, y[i], width, bottom=btm[i],
               color=colors[i])

    ax.set_xticks(x + width/2.)
    # ax.set_xticklabels(labels, rotation=-45)
    ax.set_xticklabels(labels, rotation='vertical')

    # this is for the legend
    plotList = []
    for i in range(0, stackNum):
        plotList.append(plots[i][0])
    plt.legend(plotList, sorted(data[data.keys()[0]].keys()))

    # now am drawing the plot
    plt.show()


def drawMultiStackedData():
    numPoints = len(data)
    widthNum = len(data[data.keys()[0]])
    stackNum = len(data[data.keys()[0]][data[data.keys()[0]].keys()[0]])
    f, ax = plt.subplots()
    ax.set_title("Something")
    x = np.arange(numPoints)

    labels = []
    y = dict()
    btm = dict()
    for i in range(0, widthNum):
        y[i] = dict()
        btm[i] = dict()
        for j in range(0, stackNum):
            y[i][j] = []

    i = 0
    for tickName in data.keys():
        labels.append(tickName)
        for test in data[tickName].keys():
            j = 0
            for category in data[tickName][test].keys():
                y[i][j].append(int(data[tickName][test][category]))
                j += 1
        i += 1

    for i in range(0, widthNum):
        total = [0] * numPoints
        for j in range(0, stackNum):
            btm[i][j] = total
            total = [first + second for (first, second) in zip(total, y[i][j])]

    width = 0
    color_cycle_length = len(plt.rcParams['axes.color_cycle'])
    for i in range(0, widthNum):
        for j in range(0, stackNum):
            ax.bar(x + width, y[i][j], .25, bottom=btm[i][j],
                   color=plt.rcParams['axes.color_cycle'][j % color_cycle_length])

        width += .25  # this number is going to have to change

    ax.set_xticks(x + width/2.)
    ax.set_xticklabels(labels, rotation='vertical')
    plt.show()


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



def parseData(line, dictionary):
    result = typeCheckInfo.match(line)
    if result:
        addElementToDictionary(dictionary, result.group(1),
                               result.group(2))


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


def main():
    global data
    readCommandline()
    os.chdir(args.folder)
    for filename in glob.glob("*.log"):
        addElementToDictionary(data, filename, dict())
        # initializeData(data[filename])
        with open(filename) as f:
            for line in f:
                parseData(line, data[filename])
    # drawMultiData()
    drawStackedData()
    print data


if __name__ == '__main__':
    main()

# print data
