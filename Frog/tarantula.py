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
res['test_output'] = ""
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
