version 19
set more off
clear
cd "CPS"
use CPS_TAX_Data_w0
local year = 2005
keep if year == `year'
*keep if year == 2010
*keep if age > 19

gen state = statefip
replace state = 3 if statefip == 4 /* Arizona */
replace state = 4 if statefip == 5 /* Arkansas */
replace state = 5 if statefip == 6 /* Cali */
replace state = 6 if statefip == 8 /* Colorado */
replace state = 7 if statefip == 9 /* Connecticut */
replace state = 8 if statefip == 10 /* Delaware */
replace state = 9 if statefip == 11 /* DC */
replace state = 10 if statefip == 12 /* Florida */
replace state = 11 if statefip == 13 /* Georgia */
replace state = 12 if statefip == 15 /* Hawaii */
replace state = 13 if statefip == 16 /* Idaho */
replace state = 14 if statefip == 17 /* Illinois */
replace state = 15 if statefip == 18 /* Indiana */
replace state = 16 if statefip == 19 /* Iowa */
replace state = 17 if statefip == 20 /* Kansas */
replace state = 18 if statefip == 21 /* Kentucky */
replace state = 19 if statefip == 22 /* Luisiana */
replace state = 20 if statefip == 23 /* Maine */
replace state = 21 if statefip == 24 /*  */
replace state = 22 if statefip == 25 /*  */
replace state = 23 if statefip == 26 /*  */
replace state = 24 if statefip == 27 /*  */
replace state = 25 if statefip == 28 /*  */
replace state = 26 if statefip == 29 /*  */
replace state = 27 if statefip == 30 /*  */
replace state = 28 if statefip == 31 /*  */
replace state = 29 if statefip == 32 /*  */
replace state = 30 if statefip == 33 /*  */
replace state = 31 if statefip == 34 /*  */
replace state = 32 if statefip == 35 /*  */
replace state = 33 if statefip == 36 /*  */
replace state = 34 if statefip == 37 /*  */
replace state = 35 if statefip == 38 /*  */
replace state = 36 if statefip == 39 /*  */
replace state = 37 if statefip == 40 /*  */
replace state = 38 if statefip == 41 /*  */
replace state = 39 if statefip == 42 /*  */
replace state = 40 if statefip == 44 /*  */
replace state = 41 if statefip == 45 /*  */
replace state = 42 if statefip == 46 /*  */
replace state = 43 if statefip == 47 /*  */
replace state = 44 if statefip == 48 /*  */
replace state = 45 if statefip == 49 /*  */
replace state = 46 if statefip == 50 /* Vermont */
replace state = 47 if statefip == 51 /* Virginia */
replace state = 48 if statefip == 53 /* Washington */
replace state = 49 if statefip == 54 /* West Virginia */
replace state = 50 if statefip == 55 /* Wisconsin */
replace state = 51 if statefip == 56 /* Wyoming */   

*pause P1

gen mstat = 1 /* Single */
replace mstat = 2 if (marst < 3) /* Married, spouse present & Married, spouse absent */

save tmp, replace

keep if mstat == 1
*pause p1
keep if age > 19
save singles, replace

use tmp, clear
*pause P2

keep if mstat == 2
save married, replace
keep if relate == 101 /* Head/householder */
*pause p2
keep if age > 19
save married_hhead, replace
use married, clear
keep if relate == 201 /* Spouse */
*pause p3
gen incwage_spouse = incwage
rename age age_spouse
keep serial incwage_spouse age_spouse
save married_spouse, replace

use married_hhead, clear
merge 1:1 serial using married_spouse 
keep if _merge != 2
*pause PP1
*save married_matched, replace

append using singles
*pause PP2
rename age page
rename age_spouse sage
*pause PP3
replace sage = 0 if sage == .
*pause PP4
rename incwage pwages 
rename incwage_spouse swages 
replace swages = 0 if swages == .

*gen AE = 41673.83
*gen hhwages_ae = (pwages + swages)/AE
*gen pwages_ae = pwages/AE
*hist pwages_ae
*pause HHwages
*keep if hhwages_ae > 0.3

gen depx = nchild
replace depx = 0 if depx == .
gen dep13 = nchlt5
replace dep13 = 0 if dep13 == .
gen dep17 = nchild
replace dep17 = 0 if dep17 == .
gen dep18 = nchild
replace dep18 = 0 if dep18 == .

gen taxsimid = _n
replace state = 1
keep taxsimid year state mstat page sage depx dep13 dep17 dep18 pwages swages 
*export delimited using taxsim_input, replace nolabel

*pause PP5
*save CPS_IPUMS_2010_base, replace
save CPS_IPUMS_`year'_base, replace

