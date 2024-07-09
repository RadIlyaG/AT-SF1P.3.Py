#!/bin/bash

# DATA  + GPIO1_6 + 476 = 482
# STROB + GPIO1_7 + 476 = 483

DATA=482
STROB=483 
DATADIR=/sys/class/gpio/gpio482
STROBDIR=/sys/class/gpio/gpio483

#echo "Configuring GPIO"

#echo $DATA  > /sys/class/gpio/export
#echo $STROB > /sys/class/gpio/export

#check if the gpio is already exported
if [ ! -e "$DATADIR" ]
then
	echo "Exporting DATA"
	echo $DATA > /sys/class/gpio/export
else
	echo "DATA already exported"
fi

if [ ! -e "$STROBDIR" ]
then
	echo "Exporting STROB"
	echo $STROB > /sys/class/gpio/export
else
	echo "STROB already exported"
fi


#echo "Set GPIO as output"

echo out > $DATADIR/direction
echo out > $STROBDIR/direction

echo "Current direction for DATA pin: `cat $DATADIR/direction`"
echo "Current direction for STROB pin: `cat $STROBDIR/direction`"


#echo "Set value as low"

echo 0 > $DATADIR/value
echo 0 > $STROBDIR/value

clock() {
#sleep 5
echo 1 > $STROBDIR/value
#sleep 5
echo 0 > $STROBDIR/value
}

if [ -z $1 ]; then
        echo "missing LTE Level value"
        exit 1
fi
value=$1


#echo "Shift  value"
mask=128

for ((i=0; i<8; ++i));
do 
((new_value = $value  << $i)) 
if (($new_value & $mask))
then
    echo 1 > $DATADIR/value
#echo "data = 1"
else 
    echo 0 > $DATADIR/value
#echo "data = 0"
fi
       clock
#    echo "new_value = $new_value"
done;

