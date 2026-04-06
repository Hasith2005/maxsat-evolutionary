import argparse
import numpy as np
import time
import random


# question 2
def get_num_satisfied_clauses(file, assignment):
    clauses = []
    with open(file, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0] == 'c' or parts[0] == 'p':
                continue  
            clauses.append([int(lit) for lit in parts[1:-1]])
    return check_sat_(clauses, assignment)[2]

        
def check_sat_(clauses,assignment): 
    satisfied_count=0
    satisfied_clauses=[]
    unsatisfied_clauses=[]
    for clause_idx,clause in enumerate(clauses):
        satisfied=False
        # given: clause [1,-3,5,-4] => x1 V -x3 V x5 V -x4 (get these values from the assignment)
        # break when a literal evaluates to true.  
        for lit in clause:
            if lit<0:
                if not(int(assignment[abs(lit)-1])) == 1:
                    satisfied_count+=1
                    satisfied=True
                    satisfied_clauses.append(clause_idx)
                    break
            elif int(assignment[lit-1])==1:
                satisfied_count+=1
                satisfied=True
                satisfied_clauses.append(clause_idx)
                break
        if not satisfied:
            unsatisfied_clauses.append(clause_idx)
    
    return satisfied_clauses,unsatisfied_clauses,satisfied_count
            
        
        
# question 1
def check_sat(clause,assignment):
    return check_sat_(clause,assignment)[2]

def get_random_pop(num_vars):
    MAXSIZE=10 # only really useful if the number of variables is more than 4. 
    pop=set()
    while len(pop)!=MAXSIZE:
        cand=''.join((np.random.sample((1,num_vars))>=0.5).astype(np.int_).astype(np.str_).tolist()[0])
        pop.add(cand)
    return list(pop)
    
def tournament_select(pop,k,assignment_dict):
    chosen= random.sample(pop,k)
    chosen.sort(key=lambda x: assignment_dict[x][2],reverse=True)
    return chosen[0]

def uniform_crossover(parent_a,parent_b):
    offspring_bits = [
        p1 if random.random() < 0.5 else p2 
        for p1, p2 in zip(parent_a, parent_b)
    ]
    return "".join(offspring_bits)

def mutate(offspring,mutation_rate):
    # flip a bit
    if random.random()<mutation_rate:
            
        offspring=list(offspring)
        rand_idx = random.randint(0,len(offspring)-1)
        lit=offspring[rand_idx]
        offspring[rand_idx]='0' if lit=='1' else '1'
        return ''.join(offspring)
    else:
        return offspring

def repair(offspring,clauses):
    satisfied_clauses,unsatisfied_clauses,num_satisfied=check_sat_(clauses,offspring)
    if not unsatisfied_clauses:
        return offspring
    # choose a clause at random 
    rand_clause_idx=random.choice(unsatisfied_clauses) # returns the index of the unsatisfied clause
    rand_clause=clauses[rand_clause_idx]
    # flip a variable that causes the least number of satisfied clauses to become unsatisfied while satisfying the current clause. 
    best_assignment= offspring
    max_satisfied_so_far = -1
    for lit in rand_clause: # 1,-3,5,-9
        offspring_list=list(offspring)
        offspring_lit = offspring_list[abs(lit)-1]
        offspring_list[abs(lit)-1] = '0' if  offspring_lit == '1' else '1' # flip the assignment for that literal and eval
        # now check sat 
        new_assignment = ''.join(offspring_list)
        _,_,num_satisfied_eval = check_sat_(clauses,new_assignment)
        if num_satisfied_eval > max_satisfied_so_far: # this clause must be satisfied AND not break any other clauses
            max_satisfied_so_far = num_satisfied_eval
            best_assignment=new_assignment
    return best_assignment
            

def run_ea(clauses,n_vars,time_budget,reps):
    POP_SIZE=100
    REPAIR_RATE=0.1

    for rep in range(reps): # remember to reset t0 and t1
        t0=time.time()
        # global vars
        runtime=0
        num_satisfied_clauses=0
        pop=get_random_pop(n_vars) # list of assignments
        gen=1
        best_sol=None
        best_fitness=-1
        while True:                    
            assignment_dict = {assignment:check_sat_(clauses,assignment) for assignment in pop}
            pop.sort(key=lambda x: assignment_dict[x][2],reverse=True)
            if assignment_dict[pop[0]][2] > best_fitness:
                best_sol=pop[0]
                best_fitness=assignment_dict[best_sol][2]
            if time.time()-t0 >= time_budget:
                runtime = gen * POP_SIZE
                print(f"{runtime}\t{best_fitness}\t{best_sol}")
                break
            new_pop=[]
            while len(new_pop)!= POP_SIZE:
                # selection
                parent_a=tournament_select(pop,3,assignment_dict)
                parent_b=tournament_select(pop,3,assignment_dict)
                # crossover
                offspring = uniform_crossover(parent_a, parent_b)
                offspring=mutate(offspring,mutation_rate=0.01)
                # repair 
                if random.random()<REPAIR_RATE:
                    offspring=repair(offspring,clauses)                
                new_pop.append(offspring)
            
            pop=new_pop
            gen+=1
            
        
        

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
    parser.add_argument('-time_budget','--time_budget',type=int,required=False,default=None)
    parser.add_argument('-repetitions','--repetitions',type=int,required=False,default=None)
    args = parser.parse_args()
    question=args.question
    if question==1:
        assignment = args.assignment
        clause = args.clause  
        parsed_clause = [int(lit) for lit in clause.split()[1:-1]]   
        res=check_sat([parsed_clause],assignment) if assignment is not None and clause is not None else "Provide both -assignment and -clause"
        print(res)
    elif question==2:
        file = args.wdimacs
        assignment = args.assignment
        sat = get_num_satisfied_clauses(file,assignment) if file is not None and assignment is not None else "Provide both -file and -assignment" 
        print(sat)
    elif question==3:
        file=args.wdimacs
        time_budget = args.time_budget
        reps = args.repetitions
        # open file, pass the clauses number of variables and number of clauses to the ea function
        with open (file,'r') as f:
            clauses=[]
            lines = [line.rstrip("\n").split() for line in f]
            n_vars=0
            for line in lines:
                if line[0]=='c':
                    continue
                if line[0]=='p':
                    n_vars=int(line[2])
                else:
                    clauses.append([int(lit) for lit in line[1:-1]])
            
        run_ea(clauses,n_vars,time_budget,reps)
            
       

if __name__=='__main__':
    main()