#!/bin/bash

declare -a benchmarks=(
'avrora' 
'batik'
'eclipse'
'fop'
'h2'
'jython'
'luindex'
'lusearch'
'pmd'
'sunflow'
'tomcat'
'tradebeans'
'tradesoap'
'xalan'
'END'
)

#BENCH_DIR=/Users/tshull7/UIUC/CS598DHP/project/dacapo/2009/dacapo-9.12-bach.jar
BENCH_DIR=~/Dropbox/CS_598DHP/benchmarks/dacapo-9.12-bach.jar

run_on_benchmarks(){
    local count=0
    while [[ ${benchmarks[count]} != 'END' ]]
    do
        benchmark=${benchmarks[count]}
        echo "benchmark: $benchmark"
        #java -jar $BENCH_DIR $benchmark --information --size small
        java -jar $BENCH_DIR $benchmark --size small
        count=$(( $count + 1 ))
    done

}

run_on_benchmarks
