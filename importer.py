import argparse 
from checker import check_sat


def main():
    parser = argparse.ArgumentParser(
    prog = "importer",
    description="imports a WDIMACS file and returns the number of clauses in the file satisfied by the assignment ",
            
)
    parser.add_argument('-wdimacs','--wdimacs',type=str,required=True)
    parser.add_argument('-assignment','--assignment',type=str,required=True)
    args = parser.parse_args()
    file = args.wdimacs
    assignment = args.assignment
    with open(file,'r') as f:
        lines = [line.rstrip("\n") for line in f]
        sat=0
        for line in lines:
            if line[0]=='c' or line[0]=='p':
                continue  
            sat+=check_sat(line,assignment)
            
    print(sat)           

if __name__=='__main__':
    main()