#!/bin/bash

# DC_OUT1  + IO_8 + 422 = 430
# DC_OUT2  + IO_9 + 422 = 431

# DC_IN1  + IO_0 + 422 = 430
# DC_IN2  + IO_1 + 422 = 431


DC_OUT1=430
DC_OUT2=431 
DC_OUT1_DIR=/sys/class/gpio/gpio430
DC_OUT2_DIR=/sys/class/gpio/gpio431

DC_IN1=422
DC_IN2=423
DC_IN1_DIR=/sys/class/gpio/gpio422
DC_IN2_DIR=/sys/class/gpio/gpio423


#echo "Configuring GPIO"


#check if the gpio is already exported
if [ ! -e "$DC_OUT1_DIR" ]
then
	echo "Exporting DC_OUT1"
	echo $DC_OUT1 > /sys/class/gpio/export
else
	echo "DC_OUT1 already exported"
fi

if [ ! -e "$DC_OUT2_DIR" ]
then
	echo "Exporting DC_OUT2"
	echo $DC_OUT2 > /sys/class/gpio/export
else
	echo "DC_OUT2 already exported"
fi

if [ ! -e "$DC_IN1_DIR" ]
then
	echo "Exporting DC_IN1"
	echo $DC_IN1 > /sys/class/gpio/export
else
	echo "DC_IN1 already exported"
fi

if [ ! -e "$DC_IN2_DIR" ]
then
	echo "Exporting DC_IN2"
	echo $DC_IN2 > /sys/class/gpio/export
else
	echo "DC_IN2 already exported"
fi


#echo "Set GPIOs as output and input"

echo out > $DC_OUT1_DIR/direction
echo out > $DC_OUT2_DIR/direction
echo in > $DC_IN1_DIR/direction
echo in > $DC_IN2_DIR/direction

## 15:31 01/06/2023 next lines are performed by ATE
#while ( true );
#        do cat $DC_IN1_DIR/value > $DC_OUT1_DIR/value;
#		   cat $DC_IN2_DIR/value > $DC_OUT2_DIR/value;
#done;
