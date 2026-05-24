clear
* pause on

cd "TAXSIM_input_output_v2/"
pwd

/*local file_name = "taxsim_taxparameters_1977_2019_single.txt"*/
/*local file_name = "taxsim_taxparameters_1977_2019_married.txt"*/
/*local file_name = "taxsim_taxparameters_1977_2023_married.txt"*/
local file_name = "taxsim_taxparameters_1998_2024_adj_state_ae_v2.txt"

// Sources:
// url_pre = "https://www.ssa.gov/oact/cola/oldawidata.html"
// url_post = "https://www.ssa.gov/oact/cola/awidevelop.html"

local aes = "28861.44 30469.84 32154.82 32921.92 33252.09 34064.95 35648.55 36952.94 38651.41 40405.48 41334.97 40711.61 41673.83 42979.61 44321.67 44888.16 46481.52 48098.63 48642.15 50321.89 52145.8 54099.99 55628.60 60575.07 63795.13 66621.80 69846.57"


file open myfile using `file_name', write replace
local i = 1
forvalues iyear = 1998/2023 {
    forvalues istate = 1/51 {
		
		*cd `taxsim_input_output_dir'
		import delimited using taxsim_output_state_`istate'_year_`iyear'.out, clear
        count
		save tmp, replace
		import delimited using taxsim_input_state_`istate'_year_`iyear'.csv, clear
        count
		merge 1:1 taxsimid using tmp
		keep if _merge == 3
        count
		//drop _merge
		//merge 1:1 taxsimid using above_cutoff
		
		local ae: word `i' of `aes'
		di `ae'
		gen gross_inc = (pwages + swages + 0.5*fica) /* /`ae2010' */
        gen net_inc = (gross_inc - fiitax - siitax - fica) /* /`ae2010' */
        /*gen net_inc = (gross_inc - siitax) [> /`ae2010' <]*/
		gen gross_inc_ae = gross_inc/`ae'
		gen net_inc_ae = net_inc/`ae'
		
		gen log_gross = log(gross_inc_ae)
		gen log_net = log(net_inc_ae)
		*gen log_gross = log(gross_inc)
		*gen log_net = log(net_inc)
		
		*pause PP6

		*scatter log_net log_gross, mcolor(blue) msize(vtiny) || lfit log_gross log_gross, legend(off) xtitle("Log(gross income)") ytitle("Log(net income)")
		*scatter log_net log_gross, mcolor(blue) msize(vtiny) || lfit log_net log_gross, lcolor(red) || lfit log_gross log_gross, lcolor (black) lpattern(dash) ///
		*legend(order(1 "Data" 2 "OLS" 3 "45 degree line") position(0) bplacement(nwest)) xtitle("Log(gross income)") ytitle("Log(net income)")

		reg log_net log_gross 
		local beta1 = e(b)[1,1]
		local theta1 = 1 - `beta1'
		local beta0 = e(b)[1,2]
		local theta0 = exp(`beta0')
		di `iyear'
		di `istate'
		di `theta1'
		di `theta0'
		
		*cd `base_dir'
		file write myfile %4.0f "`iyear'" _tab %2.0f "`istate'" _tab %12.8f "`theta1'" _tab %12.8f "`theta0'" _n
		*pause P1
	}
	local i = `i' + 1
}
file close myfile
