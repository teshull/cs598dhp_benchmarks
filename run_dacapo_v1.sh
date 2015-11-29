#!/bin/bash

declare -a benchmarks=(
'antlr'
#'batik' #this one throws an error
'bloat'
'chart'
'eclipse'
'fop'
'hsqldb'
'jython'
'luindex'
'lusearch'
'pmd'
#'sunflow' # this one throws an error
'xalan'
'END'
)


BENCH_DIR=~/Dropbox/CS_598DHP/benchmarks/dacapo-2006-10-MR2.jar
BENCHMARK_ARGS=""
JAVA_ARGS=""
LOG_DIR="empty"

#java -jar $BENCH_DIR -h
#exit 0

run_on_benchmarks(){
    local count=0
    while [[ ${benchmarks[count]} != 'END' ]]
    do
        benchmark=${benchmarks[count]}
        echo "benchmark: $benchmark"
        if [[ "$LOG_DIR" != "empty" ]]; then
            JAVA_ARGS="${JAVA_ARGS} -Xloggc:${LOG_DIR}/$benchmark-gc.log"
        fi
        #java -jar $BENCH_DIR -i $benchmark
        java $JAVA_ARGS -jar $BENCH_DIR $BENCHMARK_ARGS $benchmark
        count=$(( $count + 1 ))
    done

}

#this is what actually runs
while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        --small_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s small"
            ;;
        --large_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s large"
            ;;
        --default_data)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -s default"
            ;;
        --gc_log)
            LOG_DIR=$2
            shift
            ;;
        --detailed_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+PrintGCDetails -XX:+PrintGCDateStamps"
            ;;
        --serial_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseSerialGC"
            ;;
        --show_info)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -i"
            ;;
        *)
            echo "unknown option"
            exit -1
            ;;
    esac
    #moving onto next argument
    shift
done

run_on_benchmarks
