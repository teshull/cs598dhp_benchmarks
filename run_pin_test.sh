#!/bin/bash


PIN="/Users/tshull7/UIUC/research/pin-2.13-65163-clang.5.0-mac/pin"
PIN="/home/tshull226/Documents/research/pin-2.14-71313-gcc.4.4.7-linux/pin"
#export PINTOOL="/Users/tshull7/UIUC/research/pin-2.13-65163-clang.5.0-mac/source/tools/$pin_type/obj-intel64/${pin_type}.dylib"
PINTOOL="/Users/tshull7/UIUC/CS598DHP/project/trace_generator/obj-intel64/GCTracer.dylib"
PINTOOL="/home/tshull226/Documents/school/CS598DHP/project/git/trace_generator/obj-intel64/GCTracer.so"

export PINARGS=$pin_args

CACHE_SIZE=8*1024
CACHE_LINE_SIZE=64
CACHE_ASSOCIATIVITY=16


#$PIN -t $PINTOOL -o pinlog.log -- ls .
$PIN  -t $PINTOOL -mfs -cs -c $CACHE_SIZE -l $CACHE_LINE_SIZE -a $CACHE_ASSOCIATIVITY -o pinlog.log -- ls .
#$PIN  -t $PINTOOL -at -cs -o pinlog.log -- ls .
