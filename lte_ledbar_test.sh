#!/bin/bash

chmod  +x lte_ledtest.sh

for ((i=0; i<8; ++i));
do 


./lte_ledtest.sh 1

./lte_ledtest.sh 3

./lte_ledtest.sh 7

./lte_ledtest.sh 15

./lte_ledtest.sh 7

./lte_ledtest.sh 3

./lte_ledtest.sh 1

./lte_ledtest.sh 0

sleep 1
done;

