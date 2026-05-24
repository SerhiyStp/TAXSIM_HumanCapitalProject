clear
cd "CPS"
use CPS_IPUMS_2010_base
gen pwages_2010 = pwages
gen swages_2010 = swages
local aes = "9779.44 10556.03 11479.46 12513.46 13773.1 14531.34 15239.24 16135.07 16822.51 17321.82 18426.51 19334.04 20099.55 21027.98 21811.6 22935.42 23132.67 23753.53 24705.66 25913.9 27426 28861.44 30469.84 32154.82 32921.92 33252.09 34064.95 35648.55 36952.94 38651.41 40405.48 41334.97 40711.61 41673.83 42979.61 44321.67 44888.16 46481.52 48098.63 48642.15 50321.89 52145.8 54099.99 55628.60 60575.07 63795.13 66621.80"
local ae2010 = 41673.83
local i = 1
cd "../TAXSIM_input_output/"
/*forvalues iyear = 1977/2019 {*/
forvalues iyear = 1977/2023 {
    replace year = `iyear'
	local ae: word `i' of `aes'
	display `ae'
	local ae_adj = `ae'/`ae2010'
	display `ae_adj'
    forvalues istate = 1/51 {
	    replace state = `istate'
		replace pwages = pwages_2010*`ae_adj'
		replace swages = swages_2010*`ae_adj'
		export delimited taxsim year state mstat page sage pwages swages depx dep13 dep17 dep18 using taxsim_input_state`istate'_year`iyear', replace nolabel
	}
	local i = `i' + 1
}
