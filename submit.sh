#!/bin/bash
#SBATCH --job-name=tax_hc
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
## Wall clock limit:
#SBATCH --time=0-10:00:00

#set -o errexit
#set -o nounset

module restore system
#module load intel-compilers/2025.0.0
#module load stata/19.0
module list

#time ./MAIN > ProgramOutput.txt
#exit 0
#./run_all.sh > ProgramOutput.txt
#./run_all_v1.sh > ProgramOutput.txt
#./run_all_v2.sh > ProgramOutput.txt
./run_all_v3.sh > ProgramOutput.txt

