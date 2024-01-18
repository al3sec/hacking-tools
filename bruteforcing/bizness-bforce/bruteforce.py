import hashlib
from base64 import urlsafe_b64encode
import sys

def crack_hash_with_wordlist(hash_to_crack, salt, wordlist_file, encoding='latin-1'):
    count = 0
    with open(wordlist_file, 'r', encoding=encoding) as file:
        for word in file:
            word = word.strip()
            hash_object = hashlib.sha1(salt.encode() + word.encode())
            generated_hash = urlsafe_b64encode(hash_object.digest()).replace(b'+', b'.').decode()
            if generated_hash == hash_to_crack:
                return word
            count = count + 1
            print('count: ' + str(count))
    return None

if len(sys.argv) != 3:
    print("USAGE: python3 crack.py HASH WORDLIST")
    exit(1)

arguments = sys.argv[1]
wl = sys.argv[2]

salt = arguments.split("$")[2]
hash = arguments.split("$")[3]

nbtoadd = 28 - len(hash)

for i in range(nbtoadd):
  hash += "="

print("Hash with padding :", hash)

result = crack_hash_with_wordlist(hash, salt, wl)

if result:
    print("Password found :", result)
else:
    print("Password was not found")
