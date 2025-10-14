import argparse

parser = argparse.ArgumentParser("sankhya")
parser.add_argument("syllables",help="The total number of syllables whose combinations are to be calculated")
args = parser.parse_args()

def recurse(steps,n):
    if n % 2 == 0:
        steps.append(str(int(n)) + " halved: square")
        n = n/2
        recurse(steps,n)
    else:
        steps.append(str(int(n)) + " minus 1: double")
        n = n - 1
        if n == 0:
            print(steps)
        else:
            recurse(steps,n)

def calculate(steps,n):
    i = len(steps) - 1
    while i >= 0:
        if steps[i].endswith("square"):
            n = n*n
        elif steps[i].endswith("double"):
            n = n*2
        print(steps[i] + " " + str(int(n)))
        i -= 1
    print(n)
        
if __name__ == "__main__":
    steps = []
    recurse(steps,int(args.syllables))
    calculate(steps,1)

