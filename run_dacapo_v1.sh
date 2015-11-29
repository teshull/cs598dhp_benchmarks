#!/bin/bash

declare -a benchmarks=(
'antlr'
'batik'
'bloat'
'chart'
'eclipse'
'fop'
'hsqldb'
'jython'
'luindex'
'lusearch'
'pmd'
'sunflow'
'xalan'
'END'
)

BENCH_DIR=~/Dropbox/CS_598DHP/benchmarks/dacapo-2006-10-MR2.jar

run_on_benchmarks(){
    local count=0
    while [[ ${benchmarks[count]} != 'END' ]]
    do
        benchmark=${benchmarks[count]}
        echo "benchmark: $benchmark"
        #java -jar $BENCH_DIR -i $benchmark
        java -jar $BENCH_DIR -s small $benchmark
        count=$(( $count + 1 ))
    done

}

run_on_benchmarks
