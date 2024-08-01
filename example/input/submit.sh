#!/bin/bash
#PBS -N lammps
#PBS -l nodes=1:ncpus=8
#PBS -j n
#PBS -q largeq
#PBS -e ${PBS_JOBNAME}.err
#PBS -o ${PBS_JOBNAME}.out
cd $PBS_O_WORKDIR
NP=`cat $PBS_NODEFILE|wc -l`
EXEC=/opt/ohpc/pub/apps/vasp.5.4.4/bin/vasp_std
#./record.sh
mpirun -np 8 lmp_mpi -i in.lammps > log.out
