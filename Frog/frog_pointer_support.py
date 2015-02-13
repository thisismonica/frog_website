import sys
import subprocess
import re
import glob
import os
import time 
import struct
from support_frog import compute

#####################################################
# Pre Configuration
#####################################################

# KLEE Related
KLEE_INCLUDE= "tools/KLEE_SOURCE_2015/klee/include/klee"   # Path to include files, for llvm compilation
KLEE_TIMEOUT = 10 
KLEE_OPTIONS = ["--allow-external-sym-calls"] #["--libc=uclibc"]#,"--posix-runtime" ]# KLEE C library Options
KLEE_EXECUTABLE = "./tools/KLEE_SOURCE_2015/klee/Release+Asserts/bin/klee"

# Test Cases 
KTEST = "./tools/KLEE_SOURCE_2015/klee/tools/ktest-tool/ktest-tool "
MAX_TESTS = 10

# Type map for test case result unapck
TYPE_DICT = {'char':'c','signed char':'b','unsigned char':'B','_Bool':'?','short':'h','unsigned short':'H','int':'i','unsigned int':'I','long':'l','unsigned long':'L','long long':'q','unsigned long long':'Q','float':'f','double':'d','char[]':'s','void *':'P'}
CTYPE_DICT = {'int':'%d', 'unsigned int':'%u','double':'%f','float':'%f'}

#####################################################
# Function Definition Block
#####################################################

def isNumber(s):
        try:
                int(s)
                return True
        except ValueError:
                pass

        try:
                import unicodedata
                unicodedata.numeric(s)
                return True
        except (TypeError, ValueError):
                pass

        return False

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	print "Missing argument. Exit."
	sys.exit()	

target = sys.argv[1]

# Check if file exists
if not os.path.isfile(target):
	print "File does not exist. Exit."
	sys.exit()

# Astyle parse
print "\n1. Astyle target file: "+target
subprocess.call("astyle --style=allman "+target,shell=True)

func = []
kleeFunc = []

################################
# 2 -Grap functions 
################################

# Define function Regex
re_func_str = r'^\s*(unsigned\s+|signed\s+)?(void|int|char|short|long|float|double)\s+(\w+)\s*\((.*)\)\s*$'
'''
\s*
(unsigned\s+|signed\s+)?                      # group(1): unsigned/signed
(void|int|char|short|long|float|double)  # group(2): return type
\s+
(\w+)                                    # group(3): function name
\s*
\(
([^)]*)                                    # group(4) args - total cop out
\)
\s*
'
'''
re_func = re.compile(re_func_str)

with open(target, 'r') as f:

	# Extract all functions using RegExp
	print "\n2. Extract all functions"
	for line in f:
		#reg = re.match(r'^\w+\s+\w+\s*\(.*\)\s*$', line, re.M|re.I)
		reg = re_func.match(line.strip())
		if reg:
			func.append(reg.group())
			print line[0:-1] 

################################
# 3 - Screen functions
################################

print "\n3. List functions that does not take void as arg"
for item in func:
	reg = re.search(r'(\(\s*(.*)\s*\))', item, re.M|re.I)
	if reg:
		#print reg.group(2)+" - "+item[0:-1]
		if reg.group(1).strip().lower() != "void" and reg.group(1)!="":
			kleeFunc.append(item.strip())
			#print item[0:-1]

# If there is no function to test, exit
if len(kleeFunc) == 0:
	print "No matched function found."
	sys.exit()

# Ask for which function to test
for i,func in enumerate(kleeFunc):
	print str(i)+". "+func

i = raw_input("\nFunction id: ")

while(not isNumber(i) or int(i)<0 or int(i)>len(kleeFunc)):
	print "Invalid Input."
	i = raw_input("\nFunction id: ")

targetFunc = kleeFunc[int(i)]

funcType = ""
funcName = ""
argType = []
argName = []
argIsPointer = []
argSize = []

################################
# 4 - func type, name & arg type
################################
print "\n4. Extracting func type, name and argument"
#reg = re.search(r'(\w+)\s+(.*)\(\s*(.*)\s*\)\s*$', kleeFunc[int(i)], re.M|re.I)
reg = re_func.match( kleeFunc[int(i)])
p_pointer_var1 = re.compile(r'^\*.*')
p_pointer_var2 = re.compile(r'.*\[\]$')
p_pointer_type = re.compile(r'.*\*$')

if reg:
	if reg.group(1) : #unsigned/signed
		funcType = reg.group(1).strip() + " "
	funcType += reg.group(2).strip()
	funcName = reg.group(3).strip()
	for pair in reg.group(4).split(','):
		argArr = pair.strip().split(' ')
		if len(argArr) == 2:

			# Check if argument is pointer type
			# FIXME: Messy code
				# Case 1: variable begin with *
			if p_pointer_var1.match(argArr[1]):
				argType.append(argArr[0].strip())
				argIsPointer.append(True)
				name = argArr[1].strip().replace('*','') 
				argName.append( name )

				# Case 2: variable end with []
			elif p_pointer_var2.match(argArr[1]):
				argType.append(argArr[0].strip())
				argIsPointer.append(True)
				name = argArr[1].strip().replace('[]','') 
				argName.append(name)

				# Case 3: type end with *
			elif p_pointer_type.match(argArr[0]):
				arg_type = argArr[0].strip().replace('*','')
				argType.append(arg_type)
				argIsPointer.append(True)
				argName.append(argArr[1].strip())

				# Case 4: not pointer type
			else:
				argType.append( argArr[0].strip() )
				argIsPointer.append(False)
				argName.append(argArr[1].strip())

		# Case 5: pointer * in the middle
		elif len(argArr)==3 and argArr[1]=="*":
			argType.append(argArr[0].strip())
			argIsPointer.append(True)
			argName.append(argArr[2].strip())

		# Case 6: long data type definition, Example: unsigned int a
		else:
			argTypeStr = " ".join( argArr[:-1] )
			argType.append(argTypeStr.strip())
			argIsPointer.append(False)
			argName.append(argArr[-1].strip())

argSize = [ 1 for i in range(len(argType))]

print funcType
print funcName
print argType

################################
# 5 - Create test file
################################

testFileName = target+".test.c"
testFileObject = target+".test.o"
print "\n5. Creating tmp file - "+testFileName
subprocess.call("cp "+target+" "+testFileName, shell=True)

# Test if creation is successful
if not os.path.isfile(testFileName):
	print "Test file is not created successfully."
	sys.exit()

# Append Main Function
with open(testFileName, "ab") as f:
	# Inital include files and declaration
	appendCode = "\n#include \"klee.h\"\n"
	appendCode += "int main() {\n"

	# Add symbolic functions
	for i,atype in enumerate(argType):
		symbol = "a"+str(i)
		if argIsPointer[i]:
			# User input for symbolize size of pointer type argument
			# Example: char a0[size];
			print "Argument ",argName[i]," is pointer of type: ",atype
			while True:
				size = raw_input("   Please enter size of unit to symbolize: ")
				try:
					size = int(size)
				except ValueError:
					print "Error: Invalid input, Only accept integer"
					pass
				else:
					if size >0:
						break
			appendCode += "\t"+atype+" "+symbol+"["+str(size)+"];\n"
			argSize[i] = size

			# Symbolize 
			# Example: klee_make_symbolic(a0, sizeof(a0), "a0")
			appendCode += "\tklee_make_symbolic(&"+symbol+",sizeof("+symbol+"),\""+symbol+"\");\n"

			# Add string NULL terminater
			# Example: klee_assume(a0[size-1]=='\0');
			if argType[i]=="char":
				appendCode += "\tklee_assume("+symbol+"["+str(size-1)+"]==\'\\0\');\n"
		else:			
			appendCode += "\t"+atype+" "+symbol+";\n"
			appendCode += "\tklee_make_symbolic(&"+symbol+",sizeof("+symbol+"),\""+symbol+"\");\n"

	# Call target function
	if funcType.lower() == "void":
		appendCode += "\t"+funcName+"("
	else:
		appendCode += "\t"+funcType+" result="+funcName+"("
	for i,atype in enumerate(argType):
		symbol = "a"+str(i)
		appendCode += symbol
		if i < len(argType)-1:
			appendCode += ","
	appendCode += ");\n"
	appendCode += "\treturn;\n"
	appendCode += "}"
	
	print appendCode

	f.write(appendCode)

################################
# 6 - Compile to object file
################################

print "\n6. LLVM linking"
linkAddr = []
linkAddr.append(KLEE_INCLUDE)

linkCmd = "llvm-gcc --emit-llvm -c -g"
for addr in linkAddr:
	linkCmd += " -I"+addr
linkCmd += " "+testFileName

# Delete old object
if os.path.isfile(testFileObject):
	subprocess.call("rm "+testFileObject,shell=True)

# Double check on llvm command
print linkCmd
raw_input("\nMake sure that above command is correct. Press Enter to continue...\n")

returncode = subprocess.call(linkCmd, shell=True)
print "return code: "+str(returncode)
if returncode != 0:
	print "Compilation failed."
	sys.exit() 
raw_input()

################################
# 7 - Klee run
################################

print "\n7. KLEE run"
if os.path.isfile(testFileObject):
	
	# Set klee timeout
	proc = subprocess.Popen([KLEE_EXECUTABLE]+KLEE_OPTIONS+[testFileObject])
	start = time.time()
	timeout = KLEE_TIMEOUT 
	while proc.poll() is None:
		time.sleep(0.1)
		now = time.time()
		if (now-start) > timeout:
		        print "KLEE timeout..."
			returncode = proc.returncode 
			proc.kill()
	returncode = proc.returncode

	#returncode = subprocess.call("klee "+testFileObject, shell=True)
	print "return code: "+str(returncode)
	if returncode != 0:
		print "Klee failed."
		sys.exit() 
else:
	print "Object file does not exist."
raw_input()

################################
# 8 - Replaying test cases
################################

print "\n8. Replaying test cases"

# Gather testcases file for read
temp_tests = "temp_klee_test_cases.txt" # temporary file to store test case values
if os.path.isfile(temp_tests):
	subprocess.call('rm '+temp_tests, shell=True)
tests = glob.glob('klee-last/test*.ktest')

# Build Regex to extract argument value
p = re.compile(r'^object\s*(\d+):\sdata:\s(.*)\n$')
testnum = 0

# Build Regex to match gcov uncovered line
p_gcov = re.compile('^\s+#####')

# Initialize matrix for Fault Localization
F = []
M = []

for test in tests[:MAX_TESTS]:

	# Display test case values, write to temp file klee_tests
	subprocess.call(KTEST+" "+test+' >'+temp_tests, shell=True)
	print "***Test case "+str(testnum)+" for function: ", targetFunc					
	testnum += 1
	argcount = 0
	argval = []

	# Find test case value for each argument
	with open(temp_tests,'r') as f:
		for line in f:
			a = p.findall(line)	
			# If match one parameter value
			if a:
				try:
					index = int( a[0][0])
					raw_val = a[0][1]
				except IndexError, ValueError:
					print "Error: Invalid test case format, Check if ", KTEST, "correct"
					sys.exit(1)
				else:
					# Array: Unpack argument string according to size
					if argIsPointer[argcount]:
						arg = raw_val 
						length = len(arg)/argSize[argcount]
						arg_array= []
						unpack_type = TYPE_DICT[ argType[argcount] ]

						try:
							for j in range(size):
								val = struct.unpack(unpack_type, arg[j*length:(j+1)*length] )[0]
								arg_array.append(val)
						except struct.error:
							print "Error: Invalid argument type, unable to unpack from binary format. Check ",KTEST
							sys.exit(1)
						
						# Display test cases
						display = argName[ index ] + "="
						
						# Special array: string
						if argType[argcount] == 'char':
							arg_array = "".join(arg_array)
						print display , arg_array
						
						# Add test cases for replay
						argval.append( str(arg_array) )
						argcount +=1

					# Single Variable
					else:							
						# Unpack argument according to type
						try:
							unpack_type = TYPE_DICT[ argType[argcount] ] 
							val = struct.unpack(unpack_type, raw_val )[0] 
						except struct.error:
							print "Error: Invalid argument type, unable to unpack from binary format. Check ",KTEST
							sys.exit(1)
						
						# Display test cases
						argstr = argName[index]+" = " + str(val)
						print argstr
						
						# Add test cases for replay
						argval.append( str(val) )
						argcount += 1
				
	# Judge if argument number valid
	if argcount != len(argName):
		print "ERROR: Invalid argument number of only ",argcount
		print "Press Enter to Continue..."
		raw_input()
		continue	

	# Build replay test file
	replayFileName = target + '.replay.c'
	if os.path.isfile(replayFileName):
		subprocess.call('rm '+replayFileName, shell=True)
	subprocess.call('cp '+target+' '+replayFileName, shell=True)

	with open(replayFileName, 'ab') as f:
		appendCode = "\n#include <stdio.h>\n"
		appendCode += "int main(){\n"

		# Definition for array type argument
		arg_symbols = {}
		array_cnt = 0
		for i,a in enumerate(argval):
			# Example: int a[5] = {1,2,3,4,5};
			if argIsPointer[i] and argType[i] != 'char':
				s1 = str(argval) 
				s1 = s1.replace('[','{')
				s1 = s1.replace(']','}')
				arg_symbol= "a"+str(array_cnt)
				appendCode = appendCode +'\t'+argType[i]+' '+arg_symbol +'['+str(argSize[i])+'] = '
				appendCode += s1 +";\n"
				array_cnt += 1
				arg_symbols[i] = arg_symbol
				
		if funcType.lower()=='void':
			appendCode+='\t'+funcName+'('
		else:
			appendCode+='\t'+funcType+' returnval='+funcName+'('
		for i,a in enumerate(argval):

			# For string type argument : join list 
			if argIsPointer[i] and argType[i] == 'char':
				a = '"'+a+'"'
			elif argIsPointer[i] and argType[i] != 'char' and i in arg_symbols:
				a = arg_symbols[i]

			appendCode+=a
			if i< len(argval)-1:
				appendCode+=', '
		appendCode+=');\n'
		if funcType.lower() =='void':
			appendCode+='\treturn;\n}'
		else:
			return_type = CTYPE_DICT[funcType.lower()] if funcType.lower() in CTYPE_DICT else '%d'
			appendCode+=r'    printf("Return value is '+return_type + r'\n",returnval);'
			
			appendCode+='\n\treturn;\n}'
		f.write(appendCode)
	
	# Compile test file
	replayOutput = target + '.replay'
	returnval = subprocess.call('gcc -w -fprofile-arcs -ftest-coverage '+replayFileName+' -o '+replayOutput, shell=True)
	if returnval != 0:
		print 'ERROR: gcc compile for repalying failed, press ENTER to continue...'
		raw_input()
		continue
	
	# Run test file
	returnCode = subprocess.call('./'+replayOutput, shell=True)
	if returnCode == 0:
		print "ERROR: replaying test case failed, press ENTER to continue..."
		raw_input()
		continue

	# Wait for user input to judge fail(F)/pass(P)
	print '**Test case pass? [y/n]:  '
	f = raw_input()

	# Write to Matrix F[]
	while f.lower()!='y' and f.lower()!='n':
		print "Invalid input, please enter \'y\' if pass, \'n\' if fail\n"
		f = raw_input()

	if f.lower()=='y':
		F.append(False)
	elif f.lower()=='n':
		F.append(True)
	
	# Get coverage
	returnval = subprocess.call('gcov '+replayFileName, shell=True)
	if returnval != 0:
		print 'ERROR: gcov failed, press ENTER to continue...'
		raw_input()
		continue

	# RE for not covered lines, marked with"#####" in gcov
	gcovFileName = replayFileName+'.gcov'
	lineCoverage = []
	
	# Read gcov file, write to coverage matrix M
	with open(gcovFileName,'r') as f:
		for i,line in enumerate(f):
			# ignore first 5 lines, not source code
			if i < 5:
				continue
			if p_gcov.match(line) :
				lineCoverage.append(False)
			else:
				lineCoverage.append(True)
				
	M.append(lineCoverage)

################################
# 9 - Running tarantula
################################

# Set 'Live' (valid) test case, true if valid
testNum = len(F)
L = [True]*testNum

# Set 'Coverage' statement, true if the statement is coverage
stmtNum = len(M[0])
C = [True]*stmtNum

suspiciousness = compute(M,F,L,C)

print suspiciousness
