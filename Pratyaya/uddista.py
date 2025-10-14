import argparse

parser = argparse.ArgumentParser("uddista")
parser.add_argument("pattern",help="The syllabic pattern, expressed in L and G")
args = parser.parse_args()

def recurse(i,n,p):
    if i == 0:
        print(str(n))
    else:
        i = i-1
        if p[i] == "L":
            n = n*2
        else: 
            n = (n*2)-1
        recurse(i,n,p)

if __name__ == "__main__":
    p = args.pattern
    if "L" in p:
        i = p.rindex("L")
        recurse(i,2,p)
    else:
        print("1")
    

