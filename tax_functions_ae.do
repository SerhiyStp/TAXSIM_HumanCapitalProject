clear
* pause on

* Get full path of current .do file
* local dofile = c(filename)
* Extract folder path (everything up to the last backslash)
* local folder = substr("`dofile'", 1, strrpos("`dofile'", "\") - 1)
* Change directory
* cd "`folder'"
cd "TAXSIM_input_output//"

local ae2010 = 41673.83
/*local ae_cutoff = 0.5*`ae2010'*/
local ae_cutoff = 0.2*`ae2010'
import delimited using taxsim_output_state1_year2010.out
save tmp, replace
import delimited using taxsim_input_state1_year2010.csv, clear
merge 1:1 taxsimid using tmp
gen pwages2010 = pwages
gen swages2010 = swages
/*keep if mstat == 2*/
keep if (pwages2010 + swages2010) > `ae_cutoff'
/*keep if mstat == 1*/
/*keep if pwages2010 > `ae_cutoff'*/
keep taxsimid
save above_cutoff, replace



/*local file_name = "taxsim_taxparameters_1977_2019_single.txt"*/
/*local file_name = "taxsim_taxparameters_1977_2019_married.txt"*/
/*local file_name = "taxsim_taxparameters_1977_2023_married.txt"*/
local file_name = "taxsim_taxparameters_1977_2023_all_stateonly.txt"

// Sources:
// url_pre = "https://www.ssa.gov/oact/cola/oldawidata.html"
// url_post = "https://www.ssa.gov/oact/cola/awidevelop.html"

local aes = "9779.44 10556.03 11479.46 12513.46 13773.1 14531.34 15239.24 16135.07 16822.51 17321.82 18426.51 19334.04 20099.55 21027.98 21811.6 22935.42 23132.67 23753.53 24705.66 25913.9 27426 28861.44 30469.84 32154.82 32921.92 33252.09 34064.95 35648.55 36952.94 38651.41 40405.48 41334.97 40711.61 41673.83 42979.61 44321.67 44888.16 46481.52 48098.63 48642.15 50321.89 52145.8 54099.99 55628.60 60575.07 63795.13 66621.80"


file open myfile using `file_name', write replace
local i = 1
forvalues iyear = 1977/2023 {
    forvalues istate = 1/51 {
		
		*cd `taxsim_input_output_dir'
		import delimited using taxsim_output_state`istate'_year`iyear'.out, clear
		save tmp, replace
		import delimited using taxsim_input_state`istate'_year`iyear'.csv, clear
		merge 1:1 taxsimid using tmp
		drop _merge
		merge 1:1 taxsimid using above_cutoff
		keep if _merge == 3
		
		local ae: word `i' of `aes'
		di `ae'
		gen gross_inc = (pwages + swages + 0.5*fica) /* /`ae2010' */
		/*gen net_inc = (gross_inc - fiitax - siitax - fica) [> /`ae2010' <]*/
        gen net_inc = (gross_inc - siitax) /* /`ae2010' */
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
