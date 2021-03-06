# based off grader.sh, kactl preprocessor

import subprocess # run terminal stuff
import os # check if file exists
import sys
from termcolor import colored # print in color + bold
import getopt # command line

IN="wire$.in"
OUT="O.$"

TL=2
CPP="g++ -O2 -w $.cpp -o $" # C++, -w = suppress warnings

def replace(x,y): # replace occurrences of $ in x with y
	return x.replace('$',str(y))
def cb(text,col): # color and bold text with color col
	return colored(text,col,attrs=['bold'])
def isfloat(value): # check if it can be float
	try:
		float(value)
		return True
	except ValueError:
		return False
def error(a,b): # min of absolute and relative error for two doubles
	res = abs(a-b)
	if a != 0:
		res = min(res,abs(1-b/a))
	return res

def parse(output): # split output by spaces
	assert os.path.isfile(output), f'File "{output}" does not exist, cannot parse'
	output = list(open(output))
	output = " ".join(output).split(" ")
	return [i for i in output if i]

def compile(x): # compile cpp file x
	print(cb(f" * Compiling {x}.cpp","cyan"))
	if subprocess.call(CPP.replace('$',x),shell=True) != 0:
		print(cb(" * Compilation failed","red"))
		print()
		sys.exit(0)
	else:
		print(cb(" * Compilation successful!","green"))
		print()

def run(x, inputF): # return tuple of output file, exit code, time
	outputF = f"{x}.out"
	runCom = f"ulimit -t {TL}; time -p (./{x} < {inputF} > {outputF}) 2> .time_info;"
	ret = subprocess.call(runCom,shell=True)
	if ret != 0:
		return outputF,ret,-1
	timeCo = 'cat .time_info | grep real | cut -d" " -f2' # get real time
	proc = subprocess.Popen(timeCom, stdout=subprocess.PIPE, shell=True)
	time = proc.communicate()[0].rstrip().decode("utf-8") 
	return outputF,ret,time

def check(o0,o1): # check if output files o0,o1 match
	O0,O1 = parse(o0),parse(o1)
	if len(O0) != len(O1):
		return "W", "outputs don't have same length"
	for i in range(len(O0)):
		z0,z1 = O0[i],O1[i]
		if z0 == z1:
			continue
		if isfloat(z0) and '.' in z0:
			if not isfloat(z1):
				return "W", f"{i}-th elements don't match, expected {z0} but found {z1}"
			e = error(float(z0),float(z1))
			if e > 1e-6:
				return "W", f"{i}-th floats differ, error={e}"
			continue
		return "W", f"{i}-th elements don't match, expected {z0} but found {z1}"
	return "A", "OK"

def interpret(e): # interpret exit code
	assert e != 0
	if e == 152:
		return "T", "time limit exceeded"
	return "R", f"exit code {e}"

def grade(prog,inputF,outputF):
	o, e, t = run(prog,inputF)
	if e != 0:
		return interpret(e)+(t,)
	return check(outputF,o)+(t,) 

def getOutput(prog,inputF):
	o, e, t = run(prog,inputF)
	if e != 0:
		return interpret(e)+(t,)
	return 'A',parse(o),t

def output(i,res,message,t):
	print(f" * Test {i}: ",end="")
	if res == 'A':
		print(cb(res,"green"),end="")
	else:
		print(cb(res,"red"),end="")
	print(f" - {message}",end="")
	if res == 'A' or res == 'W':
		print(f" [{t}]",end="")
	print()

def outputRes(correct,total):
	if total == 0:
		print(cb("ERROR:",'grey')+" No tests found! D:")
	else:
		print(cb("RESULT:","blue"),correct,"/",total)
		if correct == total:
			print("Good job! :D")

def GETOUTPUT(f):
	print(cb(f"GET OUTPUT FOR {f}.cpp","blue"))
	compile(f)
	print(cb("RUNNING TESTS","blue"))
	total,correct = 0,0
	for i in range(1,1000):
		label = str(i)
		inputF = replace(IN,label)
		if not os.path.isfile(inputF):
			label = "0"+label
			inputF = replace(IN,label)
		if not os.path.isfile(inputF):
			break
		res,message,t = getOutput(f,inputF)
		output(label,res,message,t)
		total = i
		if res == 'A':
			correct += 1
	print()
	outputRes(correct,total)

def GRADE(f):
	print(cb(f"GRADING {f}.cpp","blue"))
	compile(f)
	print(cb("RUNNING TESTS","blue"))
	total,correct = 0,0
	for i in range(1,1000):
		label = str(i)
		inputF = replace(IN,label)
		outputF = replace(OUT,label)
		if not os.path.isfile(inputF):
			label = "0"+label
			inputF = replace(IN,label)
			outputF = replace(OUT,label)
		if not os.path.isfile(inputF):
			break
		if not os.path.isfile(outputF):
			print(cb("ERROR:",'grey')+" Output file '"+outputF+"' missing!")
			sys.exit(0)
		res,message,t = grade(f,inputF,outputF)
		output(label,res,message,t)
		total = i
		if res == 'A':
			correct += 1
	print()
	outputRes(correct,total)

def compare(f0,f1,inputF):
	o0, e0, t0 = run(f0,inputF)
	o1, e1, t1 = run(f1,inputF)
	if e0 != 0:
		return "E", "supposedly correct code gave "+interpret(e0)[1], (t0,)
	if e1 != 0:
		return interpret(e1)+(t1,)
	return check(o0,o1)+((t0,t1),)

def COMPARE(f0,f1):
	print(cb(f"COMPARING CORRECT {f0}.cpp AGAINST {f1}.cpp","blue"))
	print()
	compile(f0), compile(f1)
	print(cb("RUNNING TESTS","blue"))
	total,correct = 0,0
	for i in range(1,1000):
		label = str(i)
		inputF = replace(IN,label)
		if not os.path.isfile(inputF):
			label = "0"+label
			inputF = replace(IN,label)
		if not os.path.isfile(inputF):
			break
		res,message,t = compare(f0,f1,inputF)
		output(label,res,message,t)
		total = i
		if res == 'A':
			correct += 1
	print()
	outputRes(correct,total)

def main():
	try:
		correct = None
		output = False
		opts, args = getopt.getopt(sys.argv[1:], "ohc:t:", ["output","help","correct","time"])
		for option, value in opts:
			if option in ("-h", "--help"):
				print("This is the help section for this program.")
				print()
				print("Available options are:")
				print("\t -h --help: display help")
				print("\t -t --time: set time limit")
				print()
				print("Available commands are:")
				print("\t 'python3 grader.py3 A': test if A.cpp produces correct output file for every input file")
				print("\t 'python3 grader.py3 -o A': display output of A.cpp for every input file")
				print("\t 'python3 grader.py3 -c B A': test if A.cpp produces same output as B.cpp for every input file")
				return
			if option in ("-t", "--time"):
				TL = float(value)
			if option in ("-c", "--correct"):
				correct = value 
			if option in ("-o"):
				output = True
		if len(args) != 1:
			raise ValueError("must have exactly one argument")
		if correct:
			if output:
				raise ValueError("cannot have both -c and -o")
			if correct == args[0]:
				raise ValueError("can't compare same prog against itself")
			COMPARE(correct,args[0])
		elif output:
			GETOUTPUT(args[0])
		else:
			GRADE(args[0])
	except (ValueError, getopt.GetoptError, IOError) as err:
		print(str(err), file=sys.stderr)
		print("\t for help use --help", file=sys.stderr)
		return 2

if __name__ == "__main__":
	exit(main())
