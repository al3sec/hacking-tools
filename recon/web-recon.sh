#!/bin/bash

# The domain name
domain=$(echo $1 | sed -e 's/\./-/g')

# Discovering Subdomains & Content
echo "starting amass ..."
amass enum -brute -active -d $1 -o "$domain-amass-output.txt"

echo "starting subfinder ..."
subfinder -d $1 -o "$domain-subfinder-output.txt"

echo "starting knockpy ..."
python3 ~/Desktop/sideprojects/Hackthebox/tools/knock/knockpy.py $1 -o .
cat *.json  | jq 'keys[]' > "$domain-knockpy-output.txt"; sed -i -e 's/"//g'  -e '1d' "$domain-knockpy-output.txt"

cat "$domain-amass-output.txt" "$domain-subfinder-output.txt" "$domain-knockpy-output.txt"  > "$domain-subdomains.txt"

# Just unique subdomains
sort "$domain-subdomains.txt" | uniq > "$domain-uniq-subdomains.txt"; rm "$domain-subdomains.txt"
mv "$domain-uniq-subdomains.txt" "$domain-subdomains.txt"

# If you want to be really thorough and possibly even find some gems, dnsgen by Patrik Hudak
echo "using dnsgen ..."
cat "$domain-subdomains.txt" | dnsgen - | tee "$domain-dnsgen-subdomains.txt"

# Using a larger wordlist
dnsgen --wordlist /opt/useful/uniq-subdomain-permutation.txt subdomains.txt >> "$domain-dnsgen-subdomains.txt"
cat "$domain-dnsgen-subdomains.txt" >> "$domain-subdomains.txt"

# Again, just unique subdomains
sort "$domain-subdomains.txt" | uniq > "$domain-uniq-subdomains.txt"

# Now, it is the time to do DNS resolution.
echo "checking with dns resolution ..."
cat "$domain-uniq-subdomains.txt" | puredns resolve --resolvers /opt/useful/resolvers.txt --write "$domain-subdomains-perm.txt"

# Checking host command to see more details
echo "checking subdomains with host command ..."
cat "$domain-subdomains-perm.txt" | xargs -I{} host {} | tee -a "$domain-host-out.txt"

# From there you can find working http and https servers with httprobe
echo "testing http services ..."
cat "$domain-subdomains-perm.txt" | httprobe -p http:81 -p http:900 -p https:900 -p http:3000 -p https:3000 -p http:3001 -p https:3001 -p http:5000 -p https:5000 -p http:7070 -p https:7070 -p http:8000 -p https:8000 -p http:8008 -p https:8008 -p http:8080 -p https:8080 -p http:8443 -p https:8443 -p http:9000 -p https:9000 -p http:9090 -p https:9090 -c 50 | tee "$domain-online-subdomains.txt"

echo "starting ffuf ..."
ffuf -w /opt/useful/SecLists/Discovery/DNS/subdomains-top1million-110000.txt -u "https://FUZZ.$1" -o "$domain-json-ffuf-output.txt"
cat "$domain-json-ffuf-output.txt" | jq '.results[].url' > "$domain-ffuf-output.txt"
sed -i -e 's/"//g' "$domain-ffuf-output.txt"

# Adding ffuf output to online subdoms
cat "$domain-ffuf-output.txt" >> "$domain-online-subdomains.txt"

# Just unique http endpoints
sort "$domain-online-subdomains.txt" | uniq > "$domain-final-uniq-online-subdomains.txt"
# rm amass-output.txt subfinder-output.txt subdomains.txt uniq-subdomains.txt dnsgen-subdomains.txt online-subdomains.txt knockpy-output.txt ffuf-output.txt json-ffuf-output.txt *.json

# From there, visual inspection is a good idea, aquatone is a great tool, however most people
# don’t realise it will also accept endpoints and files
# echo "starting aquatone ..."
# cat "$domain-final-uniq-online-subdomains.txt" | aquatone

# Using a crawler
# cat final-uniq-online-subdomains.txt | sudo docker run --rm -i hakluke/hakrawler -d 3 > hakrawler-output.txt

# Using nmap in order to see more services on these subdomains:
# nmap -p- --min-rate=800 -iL subdomains-perm.txt -oN nmap-report.txt
# rm subdomains-perm.txt

# Using nuclei to going deeper
# nuclei -l final-uniq-online-subdomains.txt -o nuclei-output.txt

# If you already have a list of domains and what to see if there are new ones, anew TomNomNom also plays nicely
# cat new-output.txt | anew old-output.txt | httprobe

