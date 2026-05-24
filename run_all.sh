#!/bin/bash
module load stata/19.0
#module load python/3.14.0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
pwd

echo "STEP 1: preparing CPS sample"
time {
    stata -b process_cps_dataset.do
}

echo "STEP 2: creating TAXSIM input files"
time {
    stata -b make_taxsim_inputs.do
}

echo "STEP 3: running TAXSIM model on CPS sample"
cd TAXSIM_input_output/
time {
    ./run_all_taxsim.sh
}
cd ..
echo "STEP 4: estimating thetas"
time {
    stata -b tax_functions_ae.do
}
#mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_single.txt .
#mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_married.txt .
mv TAXSIM_input_output/taxsim_taxparameters_1977_2019_all_stateonly.txt .
