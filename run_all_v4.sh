#!/bin/bash
module load stata/19.0
module load python/3.14.3

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
pwd
source ./myenv/bin/activate

echo "STEP 1: creating TAXSIM input files"
time {
    python gen_taxsim_ae_inputs.py step_2
}

echo "STEP 2: running TAXSIM model on CPS sample"
cd TAXSIM_input_output_2005/
time {
    ./run_all_taxsim.sh
}

cd ..
echo "STEP 3: estimating thetas or raw tax rates"
time {
    python gen_taxsim_ae_inputs.py step_3
}



