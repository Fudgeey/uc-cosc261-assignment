.class public Program
.super java/lang/Object
.method public <init>()V
aload_0
invokenonvirtual java/lang/Object/<init>()V
return
.end method
.method public static main([Ljava/lang/String;)V
.limit locals 2
.limit stack 1024
new java/util/Scanner
dup
getstatic java/lang/System.in Ljava/io/InputStream;
invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V
astore 0
sipush 2
istore 1
iload 1
sipush 3
if_icmpge l4
goto l3
l4:
goto l1
l3:
sipush 1
istore 1
goto l2
l1:
sipush 0
istore 1
l2:
getstatic java/lang/System/out Ljava/io/PrintStream;
iload 1
invokestatic java/lang/String/valueOf(I)Ljava/lang/String;
invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
return
.end method
