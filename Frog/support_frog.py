#Tarantula suspiciousness calculations
'''
==Input Matrix to represent execution state of tarantula
M[][] coverage matrix - [test][stmt]
F[] failing test cases - [test] // True if test case fails
L[] live test cases - [test] // True if this test case is 'live', meaning used for suspiciousness calculating

==Matrix calculate by inputs
S[] fault numbers - [stmt] 
C[] coverable statements - [stmt]
B[] bad coverage - [test] // usually caused by seg fault

==Output suspiciousness and confidence value

'''

'''
 Calulate B[] to get bad coverage list, indexed by each testcases
 if one test cases has no statement, it is bad, usually caused by seg fault
@input M[][], [test][stmt], which test case execute which stmt
@output B[], [test], which test case is bad
'''
def getBadTestCoverage(M):
	numTests = len(M)
	B = []
	for test in M:
		# If no statement is executed, test case i is the bad case
		isBad = ( sum(test) == 0 )
		B.append(isBad)
	return B

'''
 Calculate total number of cases that is live, not bad and fail/pass 
@input: L[], F[], B[]
@output: total number of live fail cases, total number of live pass cases
'''
def getTotalLiveFailAndPass(L, F, B):
	totalLiveFail = 0;
	totalLivePass = 0;

	# iterate all test cases
	for i in range(0, len(L)):
		# if one test case is live and not bad
		if( L[i] and not B[i] ):
			if F[i] :
				totalLiveFail += 1
			else:
				totalLivePass += 1
	return totalLiveFail, totalLivePass

'''
 Calculate how may pass cases execute certain statement
@input B[], L[], C[], M[], F[]
@output passOnStmt[], failOnStmt[],index by  [stmt]
'''
def PassOnStmtAndFailOnStmt(B, L ,C ,M, F):
	numStmts = len(M[0])
	numTests = len(M)
	passOnStmt = [0] * numStmts # index by stmt, number of pass cases execute that stmt
	failOnStmt = [0] * numStmts # index by stmt, number of fail cases execute that stmt
	
	# Iterate each test
	for i in range(0,numTests):
		# if test not bad and is live
		if(not B[i] and L[i]):

			# iterate each statement
			for j in range(0,numStmts):

				# if statement is coverable and executed by i th test
				if( C[j] and M[i][j] ):
					if F[i]:
						failOnStmt[j] += 1
					else:
						passOnStmt[j] += 1
	return passOnStmt, failOnStmt

'''
  Calculate how pass ratio and fail ratio on each statement
 @input totalLivePass, totalLiveFail, passOnStmt[], failOnStmt[]
 @output passRatio[], failRation[], index by [stmt]
'''
def getPassRatioAndFailRatio(totalLivePass, totalLiveFail, passOnStmt,failOnStmt):
    
    # Initialize passRation and failRatio for each statement as zero
    numStmts = len(passOnStmt)
    passRatio = [0] * numStmts
    failRatio = [0] * numStmts
    
    # if total live pass cases number is non-zero, calculate passRatio = pass cases on each statement/ pass cases number in total
    if(totalLivePass != 0):
        passRatio = [float(p)/float(totalLivePass) for p in passOnStmt]

    # if total live fail cases number is non-zero, calculate failRation = fail cases on each statement / fail cases number in total
    if(totalLiveFail != 0):
        failRatio = [float(f)/float(totalLiveFail) for f in failOnStmt]

    return passRatio, failRatio

'''
    Final suspiciousness calculation on each statement
    @input totalLivePass, totalLiveFail, passRatio[], failRatio[]
    @output suspiciousness[stmt], confidence[stmt]
'''
def getSuspiciousnessAndConfidence(totalLivePass, totalLiveFail, passRatio, failRatio):

    # Initialize suspiciousness and confidence
    numStmts = len(passRatio)
    suspiciousness = [-1]*numStmts
    confidence = [-1]*numStmts

    # If total live fail number and total live pass number are both 0, suspiciousness and confidence are -1
    if( totalLiveFail==0 and totalLivePass==0):
        return suspiciousness, confidence

    # Iterate each statment to calculate suspiciousness and confidence
    for i in range(0, numStmts):
        if(passRatio[i]==0 and failRatio[i]==0):
            suspiciousness[i]=-1
            confidence[i]=-1
        else:
            suspiciousness[i] = failRatio[i]/ ( failRatio[i] + passRatio[i] )
            confidence[i] = max( failRatio[i], passRatio[i] )
    return suspiciousness, confidence

'''
#==== Testing code ====

# Set input
M=[ [True, False, True], [True, False, False] ]
F = [True, False]
L = [True, True]
C = [True, True, True]

print "==Getting bad coverage=="
B=getBadTestCoverage(M)
print "result is: ", B

print "\n==Getting total live pass and fail number =="
[f, p] = getTotalLiveFailAndPass(L,F,B)
print("Total live fail is %d; Total live pass is %d"%(f,p) )

print "\n===Getting pass/fail cases number on each statement=="
[pst,fst] = PassOnStmtAndFailOnStmt(B,L,C,M,F)
print "pass statement(1,0,0) is " ,pst," fail statement(1,0,1) is ",fst

print "\n===Getting pass/fail ratio on each statement==="
[pr, fr] = getPassRatioAndFailRatio(p, f, pst, fst)
print "pass ratio(1,0,0) is ",pr," fail ratio(1,0,1) is", fr
	
print "\n===Getting suspiciousness and confidence on each statement==="
[suspiciousness, confidence] = getSuspiciousnessAndConfidence(p,f,pr, fr)
print "suspiciousness(0.5, -1, 1) is", suspiciousness, "confidence(1,-1,1) is", confidence
'''

def compute(M, F, L, C):
	B = getBadTestCoverage(M)
	
	[f,p] = getTotalLiveFailAndPass(L,F,B)

	[pst, fst] = PassOnStmtAndFailOnStmt(B,L,C,M,F)

	[pr, fr] = getPassRatioAndFailRatio(p, f, pst, fst)
	
	[suspiciousness, confidence] = getSuspiciousnessAndConfidence(p,f,pr,fr)

	return suspiciousness
