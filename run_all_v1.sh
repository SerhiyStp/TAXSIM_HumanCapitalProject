#!/bin/bash
module load stata/19.0
module load python/3.14.3

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
pwd
source ./myenv/bin/activate

echo "STEP 1: creating TAXSIM input files"
time {
    python gen_taxsim_ae_inputs.py
}

echo "STEP 2: running TAXSIM model on CPS sample"
cd TAXSIM_input_output_v1/
time {
    ./run_all_taxsim.sh
}

cd ..
echo "STEP 3: estimating thetas"
time {
    stata -b tax_functions_ae_v1.do
}
#mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_single.txt .
#mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_married.txt .
#mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_all_stateonly.txt .
mv TAXSIM_input_output_v1/taxsim_taxparameters_1998_2024_adj_state_ae.txt .
