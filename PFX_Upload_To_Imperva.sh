#!/bin/sh
basename=$1
dom=${basename%.*}

mkdir -p sites
clear
read -p "Enter cert password: " pw
clear
echo Password Set

read -p "Enter Numerical SiteID for your domain: " sid



#ssl
openssl pkcs12 -in $1 -passin pass:"$pw" -passout pass:"$pw" -nocerts -out $dom.key
openssl pkcs12 -in $1 -passin pass:"$pw" -clcerts -nokeys -out tempcert.crt
openssl pkcs12 -in $1 -passin pass:"$pw" -cacerts -nokeys -out tempcacert.crt

cat tempcert.crt tempcacert.crt > $dom.pem
rm -rf tempcert.crt tempcacert.crt
clear
echo
echo "Created $dom.key and $dom.pem"
echo
echo
echo Invoking python script to upload $dom.pem to Imperva
echo
read -s -p  "Press Enter to continue"
echo
clear
echo site_id = \{$sid\} >thiscert.py
echo pemfile = "$dom.pem" >>thiscert.py
echo keyfile = "$dom.key" >>thiscert.py
echo pw = "$pw" >>thiscert.py
python ./PFX_Upload_To_Imperva.py
rm -rf thiscert.py
echo Complete
read -s -p "The End"
