#!/bin/bash
#
# add line to crontab:
# a) use private cron: crontab -e
# b) use system  cron: sudo nano /etc/crontab
# */15 * * * * /home/pi/temp/temp-writedb.sh
# this will read the sensor every 15 minutes

cd /home/pi/data/temp/ || exit

## config 1 read (default)
# read sensors and write into database
/usr/bin/python temp.py

# read sensors and write into backup-database
/usr/bin/python temp.py -b

## config 2 read
# read sensors and write into database
/usr/bin/python temp.py --conf temp-config-2.txt

# read sensors and write into backup-database
/usr/bin/python temp.py -b --conf temp-config-2.txt

## config 3 read
# read sensors and write into database
/usr/bin/python temp.py --conf temp-config-3.txt

# read sensors and write into backup-database
/usr/bin/python temp.py -b --conf temp-config-3.txt

## html config 1 (default)
# create html page with last dataset
/usr/bin/python temp.py -b -w

## html config 2
# create html page with last dataset
/usr/bin/python temp.py -b -w --conf temp-config-2.txt

## html config 3
# create html page with last dataset
/usr/bin/python temp.py -b -w --conf temp-config-3.txt

## multi html
/usr/bin/python temp.py -b -wm temp-config-2.txt,temp-config-anzeige.txt,temp-config-3-anzeige.txt

## copy temp*.html files
sudo cp -r www/temp* /var/www/temp/

echo ""
echo "File (s) copied"
echo ""
