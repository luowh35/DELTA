# delta/main.py
import logging
from delta.config import load_config
from delta.logger import setup_logging, display_info
from delta.atom_processing import filter_atoms
from delta.vasp import x2vasp, read_opt, final_str, process_generation
from delta.lammps import convert_all_poscars, copy_and_run_tasks, get_natom, out_energy, get_press, get_tasks_energy
from delta.genetic_algorithm import initial_X, renew_X, write_restart
import numpy as np
import os


def main():
    setup_logging()
    display_info()
    param = load_config('param.json')
    logging.info(param)
    input_file = param['input_file']
    output_dir = param['output_dir']
    atoms = param['atoms']
    total = param['total']
    pop_size = param['pop_size']
    generation = param['generation']
    mpi_tasks = param['mpi_tasks']
    CR_start = param['CR_start']
    CR_end = param['CR_end']
    F_start = param['F_start']
    F_end = param['F_end']
    restart = param['restart']

    if mpi_tasks == 1:
        logging.warning(
            f"YOU SET MPI_TASKS FOR 1, THAT MEANS YOUR TASKS ARE EXECUTED ONE AFTER ANOTHER.")
        logging.warning(
            f"IN ORDER TO THE EFFICIENCY, YOU CAN SET PARRELL VERSION")
    elif mpi_tasks > 20:
        logging.warning(
            f"YOU SET MPI_TASKS FOR {mpi_tasks}! ! ! PLEASE MAKE SURE THE TOTAL CPU CORES! ")

    if restart == 0:
        X = initial_X(atoms, total, pop_size)
        init_dir = os.path.join(output_dir, 'generation_0')
        os.makedirs(init_dir, exist_ok=True)
        process_generation(init_dir, input_file, X, mpi_tasks)
        E = get_tasks_energy(init_dir, pop_size)
        best_E = np.min(E)
        best_X = X[np.argmin(E)]
    elif restart == 1:
        X, E = read_opt(output_dir, restart)
        best_E = np.min(E)
        best_X = X[np.argmin(E)]
        logging.info(
            f"you set the restart = 1, read the restart.file in the {output_dir}")
    else:
        logging.error(f"restart should be 0 or 1! you set {restart}!")

    for i in range(generation):
        logging.info(
            f"----------------------Gen {i} START-------------------")
        logging.info(
            f"Generation {i + 1} start, Total Generation {generation}")
        F = F_end + (F_start - F_end) * (1 - i / generation)
        CR = CR_end + (CR_start - CR_end) * (1 - i / generation)
        logging.info(f"Now the F is: {F}, the CR is: {CR}")
        new_X = renew_X(X, atoms, F, CR)
        gen_dir = os.path.join(output_dir, f'generation_{i + 1}')
        os.makedirs(gen_dir, exist_ok=True)
        process_generation(gen_dir, input_file, new_X, mpi_tasks)

        new_E = get_tasks_energy(gen_dir, pop_size)
        new_X = np.array(new_X)
        X = np.array(X)
        tmp_X = []
        tmp_E = []
        for j in range(pop_size):
            new_x = new_X[j, :]
            old_x = X[j, :]
            new_e = new_E[j]
            old_e = E[j]
            if new_e < old_e:
                tmp_X.append(new_x)
                tmp_E.append(new_e)
            else:
                tmp_X.append(old_x)
                tmp_E.append(old_e)
        X = np.array(tmp_X)
        E = tmp_E
        tmp_best_E = np.min(E)
        tmp_best_X = X[np.argmin(E)]
        if tmp_best_E < best_E:
            best_E = tmp_best_E
            best_X = tmp_best_X
        logging.info(f"Generation {i + 1}: Best Fitness = {best_E:.2f}")
        final_str(input_file, output_dir, best_X)
        logging.info(
            f"--------------------Gen {i} FINISHED-------------------")
        write_restart(output_dir, X, E)
    logging.info(f"Best Fitness = {best_E:.2f}")
    logging.info(f"Best X = {best_X}")
    final_str(input_file, output_dir, best_X)
    logging.info(f"The final POSCAR is written into the output directory.")


if __name__ == "__main__":
    main()
