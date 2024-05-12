bash
#!/bin/bash

read -p "File to run " file

python3 compiler.py < tests/"$file" > build/Program.j
java -Xmx100m -jar jasmin.jar build/Program.j
java -Xmx100m build/Program