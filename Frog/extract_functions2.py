import sys
import subprocess
import re
import glob
import os
from support_frog import compute
import json
from function import Function
import pickle

#####################################################
# extract_functions2.py
# version 2.0: update RE for more funciton types
# usage: python extract_function2.py [file name]
# output: res['msg'] and res['success'], res['content']
# file output: filename+function_id+".test.c"
# function data output: filename_function_id+".test.c.pickle"
#####################################################
res = {}
res['success'] = False
res['msg'] = ""

#####################################################
# Pre Configuration
#####################################################

# Default size for pointer symbolization
DEFAULT_SIZE = 5

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	#print "Missing argument. Exit."
	res['msg'] = "Missing argument"
	print json.dumps(res)
	sys.exit()	

target = sys.argv[1]

# Check if file exists
if not os.path.isfile(target):
	res['msg'] = "File does not exist"
	print json.dumps(res)
	sys.exit()

# Astyle parse
import os
with open(os.devnull,'w') as f:
	astyle_return = subprocess.call("astyle --style=allman "+target,shell=True, stdout=f)
if astyle_return == 1:
	res['msg'] = "Unable to run Astyle on source code"
	print json.dumps(res)
	sys.exit()

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
	for line in f:
		#reg = re.match(r'^\w+\s+\w+\s*\(.*\)\s*$', line, re.M|re.I)
		reg = re_func.match(line.strip())
		if reg:
			func.append(reg.group())

################################
# 3 - Screen functions
################################

for item in func:
	reg = re.search(r'(\(\s*(.*)\s*\))', item, re.M|re.I)
	if reg:
		if reg.group(1).strip().lower() != "void" and reg.group(1)!="":
			kleeFunc.append(item.strip())

# If there is no function to test, exit
if len(kleeFunc) == 0:
	res['msg'] = "No matched function found. Only accept function with argument(s)."
	print json.dumps(res)
	sys.exit()


########################################
# 4 - Create test file for each function
########################################
res['success'] = True
content = []
for fid in range(len(kleeFunc)):

	targetFunc = kleeFunc[fid]
	d = {}
	d['id'] = fid;
	d['function'] = targetFunc
	content.append(d)

	# - Create test file for target function
	testFileName = target+str(fid)+".test.c"
	testFileObject = target+str(fid)+".test.o"
	subprocess.call("cp "+target+" "+testFileName, shell=True)

	# Test if creation is successful
	if not os.path.isfile(testFileName):
		res['success'] = False
		res['msg'] = "Test file is not created successfully."
		print json.dumps(res)
		sys.exit()

	funcType = ""
	funcName = ""
	argType = []
	argName = []
	argIsPointer = []
	argSize = []

	# - Extract argument and funciton type
	reg = re_func.match( targetFunc )
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

	argSize = [ DEFAULT_SIZE for cnt in range(len(argType))]

	# Store function data
	fdata = Function()
	fdata.funcType = funcType
	fdata.funcName = funcName
	fdata.argType = argType
	fdata.argName = argName
	fdata.argIsPointer = argIsPointer
	fdata.argSize = argSize
	with open(testFileName+".pickle",'wb') as fb:
		pickle.dump(fdata, fb ,-1)

	# Append Main Function
	with open(testFileName, "ab") as f:
		# Inital include files and declaration
		appendCode = "\n#include \"klee.h\"\n"
		appendCode += "int main() {\n"

		# Add symbolic functions
		for i,atype in enumerate(argType):
			symbol = "a"+str(i)
			if argIsPointer[i]:
				# Example: char a0[size];
				size = DEFAULT_SIZE
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

		f.write(appendCode)

######################################
# Output function list to server
######################################
res['content'] = content
print json.dumps(res)
