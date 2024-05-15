# COSC261 Compiler Assignment
A compiler of a basic language using an extended BNF syntax for the COSC261 2024S1 Assignment at the University of Canterbury.

## Running / Testing
First, the compiler is run using Python 3, with the program passed via standard input. The Java assembly is produced via standard output.  
`python3 compiler.py < program > Program.j`

Next, the Java assembly is translated to a Java class file using the Jasmin assembler.  
`java -Xmx100m -jar jasmin.jar Program.j`

Finally, the Java class file can be run.  
`java -Xmx100m Program`

## Language Syntax
Any programs written for this compiler must be use this grammar.
```Program = Statements
Statements = Statement (; Statement)*
Statement = If | While | Assignment | Read | Write

If = if BooleanExpression then Statements [else Statements] end
While = while BooleanExpression do Statements end
Assignment = identifier := Expression
Read = read identifier
Write = write Expression

Comparison = Expression Relation Expression
Relation = = | != | < | <= | > | >=

Expression = Term ((+ | -) Term)*
Term = Factor ((* | /) Factor)*
Factor = (Expression) | number | identifier

BooleanExpression = BooleanTerm (or BooleanTerm)*
BooleanTerm = BooleanFactor (and BooleanFactor)*
BooleanFactor = not BooleanFactor | Comparison
```