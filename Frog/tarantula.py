import sys
import json
import os
from support_frog import compute
import pickle

############################################################################
# tarantula.py 
# version 1.0: run tarantula based on F/M 
# usage: python replay.py [test file] (e.g. mid.c0.test.c)
# output: res['msg'] and res['success']
# output: res['test_output'] test case dictionary array - ['arg'] argument string, ['return'] output string
# output file: [test file name]_matrix.txt
###########################################################################

res = {}
res['success'] = False
res['msg'] = ""
res['suspiciousness'] = ""

################################
# 1 - Parse argument
################################

if len(sys.argv) < 2:
	res['msg'] += "Missing argument. Exit.\n"
	print res
	sys.exit(1)	

testFileName= sys.argv[1]

# Check if file exists
if not os.path.isfile(testFileName):
	res['msg'] += testFileName+ "File does not exist. Exit.\n"
	print res
	sys.exit(1)


######################################
# 2 - Construct F/M matrix from file
#####################################
cov_file = testFileName+"_coverage.pickle"
pf_file = testFileName+"_passorfail.txt"

M = []
with open(cov_file, 'rb') as f:
	while True:
		try:
			M.append(pickle.load(f))
		except EOFError:
			break

F = []
with open(pf_file, 'r') as f:
	for line in f.readlines():
		if line.strip() == "True":
			F.append(True)
		elif line.strip() == "False":
			F.append(False)
		else:
			res['msg'] += "Invalid file format of "+pf_file
			print res
			sys.exit(1)

################################
# 3 - Running tarantula
################################


# Set 'Live' (valid) test case, true if valid
testNum = len(F)
L = [True]*testNum

# Set 'Coverage' statement, true if the statement is coverage
stmtNum = len(M[0])
C = [True]*stmtNum

res['suspiciousness'] = compute(M,F,L,C)
res['success'] = True
print json.dumps(res)
