import argparse
import numpy as np
import time
import random

POP_SIZE=20
print("POP_SIZE= ",POP_SIZE)
TOURNAMENT_SIZE=3
print('TOURNAMENT_SIZE= ',TOURNAMENT_SIZE)
REPAIR_RATE=0.1
print("REPAIR_RATE= ",REPAIR_RATE)
FLIP_PROB=0.3
print("FLIP_PROB= ",FLIP_PROB)

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
                if assignment[abs(lit)-1] == '0':
                    satisfied_count+=1
                    satisfied=True
                    satisfied_clauses.append(clause_idx)
                    break
            elif assignment[lit-1] == '1':
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
    MAXSIZE=POP_SIZE 
    pop=set()
    while len(pop)!=MAXSIZE:
        cand=''.join((np.random.sample((1,num_vars))>=0.5).astype(np.int_).astype(np.str_).tolist()[0])
        pop.add(cand)
    return list(pop)
    
def tournament_select(pop,k,assignment_dict):
    chosen= random.sample(pop,k)
    chosen.sort(key=lambda x: assignment_dict[x][2],reverse=True)
    return chosen[0]

def one_point_crossover(parent_a, parent_b):
    randpoint = random.randint(1, len(parent_a) - 1)
    if random.random() < 0.5:
        return parent_a[:randpoint] + parent_b[randpoint:]
    else:
        return parent_b[:randpoint] + parent_a[randpoint:]

def mutate(offspring):  
    offspring=list(offspring)
    mutation_rate=1/len(offspring)
    for i in range (len(offspring)):
        if random.random()<mutation_rate:            
            offspring[i]='0' if offspring[i]=='1' else '1'
    
    return ''.join(offspring)


def get_num_clauses_broken_by_flip(lit,assignment,true_lit_count,lit_clause_mapping):
    # true lit count = {clause_idx:num_true_lits}
    # lit_clause_mapping = {lit:[clause_idxs]}
    break_count=0
    if assignment[lit-1]=='1':
        clauses_subset=lit_clause_mapping.get(lit,[]) # clauses where lit is present
    else:
        clauses_subset=lit_clause_mapping.get(-lit,[]) # clauses where neg lit is present
    # once lit is flipped, only clauses_subset are re-evaluated 
    for c in clauses_subset:
        if true_lit_count[c] == 1:
            break_count += 1
    return break_count

def flip_variable(lit,assignment,true_lit_count,lit_clause_mapping):
    idx=lit-1
    assignment[idx] = '0' if assignment[idx] == '1' else '1' # flip it 
    for clause in lit_clause_mapping.get(lit,[]):
        if assignment[idx]=='1':
            true_lit_count[clause]+=1
        else:
            true_lit_count[clause]-=1
    for clause in lit_clause_mapping.get(-lit, []):
        if assignment[idx] == '0':
            true_lit_count[clause] += 1
        else:
            true_lit_count[clause] -= 1

def walksat_repair(assignment,clauses,true_lit_count,lit_clause_mapping):
    # pick an unsatisfied clause:
    unsatisfied_clauses= [idx for idx,val in enumerate(true_lit_count) if val == 0]
    if not unsatisfied_clauses:
        return assignment 
    rand_clause=random.choice(unsatisfied_clauses)
    rand_clause=clauses[rand_clause]
    clause_vars = [abs(lit) for lit in rand_clause]
    if random.random()< FLIP_PROB:
        x=random.choice(clause_vars)
    else: # choose variable that minimises the number of unsat clauses when flipped
        best_x=[]
        min_broken = float('inf')
        for x_candidate in clause_vars:
            broken = get_num_clauses_broken_by_flip(x_candidate,assignment,true_lit_count,lit_clause_mapping)
            if broken < min_broken:
                min_broken=broken
                best_x=[x_candidate]
            elif broken==min_broken:
                best_x.append(x_candidate)
        x=random.choice(best_x)
    
    flip_variable(x,assignment,true_lit_count,lit_clause_mapping)
    
    return assignment
    
    # choose some variable 

def run_ea(clauses,lit_clause_mapping,n_vars,time_budget,reps):
    
    
    for rep in range(reps): # remember to reset t0 and t1
        t0=time.time()
        # global vars
        runtime=0
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
                print(f"New Best: {best_fitness} at Gen {gen} ({time.time() - t0:.2f} seconds)")
            if time.time()-t0 >= time_budget:
                runtime = gen * POP_SIZE
                unsatisfied_count = len(clauses) - best_fitness
                print(f"Total Clauses in File: {len(clauses)}")
                print(f"Generations Completed in 60s: {gen}")
                print(f"satisfied clauses: {best_fitness}/{len(clauses)}")
                print(f"{runtime}\t{best_fitness}\t{best_sol}")
                break
            new_pop=[]
            while len(new_pop)< POP_SIZE:
                # selection
                parent_a=tournament_select(pop,TOURNAMENT_SIZE,assignment_dict)
                parent_b=tournament_select(pop,TOURNAMENT_SIZE,assignment_dict)
                # crossover
                offspring = one_point_crossover(parent_a, parent_b)
                offspring=mutate(offspring)
                # repair 
                if random.random()<REPAIR_RATE:
                    offspring=list(offspring) # list of strings 
                    # compute the number of true literals per clause given the currnet offspring: 
                    true_lit_count = [0] * len(clauses)
                    for clause_idx,clause in enumerate(clauses): 
                        true_lit_count[clause_idx] = 0
                        for lit in clause: # a list of ints giving us an index into the offspring array
                            var_idx = abs(lit) - 1

                            if lit> 0:                                
                                if offspring[var_idx] == '1':
                                    true_lit_count[clause_idx] += 1
                            else:
                               if offspring[var_idx] == '0':
                                    true_lit_count[clause_idx] += 1
                    for _ in range(50):
                        offspring=walksat_repair(offspring,clauses,true_lit_count,lit_clause_mapping)   
                    offspring=''.join(offspring)             
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
            lit_clause_mapping = {}
            clauses = []

            for line in lines:
                if not line or line[0] in ['c']:
                    continue
                if line[0] == 'p':
                    n_vars = int(line[2])
                    continue

                clause = [int(lit) for lit in line[1:-1]]
                clause_idx = len(clauses)

                for lit in clause:
                    if lit not in lit_clause_mapping:
                        lit_clause_mapping[lit] = []
                    lit_clause_mapping[lit].append(clause_idx)

                clauses.append(clause)
                
        run_ea(clauses,lit_clause_mapping,n_vars,time_budget,reps)
        
        

if __name__=='__main__':
    main()
    
