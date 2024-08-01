import os
import shutil
import subprocess
import logging
from ase.io import read, write
from concurrent.futures import ThreadPoolExecutor, as_completed

def convert_poscar_to_lammps(directory):
    poscar_file = os.path.join(directory, 'POSCAR')
    lammps_file = os.path.join(directory, 'data.lammps')
    
    if os.path.isfile(poscar_file):
        atoms = read(poscar_file)
        write(lammps_file, atoms, format='lammps-data')
    else:
        logging.warning(f"No POSCAR file found in {directory}")

def convert_all_poscars(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'POSCAR' in filenames:
            convert_poscar_to_lammps(dirpath)

def copy_and_run_tasks(gen_dir, np=1):
    current_dir = os.getcwd()
    subdirs = [d for d in os.listdir(gen_dir) if os.path.isdir(os.path.join(gen_dir, d))]
    files_to_copy = ['in.lammps', 'submit.sh']

    def copy_and_run(subdir):
        subdir_path = os.path.join(gen_dir, subdir)
        
        for file_name in files_to_copy:
            src_file = os.path.join(current_dir, file_name)
            dest_file = os.path.join(subdir_path, file_name)
            shutil.copy(src_file, dest_file)
        
        submit_script_path = os.path.join(subdir_path, 'submit.sh')
        try:
            result = subprocess.run(['sh', os.path.abspath(submit_script_path)], cwd=subdir_path, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing {submit_script_path}: {e}")
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")

    with ThreadPoolExecutor(max_workers=np) as executor:
        futures = [executor.submit(copy_and_run, subdir) for subdir in subdirs]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Task generated an exception: {e}")

    logging.info("All tasks completed.")

def get_natom(task_dir):
    filepath = os.path.join(task_dir, 'relax.lammpstrj')
    with open(filepath, 'r') as f:
        datas = [line.split() for line in f]
    natom = int(datas[3][0])
    return natom

def out_energy(task_dir):
    natom = get_natom(task_dir)
    log_file = os.path.join(task_dir, 'log.lammps')
    result = os.popen(f'''grep Enthalpy {log_file} | tail -1''').read().split('=')[1]
    try:
        energy = float(result) / natom
    except:
        energy = 76243685
    return energy

def get_press(task_dir):
    log_file = os.path.join(task_dir, 'log.lammps')
    result = os.popen(f'''grep Pressure {log_file} | tail -1''').read().split('=')[1]
    try:
        pressure = float(result)
        return abs(pressure) < 5e5
    except:
        return False

def get_tasks_energy(gen_dir, pop_size):
    with open(os.path.join(gen_dir, 'E.dat'), 'w') as output_file:
        E = []
        for i in range(1, pop_size + 1):
            task_dir = os.path.join(gen_dir, f'task_{i}')
            if os.path.isdir(task_dir):
                try:
                    if get_press(task_dir):
                        energy = out_energy(task_dir)
                    else:
                        energy = 76243685
                except:
                    energy = 76243685
                output_file.write(f'{energy}\n')
            E.append(energy)
    return E
