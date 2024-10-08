# DELTA: Differential Evolution algorithm for Large-scale Tailored Atomistic structures

## Overview
DELTA is a Python package designed to search for the minimum energy configurations of crystal structures using DDE algorithms and various computational chemistry tools. 

## Features
- Load configuration from JSON files
- Setup and display logging information
- Process atomic structures using the ASE library
- Generate and evolve populations of crystal structures
- Handle VASP and LAMMPS file formats
- Perform parallel computations

## Installation

1. **Create a virtual environment**:
    ```sh
    conda create -n delta python=3.9   #choose your python version and env name
    conda activate delta # 
    ```
2. **Clone the repository**:
    ```sh
    git clone https://github.com/luowh35/delta.git
    ```

3. **Install DELTA**:
    ```sh
    cd DELTA
    pip install .
    ```

## how to use
1. **Example for the Al2O3 structure searching**:
   ```sh
   cd example
   cat param.json
   ```
   **Then you will get this output, which is about the input parameters**:
    ```sh
        "input_file" : "./input/POSCAR",
        "lammps_in_file": "./input/in.lammps",
        "run_lammps_file": "./input/submit.sh",
        "output_dir" : "./out",
        "atoms" : 64,
        "total" : 264,
        "pop_size" : 4,
        "generation" : 3,
        "mpi_tasks" : 4,
        "CR_start" : 0.8,
        "CR_end" : 0.2,
        "F_start" : 0.8,
        "F_end" : 0.2,
        "restart" : 0
    ```
    
2. **Explanation of parameters**:
    `input_file`: Path to the POSCAR, which is filled with all possible positions.

    `output_dir`: Output director.

    `atoms`: Real atoms, now only support Al.

    `total`: All the Al + vacancy.

    `pop_size`: The total population of each generation.

    `generation`: The total generation.

    `mpi_tasks`: It determines how many tasks run at the same time.

    `CR_start` and `CR_end`: The starting and ending crossrate ​​of the DDE algorithm.

    `F_start` and `F_end`: The starting and ending Mutation Factor ​​of the DDE algorithm.

    `restart`: The flag to set continue calculation, only can be set to 0 or 1.

    
3. **Run the main script**:
    ```sh
    delta
    ```
    Or use `nohup delta` to prevent printing log information to the screen.
    
    You can also submit `delta` to the queue system, eg: PBS, Slurm.
    ```sh
    qsub rundelta.sh
    ```

## OUTPUT
The OUTPUT logfile is Generation.log, which contains the necessary output




