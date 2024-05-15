#!/bin/bash

python3 compiler.py < tests/"$1" > ./build/Program.J
java -Xmx100m -jar jasmin.jar -d ./build ./build/Program.J
java -Xmx100m -cp ./build Program