#!/bin/bash

# Discovering Subdomains & Content
echo "starting amass ..."
amass enum -brute -active -d $1 -o amass-output.txt

echo "starting subfinder ..."
subfinder -d $1 -o subfinder-output.txt
cat amass-output.txt subfinder-output.txt > subdomains.txt

# From there you can find working http and https servers with httprobe
echo "testing http services ..."
cat subdomains.txt | httprobe -p http:81 -p http:3000 -p https:3000 -p http:3001 -p https:3001 -p http:8000 -p http:8080 -p https:8443 -c 50 | tee online-subdomains.txt

# If you want to be really thorough and possibly even find some gems, dnsgen by Patrik Hudak
echo "using dnsgen ..."
cat subdomains.txt | dnsgen - | httprobe | tee dnsgen-subdomains.txt

# adding it to online subdoms
cat dnsgen-subdomains.txt >> online-subdomains.txt

# just unique endpoints
sort online-subdomains.txt | uniq > uniq-online-subdomains.txt
rm amass-output.txt subfinder-output.txt subdomains.txt dnsgen-subdomains.txt online-subdomains.txt

# From there, visual inspection is a good idea, aquatone is a great tool, however most people
# don’t realise it will also accept endpoints and files
cat uniq-online-subdomains.txt | aquatone

# To discover files and directories, ffuf
# ffuf -ac -v -u https://domain/FUZZ -w wordlist.txt

# If you already have a list of domains and what to see if there are new ones, anew TomNomNom also plays nicely
# cat new-output.txt | anew old-output.txt | httprobe
