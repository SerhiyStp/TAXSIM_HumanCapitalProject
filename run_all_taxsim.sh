for i in $(seq 1 1 2)
#for i in $(seq 1 1 1)
do
    for j in $(seq 2000 2001)
    #for j in $(seq 1998 1998)
    do
        for ae in 0.5 1.0 2.0 3.0
        do
            echo "state=$i year=$j ae=${ae}"
            ./taxsim35-unix.exe <taxsim_input_state_${i}_year_${j}_ae_${ae}.csv >taxsim_output_state_${i}_year_${j}_ae_${ae}.out
        done
    done
done
