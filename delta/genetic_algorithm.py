import numpy as np
import os

def initial_X(atoms=64, total=264, pop_size=10):
    sections = {
        "8a": (0, 24),
        "16d": (24, 72),
        "16c": (72, 120),
        "48f": (120, 264)
    }
    def create_individual():
        x = np.zeros(total)
        # 随机选择1到10之间的数量
        num_c = np.random.randint(1, 11)
        num_f = np.random.randint(1, 11)
        
        c_indices = np.random.choice(range(sections["16c"][0], sections["16c"][1]), num_c, replace=False)
        x[c_indices] = 1
        f_indices = np.random.choice(range(sections["48f"][0], sections["48f"][1]), num_f, replace=False)
        x[f_indices] = 1
        
        remaining_atoms = atoms - (num_c + num_f)
        remaining_sections = list(range(sections["8a"][0], sections["8a"][1])) + list(range(sections["16d"][0], sections["16d"][1]))
        remaining_indices = np.random.choice(remaining_sections, remaining_atoms, replace=False)
        x[remaining_indices] = 1
        
        return x

    X = [create_individual() for _ in range(pop_size)]
    return X

def crossover(target, donor, CR, atoms):
    if not (0 <= CR <= 1):
        raise ValueError("crossover_rate must be between 0 and 1")
    trial = np.where(np.random.rand(len(target)) < CR, donor, target)
    trial = repair(trial, atoms)
    return trial

def ensure_valid_individual(individual, atoms):
    indices = np.argsort(individual)[::-1]
    valid_individual = np.zeros_like(individual)
    valid_individual[indices[:atoms]] = 1
    return valid_individual

def mutate(population, atoms, F):
    pop_size = len(population)
    a, b, c = population[np.random.choice(pop_size, 3, replace=False)]
    donor = np.clip(a + F * (b - c), 0, 1)
    donor = np.round(donor).astype(int)
    indivi = repair(donor, atoms)
    return indivi

def repair(individual, atoms=64):
    sections = {
        "8a": (0, 24),
        "16d": (24, 72),
        "16c": (72, 120),
        "48f": (120, 264)
    }
    c_indices = range(sections["16c"][0], sections["16c"][1])
    f_indices = range(sections["48f"][0], sections["48f"][1])
    
    while sum(individual[c_indices]) > 10:
        ones_in_c = np.where(individual[c_indices] == 1)[0] + sections["16c"][0]
        individual[np.random.choice(ones_in_c)] = 0
        
    while sum(individual[f_indices]) > 10:
        ones_in_f = np.where(individual[f_indices] == 1)[0] + sections["48f"][0]
        individual[np.random.choice(ones_in_f)] = 0
    
    current_ones = sum(individual)
    
    if current_ones < atoms:
        remaining_sections = list(range(sections["8a"][0], sections["8a"][1])) + list(range(sections["16d"][0], sections["16d"][1]))
        remaining_zeros = np.where(individual[remaining_sections] == 0)[0]
        
        while current_ones < atoms:
            idx_to_flip = np.random.choice(remaining_zeros)
            individual[remaining_sections[idx_to_flip]] = 1
            remaining_zeros = np.delete(remaining_zeros, np.where(remaining_zeros == idx_to_flip))
            current_ones += 1
            
    elif current_ones > atoms:
        all_indices = np.where(individual == 1)[0]
        while current_ones > atoms:
            idx_to_flip = np.random.choice(all_indices)
            individual[idx_to_flip] = 0
            all_indices = np.delete(all_indices, np.where(all_indices == idx_to_flip))
            current_ones -= 1
    
    return individual

def renew_X(X, atoms, F, CR):
    X = np.array(X)
    pp = X.shape[0]
    new_X = []
    for i in range(pp):
        target = X[i]
        donor = mutate(X, atoms, F)
        new_x = crossover(target, donor, CR, atoms)
        new_X.append(new_x)
    return new_X

def write_restart(gen_dir, X, E):
    X_restart_file = os.path.join(gen_dir, 'X_restart.dat')
    E_restart_file = os.path.join(gen_dir, 'E_restart.dat')
    x = np.array(X)
    e = np.array(E)
    np.savetxt(X_restart_file, x, fmt='%d')
    np.savetxt(E_restart_file, e, fmt='%f')
