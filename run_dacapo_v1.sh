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


benchmarks=(
'xalan'
'END'
)

BENCH_DIR=~/Dropbox/CS_598DHP/benchmarks/dacapo-2006-10-MR2.jar
BENCHMARK_ARGS=""
JAVA_ARGS=""
LOG_DIR="empty"

PIN_LOG_DIR="empty"
DO_PIN="no"
PIN="/Users/tshull7/UIUC/research/pin-2.13-65163-clang.5.0-mac/pin"
PIN="/home/tshull226/Documents/research/pin-2.14-71313-gcc.4.4.7-linux/pin"
PINTOOL="/Users/tshull7/UIUC/CS598DHP/project/trace_generator/obj-intel64/GCTracer.dylib"
PINTOOL="/home/tshull226/Documents/school/CS598DHP/project/git/trace_generator/obj-intel64/GCTracer.so"

CACHE_SIZE=$((8*1024))
CACHE_LINE_SIZE=64
CACHE_ASSOCIATIVITY=16

PINARGS=" -cs -at -c $CACHE_SIZE -l $CACHE_LINE_SIZE -a $CACHE_ASSOCIATIVITY"

#java -jar $BENCH_DIR -h
#exit 0

unamestr=`uname`
platform='unknown'


if [[ "$unamestr" == 'Linux' ]]; then
    platform='linux'
elif [[ "$unamestr" == 'Darwin' ]]; then
    platform='mac'
fi

case $platform in
    'linux')
        JAVA_PATH="/home/tshull226/Documents/school/DHP_CS598/jdk8u60/build/linux-x86_64-normal-server-release/jdk/bin/java"
        #JAVA_PATH="/home/tshull226/Documents/school/DHP_CS598/hotspot_debug/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
        #JAVA_PATH="/home/tshull226/Documents/school/DHP_CS598/jdk8u60/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
        ;;
    'mac')
        JAVA_PATH="java"
        ;;
esac

run_on_benchmarks(){
    local count=0
    while [[ ${benchmarks[count]} != 'END' ]]
    do
        EXEC_COMMAND=""
        benchmark=${benchmarks[count]}
        echo "benchmark: $benchmark"
        if [[ "$DO_PIN" != "no" ]]; then
            EXEC_COMMAND="$PIN -t $PINTOOL $PINARGS"
            if [[ "$PIN_LOG_DIR" != "empty" ]]; then
                EXEC_COMMAND="$EXEC_COMMAND -o ${PIN_LOG_DIR}/$benchmark-pin.log --"
            else
                EXEC_COMMAND="$EXEC_COMMAND -o pinlog.log --"
            fi
        fi
        EXEC_COMMAND="$EXEC_COMMAND $JAVA_PATH $JAVA_ARGS"
        if [[ "$LOG_DIR" != "empty" ]]; then
            EXEC_COMMAND="$EXEC_COMMAND -Xloggc:${LOG_DIR}/$benchmark-gc.log"
        fi
        #java -jar $BENCH_DIR -i $benchmark
        #$JAVA_PATH -version
        #$JAVA_PATH $JAVA_ARGS -jar $BENCH_DIR $BENCHMARK_ARGS $benchmark
        EXEC_COMMAND="$EXEC_COMMAND -jar $BENCH_DIR $BENCHMARK_ARGS $benchmark"
        echo "$EXEC_COMMAND"
        $EXEC_COMMAND
        count=$(( $count + 1 ))
    done

}

#this is what actually runs
while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        --debug)
            JAVA_PATH="gdb -x gdb_commands.txt --args /home/tshull226/Documents/school/DHP_CS598/jdk8u60/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
            #JAVA_PATH="gdb -x gdb_commands.txt --args /home/tshull226/Documents/school/DHP_CS598/hotspot_debug/build/linux-x86_64-normal-server-slowdebug/jdk/bin/java"
            ;;
        --mark_gc_phases)
            JAVA_ARGS="$JAVA_ARGS -XX:+MarkGCStartEnd"
            ;;
        --send_markers_to_pin)
            JAVA_ARGS="$JAVA_ARGS -XX:+SendMessagesToPin"
            ;;
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
        --pin)
            #JAVA_PATH="$PIN -t $PINTOOL $PINARGS -- $JAVA_PATH"
            DO_PIN="yes"
            ;;
        --pin_log)
            PIN_LOG_DIR=$2
            shift
            ;;
        --detailed_gc)
            #JAVA_ARGS="${JAVA_ARGS} -XX:+PrintGCDetails -XX:+PrintGCDateStamps"
            JAVA_ARGS="${JAVA_ARGS} -XX:+PrintGCDetails"
            ;;
        --serial_serial_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseSerialGC"
            ;;
        --parallel_both_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseParallelGC"
            ;;
        --parallel_serial_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseParallelGC -XX:-UseParallelOldGC"
            ;;
        --conc_mark_sweep_gc)
            #the useparnewgc is on by default
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseParNewGC -XX:+UseConcMarkSweepGC"
            ;;
        --g1_gc)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UseG1GC"
            ;;
        --papi_monitor)
            JAVA_ARGS="${JAVA_ARGS} -XX:+UsePapiCounters -XX:PapiEventFile=/home/tshull226/Documents/school/DHP_CS598/benchmarks/papi_options.txt"
            #JAVA_ARGS="${JAVA_ARGS} -XX:+UsePapiCounters"
            ;;
        --papi_result)
            JAVA_ARGS="${JAVA_ARGS} -XX:PapiResultFile=$2"
            shift
            ;;
        --papi_sampling)
            JAVA_ARGS="${JAVA_ARGS} -XX:+PerformPapiSampling"
            ;;
        --papi_sampling_rate)
            JAVA_ARGS="${JAVA_ARGS} -XX:PapiSamplingInterval=$2"
            shift
            ;;
        --show_info)
            BENCHMARK_ARGS="$BENCHMARK_ARGS -i"
            ;;
        *)
            echo "unknown option: $key"
            exit -1
            ;;
    esac
    #moving onto next argument
    shift
done

run_on_benchmarks
