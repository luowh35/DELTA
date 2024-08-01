import time
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

def copy_and_run_tasks_cp(gen_dir, np=1):
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

def copy_and_run_tasks(gen_dir, files_to_copy, np=1):
    subdirs = [d for d in os.listdir(gen_dir) if os.path.isdir(os.path.join(gen_dir, d))]
    job_ids = []

    def copy_and_run(subdir):
        subdir_path = os.path.join(gen_dir, subdir)
        
        for file_name in files_to_copy:
            src_file = os.path.abspath(file_name)
            dest_file = os.path.join(subdir_path, os.path.basename(file_name))
            if os.path.isdir(src_file):
                logging.error(f"Source {src_file} is a directory, not a file.")
                return
            shutil.copy(src_file, dest_file)
        
        # Submit the PBS script using qsub
        submit_script_path = os.path.join(subdir_path, 'submit.sh')
        try:
            result = subprocess.run(['qsub', os.path.abspath(submit_script_path)], cwd=subdir_path, check=True, capture_output=True, text=True)
            job_id = result.stdout.strip().split('.')[0]  # Extract job ID
            logging.info(f"Successfully submitted {submit_script_path} with job ID {job_id}")
            job_ids.append(job_id)
            logging.info(f"qsub output: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing {submit_script_path}: {e}")
            logging.error(f"stderr: {e.stderr.strip()}")
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
    logging.info("Proceeding to post-submission steps...")

    # Post-submission steps: wait for jobs to complete
    wait_for_jobs_to_complete(job_ids)

def wait_for_jobs_to_complete(job_ids):
    logging.info("Waiting for all jobs to complete...")
    while job_ids:
        try:
            result = subprocess.run(['qstat'], capture_output=True, text=True, check=True)
            current_jobs = set(job_id for job_id in job_ids if job_id in result.stdout)
            if not current_jobs:
                logging.info("All jobs have completed.")
                break
            else:
                logging.info("Jobs are still running. Checking again in 60 seconds...")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking job status: {e}")
        
        time.sleep(30)

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
