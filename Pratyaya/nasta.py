import argparse

parser = argparse.ArgumentParser("nasta")
parser.add_argument("syllables",help="The total number of syllables")
parser.add_argument("number",help="The number of the specific combination of light and heavy syllables")
args = parser.parse_args()

def nasta(s,n,i):
    if i % 2 == 0:
        s = s+"L"
        i = i/2
    else:
        s = s+"G"
        i = (i+1)/2
    if len(s) == n:
        print(s)
    else:
        nasta(s,n,i)

if __name__ == "__main__":
    nasta("",int(args.syllables),int(args.number))

