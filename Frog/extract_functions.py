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
	print json.dumps(res)
	sys.exit()	

target = sys.argv[1]

# Check if file exists
if not os.path.isfile(target):
	#print "File does not exist. Exit."
	print json.dumps(res)
	sys.exit()

# Astyle parse
'''
print "\n1. Astyle target file: "+target
subprocess.call("astyle --style=allman "+target,shell=True)
'''

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
	reg = re.search(r'(\(\s+(.*)\s+\))', item, re.M|re.I)
	if reg:
		#print reg.group(2)+" - "+item[0:-1]
		if reg.group(2).strip().lower() != "void":
			kleeFunc.append(item[0:-1].strip())
			#print item[0:-1]

# If there is no function to test, exit
if len(kleeFunc) == 0:
	#print "No matched function found."
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

print json.dumps(res)

