import argparse

parser = argparse.ArgumentParser("prastara")
parser.add_argument("syllables",help="The total number of syllables")
args = parser.parse_args()

def prastara(s,n):
    top = s
    bottom = s.copy()
    for i,j in enumerate(top):
        top[i] = j + "G"
    for i,j in enumerate(bottom):
        bottom[i] = j + "L"
    if len(top[0]) != n:
        prastara(top+bottom,n)
    else:
        for i,j in enumerate(top+bottom):
            print(str(i+1) + ": " + j)

if __name__ == "__main__":    
    s = [ "G", "L" ]
    prastara(s,int(args.syllables))

# the odd-numbered ones begin with a heavy syllable, and the even-numbered ones begin with a light. Each round disposes of half of the possibilities.
