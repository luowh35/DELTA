import os
import numpy as np
from ase.io import read, write
from delta.atom_processing import filter_atoms
from delta.lammps import convert_all_poscars, copy_and_run_tasks
import logging
def x2vasp(input_file, output_base_folder, X):
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)
    
    atoms = read(input_file, format='vasp')
    
    total_Al = sum(1 for atom in atoms if atom.symbol == 'Al')
    num_to_keep = 64
    X = np.array(X)
    pp = X.shape[0]
    for i in range(pp):
        x = X[i,:]
        filtered_atoms = filter_atoms(atoms, 'Al', x)
        output_folder = os.path.join(output_base_folder, f'task_{i+1}')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.join(output_folder, 'POSCAR')
        write(output_file, filtered_atoms, format='vasp')
    
    np.savetxt(os.path.join(output_base_folder, 'X.dat'), X, fmt='%d')

def read_opt(out_dir, restart):
    X_path = os.path.join(out_dir, 'X_restart.dat')
    E_path = os.path.join(out_dir, 'E_restart.dat')
    if not os.path.isfile(X_path):
        raise logging.error(f"File {X_path} does not exist")
    data = np.loadtxt(X_path)
    X = data.tolist()
    E = np.loadtxt(E_path)
    return X, E

def final_str(input_file, output_dir, x):
    atoms = read(input_file, format='vasp')
    total_Al = sum(1 for atom in atoms if atom.symbol == 'Al')
    num_to_keep = 64
    filtered_atoms = filter_atoms(atoms, 'Al', x)
    output_file = os.path.join(output_dir, 'final_POSCAR')
    write(output_file, filtered_atoms, format='vasp')

def process_generation(gen_dir, input_file, run_file, X, np=1):
    x2vasp(input_file, gen_dir, X)
    convert_all_poscars(gen_dir)
    copy_and_run_tasks(gen_dir, run_file, np)
