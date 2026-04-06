import argparse
import numpy as np
import time

def get_num_satisfied_clauses(file,assignment):
    with open(file,'r') as f:
        lines = [line.rstrip("\n") for line in f]
        sat=0
        for line in lines:
            if line[0]=='c' or line[0]=='p':
                continue  
            sat+=check_sat(line,assignment)
            
    return sat 

def get_num_satisfied_clauses_(lines,assignment):
    sat=0
    for line in lines:
        if line[0]=='c' or line[0]=='p':
            continue  
        sat+=check_sat(line,assignment)
    
    return sat
        

def check_sat(clause,assignment):
    clause = np.array(clause.split(sep=" ")[1:-1],dtype=np.int_) > 0 # 2 1 -3 -4 =? True True False False 
    assignment = np.array([assignment for assignment in assignment],np.int_) == 1 #0011=? False False True True 
    # truth table for logical equivalence (lol)
    return int(((clause==assignment)==True).any())

def get_random_pop(num_vars):
    MAXSIZE=10 # only really useful if the number of variables is more than 4. 
    pop=set()
    while len(pop)!=MAXSIZE:
        cand=''.join((np.random.sample((1,num_vars))>=0.5).astype(np.int_).astype(np.str_).tolist()[0])
        pop.add(cand)
    return list(pop)
    

def run_ea(file,time_budget,reps):
    num_vars=0
    POP_SIZE=10
    # read into memory 
    with open (file,'r') as f:
        lines= [line.rstrip("\n").split(" ") for line in f]
        for line in lines:
            if line[0]=='p':
                num_vars=int(line[2])
                num_clauses=int(line[3])

        for rep in range(reps): # remember to reset t0 and t1
            t0=time.time()
            # global vars
            runtime=0
            num_satisfied_clauses=0
            pop=get_random_pop(num_vars)
            gen=1
            best_sol=None
            best_fitness=-1
            while True:                    
                sat_clauses = [get_num_satisfied_clauses_(lines,assignment) for assignment in pop]
                pop=list(zip(pop,sat_clauses))
                pop.sort(key=lambda x: x[1],reverse=True)
                if pop[0][1] > best_fitness:
                    best_sol=pop[0][0]
                    best_fitness=pop[0][1]
                if time.time()-t0 >= time_budget:
                    runtime = gen * POP_SIZE
                    print(f"{runtime}\t{best_fitness}\t{best_sol}")
                    break
                new_pop=[]
                # evolution goes here..
                new_pop=pop[:5]
                # repair ??
                for sol in pop:
                    

                
                t1=time.time()
                if t1-t0>=time_budget:
                    return runtime,num_satisfied_clauses,best_sol

            
            t0=t1=0 # reset timer before start of new rep. 
                
        
        

def main():
    parser = argparse.ArgumentParser(
        prog = "assign_2",
        description='''
        question 1: checks if an assignment satisfies a clause given an assignment and clause.
        question 2: returns the number of satisfied clauses given a wdimacs file and an assignment.
        question 3: returns the runtime, num satisfied clauses, and the best solution given a wdimacs file, a time budget and the number of repitions by running an EA.  
        '''               
    )
    parser.add_argument('-question','--question',type=int,required=True)
    parser.add_argument('-clause','--clause',type=str,required=False,default=None)
    parser.add_argument('-wdimacs','--wdimacs',type=str,required=False,default=None)
    parser.add_argument('-assignment','--assignment',type=str,required=False,default=None)
    parser.add_argument('-assignment','--assignment',type=str,required=False,default=None)
    parser.add_argument('-time_budget','--time_budget',type=int,required=False,default=None)
    parser.add_argument('-repititions','--repititions',type=int,required=False,default=None)
    args = parser.parse_args()
    question=args.question
    if question==1:
        assignment = args.assignment
        clause = args.clause     
        res=check_sat(clause,assignment) if assignment is not None and clause is not None else "Provide both -assignment and -clause"
        print(res)
    elif question==2:
        file = args.wdimacs
        assignment = args.assignment
        sat = get_num_satisfied_clauses(file,assignment) if file is not None and assignment is not None else "Provide both -file and -assignment" 
        print(sat)
    elif question==3:
        file=args.wdimacs
        time_budget = args.time_budget
        reps = args.repititions
        run_ea(file,time_budget,reps)
            
       

if __name__=='__main__':
    main()