README for Gateway
Author/Contact: matthew.scott.lindsay@gmail.com

Description:

 Gateway is is part of a parking guidance and information system
 designed to take advantage of the TelosB and an analog range finder.

Setup:

1. Install: libCURL
2. Install: libmote
3. Install: libmjson
4. Build: g++ -Wall -L/serial -Iserial -Ijson/src/ -o main serial.cpp curl.cpp main.cpp -lmote -lcurl
5. Run: ./main

