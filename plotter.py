import assign_2
import matplotlib.pyplot as plt
import numpy as np
import io
import sys
import os

def run_experiment(file_path, time_budget, reps, pop_size, repair_rate, walksat_steps):
    # Extract just the filename for display purposes
    filename = os.path.basename(file_path)
    
    # Override globals in assign_2
    assign_2.POP_SIZE = pop_size
    assign_2.REPAIR_RATE = repair_rate
    assign_2.WALKSAT_STEPS = walksat_steps
    
    # Parse the WDIMACS file using the logic from your main script
    with open(file_path, 'r') as f:
        lines = [line.rstrip("\n").split() for line in f]
        lit_clause_mapping = {}
        clauses = []
        n_vars = 0
        for line in lines:
            if not line or line[0] == 'c': continue
            if line[0] == 'p':
                n_vars = int(line[2])
                continue
            clause = [int(lit) for lit in line[1:-1]]
            clause_idx = len(clauses)
            for lit in clause:
                if lit not in lit_clause_mapping: lit_clause_mapping[lit] = []
                lit_clause_mapping[lit].append(clause_idx)
            clauses.append(clause)

    # Capture the tab-separated stdout for parsing
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    # Run the EA logic
    assign_2.run_ea(clauses, lit_clause_mapping, n_vars, time_budget, reps)
    
    sys.stdout = sys.__stdout__ 
    
    lines = captured_output.getvalue().strip().split('\n')
    fitnesses = []
    runtimes = []
    
    for line in lines:
        if line:
            parts = line.split('\t')
            runtimes.append(int(parts[0]))
            fitnesses.append(int(parts[1]))
            
    return fitnesses, np.mean(runtimes)

# --- CONFIGURATION ---
# already tsted: mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/maxcut/brock400_4.clq.wcnf
#mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/maxcut/t7pm3-9999.spn.wcnf
#mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/set-covering/scpclr12_maxsat.wcnf
#mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/maxclique/brock400_1.clq.wcnf
# mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/bcp-syn/normalized-addm4.r.wcnf

file_path = "mse17-complete-unweighted-benchmarks/mse17-complete-unweighted-benchmarks/frb/frb40-19-5.partial.wcnf" # Set your instance path here
time_budget = 15
reps = 100
instance_name = os.path.basename(file_path)

experiments = {
    "POP_SIZE": [10, 50, 100],
    "REPAIR_RATE": [0.0, 0.1, 0.5],
    "WALKSAT_STEPS": [5, 50, 250]
}

# Baseline default params
base_pop, base_repair, base_walksat = 50, 0.1, 50

fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.suptitle(f'Parameter Sensitivity Analysis for MAX-SAT\nInstance: {instance_name} | Budget: {time_budget}s', fontsize=16)

print(f"Starting experiments for {instance_name}...")

for ax_idx, (param_name, values) in enumerate(experiments.items()):
    all_fitness_scores = []
    labels = []
    
    print(f"\nTesting {param_name}:")
    for val in values:
        print(f"  Value: {val}...", end="", flush=True)
        
        p = val if param_name == "POP_SIZE" else base_pop
        r = val if param_name == "REPAIR_RATE" else base_repair
        w = val if param_name == "WALKSAT_STEPS" else base_walksat
        
        fitnesses, avg_runtime = run_experiment(file_path, time_budget, reps, p, r, w)
        
        all_fitness_scores.append(fitnesses)
        labels.append(f"{val}\n(Avg Evals: {int(avg_runtime)})")
        print(f" Done! Mean: {np.mean(fitnesses):.1f}")
        
    # Plotting each parameter set
    axes[ax_idx].boxplot(all_fitness_scores, labels=labels)
    axes[ax_idx].set_title(f'Varying {param_name}\nFile: {instance_name}', fontsize=10)
    axes[ax_idx].set_ylabel('Satisfied Clauses')
    axes[ax_idx].set_xlabel(param_name)
    axes[ax_idx].grid(True, axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.subplots_adjust(top=0.85)

# Save the plot with the filename included in the PNG name
output_png = f"results_{instance_name.replace('.', '_')}.png"
plt.savefig(output_png)
print(f"\nPlotting complete. Results saved to {output_png}")
plt.show()