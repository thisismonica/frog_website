import sys
import subprocess
import re
import glob
import os
from support_frog import compute
import json

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

# Initialize results
res = {}
res['success'] = False

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
	#print "File does not exist. Exit."
	res['msg'] = "File does not exist"
	print json.dumps(res)
	sys.exit()

# Astyle parse
'''
print "\n1. Astyle target file: "+target
'''
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

with open(target, 'r') as f:

	# Extract all functions using RegExp
	#print "\n2. Extract all functions"
	for line in f:
		reg = re.match(r'^\w+\s+\w+\s*\(.*\)\s*$', line, re.M|re.I)
		if reg:
			func.append(reg.group())
			#print line[0:-1] 

################################
# 3 - Screen functions
################################

#print "\n3. List functions that does not take void as arg"
for item in func:
	reg = re.search(r'(\(\s*(.*)\s*\))', item, re.M|re.I)
	if reg:
		#print reg.group(2)+" - "+item[0:-1]
		if reg.group(2).strip().lower() != "void" and reg.group(2)!="":
			kleeFunc.append(item[0:-1].strip())
			#print item[0:-1]

# If there is no function to test, exit
if len(kleeFunc) == 0:
	#print "No matched function found."
	res['msg'] = "No matched function found. Only accept function with argument(s)."
	print json.dumps(res)
	sys.exit()

# Ask for which function to test
res['success'] = True
content = []
for i,func in enumerate(kleeFunc):
	#print str(i)+". "+func
	d = {}
	d['id'] = str(i);
	d['function'] = func
	content.append(d)
res['content'] = content

################################
# 4 - func type, name & arg type
################################
for i in range(len(kleeFunc)):
	argType = []
	funcType = ""
	funcName = ""
	argName = []
	reg = re.search(r'(\w+)\s+(.*)\(\s+(.*)\s+\)\s*$', kleeFunc[int(i)], re.M|re.I)
	if reg:
		funcType = reg.group(1).strip()
		funcName = reg.group(2).strip()
		for pair in reg.group(3).split(','):
			argTypeArr = pair.strip().split(' ')
			if len(argTypeArr) == 2:
				argType.append(argTypeArr[0].strip())
				argName.append(argTypeArr[1].strip())
			else:
				argTypeStr = argTypeArr[0]+argTypeArr[1]
				argType.append(argTypeStr.strip())

	################################
	# 5 - Create test file
	################################
	testFileName = target+str(i)+".test.c"
	testFileObject = target+str(i)+".test.o"
	subprocess.call("cp "+target+" "+testFileName, shell=True)

	# Test if creation is successful
	if not os.path.isfile(testFileName):
		res['msg'] = "Test file is not created successfully."
		print json.dumps(res);
		sys.exit();

	# Append Main Function
	with open(testFileName, "ab") as f:
		#appendCode = funcType[i]+" main() {\n"
		appendCode = "#include \"klee.h\"\n"
		appendCode += "#include \"ansi_prefix.PPCEABI.bare.h\"\n"
		appendCode += "int main() {\n"
		for i,atype in enumerate(argType):
			symbol = "a"+str(i)
			appendCode += "\t"+atype+" "+symbol+";\n"
			appendCode += "\tklee_make_symbolic(&"+symbol+",sizeof("+symbol+"),\""+symbol+"\");\n"
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
		f.close()

# Output function list to server
print json.dumps(res)
