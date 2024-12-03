#!/usr/bin/bash

PROTEOME=$1
OUT=$2
SP=${PROTEOME%.*}

#Check that file is not multifasta

python /home/bioxaxi/PycharmProjects/FANTASIA/FANTASIA/single_line_fa.py $PROTEOME

mv ${PROTEOME}.out ${PROTEOME%.*}_oneline.pep

awk 'length($1) > 5000 { print $1 }' ${PROTEOME%.*}_oneline.pep > ${SP}_seqs_larger5k.txt

grep -B1 -f ${SP}_seqs_larger5k.txt ${PROTEOME%.*}_oneline.pep | grep ">" | sed "s/>//g" > ${SP}_headers_larger5k.txt

grep -Fvf ${SP}_headers_larger5k.txt ${PROTEOME} | grep ">" | sed "s/>//g" | cut -f1 -d" " > ${SP}_headers_smaller5k.txt

seqtk subseq $PROTEOME ${SP}_headers_smaller5k.txt > $OUT
