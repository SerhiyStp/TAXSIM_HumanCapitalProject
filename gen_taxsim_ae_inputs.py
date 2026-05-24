# %%
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import pickle

# %%
def get_awis():
    import webscraping_fns as web_scrape
    url_pre = "https://www.ssa.gov/oact/cola/oldawidata.html"
    url_post = "https://www.ssa.gov/oact/cola/awidevelop.html"

    awi_pre = web_scrape.get_awi(url_pre, 7)
    awi_post = web_scrape.get_awi(url_post, 1)

    awi = pd.concat([awi_pre, awi_post])
    awi.to_pickle('awi.pkl')
    awi_df = pd.DataFrame(awi)
    awi_df.rename(columns={0: 'awi'}, inplace=True)
    awi_df['year'] = awi_df.index
    awi_df.to_csv('awi.csv', index=False)


def save_cps_parquet():
    df = pd.read_stata("CPS/CPS_TAX_Data_w0.dta")
    df["uhrsworkt"] = pd.to_numeric(
        df["uhrsworkt"]
            .replace(["hours vary", "niu"], np.nan),
        errors="coerce"
    )
    df["uhrswork1"] = pd.to_numeric(
        df["uhrswork1"]
            .replace(["hours vary", "niu/missing"], np.nan),
        errors="coerce"
    )
    df.to_parquet("CPS/CPS_TAX_DATA_w0.parquet")
    return 0

def process_cps_dataset_alt(year=2010):

    with open('fips_to_irs.pickle', 'rb') as f:
        fips_to_irs = pickle.load(f)

    with open('irs_to_statename.pickle', 'rb') as f:
        irs_to_statename = pickle.load(f)

    #df = pd.read_stata("CPS/CPS_TAX_Data_w0.dta", convert_categoricals=False)
    #df.to_parquet("CPS/CPS_TAX_DATA_w0_alt.parquet")

    df = pd.read_parquet("CPS/CPS_TAX_DATA_w0_alt.parquet")
    df = df.loc[ df['year'] == year ]
    df = df.loc[ (df['age'] > 19) & (df['age'] < 65) ]
    df['mstat'] = np.where(df['marst'] < 3, 2, 1)
    df['state'] = df['statefip'].map(fips_to_irs).map(irs_to_statename)

    df_singles = df.loc[ df['mstat'] == 1 ]

    df_mar_head = df.loc[ (df['mstat'] == 2) & (df['relate'] == 101) ]
    df_mar_spouse = df.loc[ (df['mstat'] == 2) & (df['relate'] == 201) ]
    df_mar_spouse = df_mar_spouse[['serial', 'incwage', 'statefip', 'sex', 'age', 'marst', 'relate']]
    df_mar = pd.merge( df_mar_head, df_mar_spouse, on=['serial'], suffixes=('_head', '_spouse') )
    df_mar = df_mar.rename(
        columns={
            'incwage_head': 'incwage', 
            'statefip_head': 'statefip', 
            'sex_head': 'sex', 
            'age_head': 'age',
            'marst_head': 'marst',
            'relate_head': 'relate'}
        )

    df_year = pd.concat([df_singles, df_mar], ignore_index=True)
    #df_year = df_mar
    print(df_year.groupby(['state']).size().sort_values())

    df_year['page'] = df_year['age'].fillna(0)
    df_year['sage'] = df_year['age_spouse'].fillna(0)
    df_year['depx'] = df_year['nchild'].fillna(0)
    df_year['age1'] = df_year['yngch'].fillna(0)
    #df_year.loc[df_year['yngch'] == 'niu', 'age1'] = 0
    df_year['pwages'] = df_year['incwage'].fillna(0)
    df_year['swages'] = df_year['incwage_spouse'].fillna(0)
    df_year["age1"] = df_year["age1"].replace(99, 0)
    df_year["age2"] = np.where(df_year["depx"] == 2, df_year["eldch"], 0)
    df_year["age3"] = np.where(df_year["depx"] == 3, df_year["eldch"], 0)
    df_year["intrec"] = df_year["incint"].fillna(0)
    df_year["dividends"] = df_year["incdrt"].fillna(0)
    df_year["stcg"] = df_year["capgain"] - df_year["caploss"]
    df_year["stcg"] = df_year["stcg"].fillna(0)
    df_year.loc[ (df_year["age3"] <= 19) & (df_year["age3"] > 0) & (df_year["age2"] == 0), "age2" ] = df_year["age3"]
    df_year.loc[ (df_year["age1"] > 0) & (df_year["age3"] > 0) & (df_year["age2"] == 0), "age2" ] = (df_year["age1"] + df_year["age3"])//2

    #df_year.to_parquet("CPS2010.parquet")
    df_year = df_year[['statefip','mstat','serial','page','sage','pwages','swages','depx','age1','age2','age3','intrec','dividends','stcg']]
    df_year.to_csv(f"CPS{year}.csv", index=False)

    return 0

def process_cps_dataset():
    df = pd.read_parquet("CPS/CPS_TAX_DATA_w0.parquet")
    df = df.loc[ df['year'] == 2010 ]
    df['age'] = pd.to_numeric( df['age'], errors="coerce" )
    df = df.loc[ (df['age'] > 19) & (df['age'] < 65) ]
    df['statefip_int'] = df['statefip'].cat.codes
    #print(df.groupby(['statefip_int']).size())
    #print(df.head())
    df['mstat'] = (df['marst'].isin(['married, spouse present', 'married, spouse absent'])).astype(int) + 1

    df_singles = df.loc[ df['mstat'] == 1 ]

    df_mar_head = df.loc[ (df['mstat'] == 2) & (df['relate'] == "head/householder") ]
    df_mar_spouse = df.loc[ (df['mstat'] == 2) & (df['relate'] == "spouse") ]
    df_mar_spouse = df_mar_spouse[['serial', 'incwage', 'statefip', 'sex', 'age', 'marst', 'relate']]
    df_mar = pd.merge( df_mar_head, df_mar_spouse, on=['serial'], suffixes=('_head', '_spouse') )
    df_mar = df_mar.rename(
        columns={
            'incwage_head': 'incwage', 
            'statefip_head': 'statefip', 
            'sex_head': 'sex', 
            'age_head': 'age',
            'marst_head': 'marst',
            'relate_head': 'relate'}
        )
    #df_mar_test = df_mar[['incwage_head','incwage_spouse','age_head','age_spouse','sex_head','sex_spouse','marst_head','marst_spouse','relate_head','relate_spouse','statefip_head','statefip_spouse']]

    df2010 = pd.concat([df_singles, df_mar], ignore_index=True)
    print(df2010.groupby(['statefip']).size())

    df2010['page'] = df2010['age'].fillna(0)
    df2010['sage'] = df2010['age_spouse'].fillna(0)
    df2010['depx'] = df2010['nchild'].cat.codes.fillna(0)
    df2010['age1'] = df2010['yngch'].cat.codes.fillna(0)
    df2010.loc[df2010['yngch'] == 'niu', 'age1'] = 0
    df2010['pwages'] = df2010['incwage'].fillna(0)
    df2010['swages'] = df2010['incwage_spouse'].fillna(0)
    df2010["age2"] = np.where(df2010["depx"] == 2, df2010["eldch"].cat.codes, 0)
    df2010["age3"] = np.where(df2010["depx"] == 3, df2010["eldch"].cat.codes, 0)
    df2010["intrec"] = df2010["incint"].fillna(0)
    df2010["dividends"] = df2010["incdrt"].fillna(0)
    df2010["stcg"] = df2010["capgain"] - df2010["caploss"]
    df2010["stcg"] = df2010["stcg"].fillna(0)
    df2010.loc[ (df2010["age3"] <= 19) & (df2010["age3"] > 0) & (df2010["age2"] == 0), "age2" ] = df2010["age3"]

    #df2010.to_parquet("CPS2010.parquet")
    df2010 = df2010[['statefip','statefip_int','mstat','serial','page','sage','pwages','swages','depx','age1','age2','age3','intrec','dividends','stcg']]
    df2010.to_csv("CPS2010.csv", index=False)
    
    return 0

# %%
def make_taxsim_inputs_v3(AE=1.0, AE_cut=1.0, cpsyear=2010):
    df_ebs = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    df_awi = pd.read_csv("awi.csv")
    df_cps = pd.read_csv(f"CPS{cpsyear}.csv")
    df_cps['hhwages'] = df_cps['pwages'] + df_cps['swages']
    m_hh_cps = df_cps['hhwages'].mean()
    m_pe_cps = df_cps['pwages'].mean()
    ae_bea_cpsyear = df_ebs[  (df_ebs['Year'] == cpsyear) & (df_ebs['IRS'] == 0) ]['per capita income'].iloc[0]
    ae_ss_cpsyear = df_awi.loc[ df_awi['year'] == cpsyear, 'awi' ].iloc[0]
    #print("Mean earnings: ")
    #print(f" CPS(hhwages): {m_hh_cps}")
    #print(f" CPS(phwages): {m_pe_cps}")
    #print(f" BEA(per capita income): {ae_bea_2010}")
    #print(f" SS(per capita income): {ae_ss_2010}")
    state_codes = df_ebs['IRS'].unique()
    # state_codes = [1]
    #years = df_ebs['Year'].unique()
    years = list(range(1977, 2024))
    # years = list(range(2000, 2001))
    make_hist = False
    for state in state_codes:
        print("State {state}")
        ae_bea_cpsyear_state = df_ebs[ (df_ebs['IRS'] == state) & (df_ebs['Year'] == cpsyear ) ]['per capita income'].iloc[0]
        for year in years:
            print(year)
            df_cps = pd.read_csv(f"CPS{cpsyear}.csv")
            ae_ss_year = df_awi.loc[ df_awi['year'] == year, 'awi' ].iloc[0]
            #adj_state = ae_bea_2010_state/ae_bea_2010
            adj_state = 1.0
            adj_year = ae_ss_year/ae_ss_cpsyear
            adj_factor = adj_state*adj_year
            df_cps['hhwages'] = df_cps['pwages'] + df_cps['swages']
            df_cps['pwages'] = df_cps['pwages']*adj_factor
            df_cps['swages'] = df_cps['swages']*adj_factor
            df_cps['hhwages'] = df_cps['hhwages']*adj_factor
            ae_m_hh = df_cps['hhwages'].mean()
            df_cps['state'] = state
            df_cps['year'] = year
            df_cps['hhwages_ae'] = df_cps['hhwages'] / ae_m_hh
            if (make_hist == True):
                df_cps['hhwages_ae'].hist(bins=100)
                plt.axvline(x = 1, color = 'k')
                #plt.xlim(0, 5)
                plt.xlim(0, 11)
            df_cps_filtered = df_cps[ (df_cps['hhwages_ae'] > AE_cut - 0.2) & (df_cps['hhwages_ae'] < AE_cut + 0.2)  ] 
            print(f"{len(df_cps_filtered)} observations in state {state} in year {year} after filtering for AE={AE_cut}")
            mm = df_cps_filtered['mstat'].value_counts()
            if 1 in mm.index:
                print(f" sinlges = {mm.loc[1]}")
            else:
                print(" singles = 0")
            if 2 in mm.index:
                print(f" married = {mm.loc[2]}")
            else:
                print(" married = 0")
            df_cps_filtered = df_cps_filtered.reset_index(drop=True).reset_index(names="taxsimid")
            df_cps_filtered['taxsimid'] = df_cps_filtered['taxsimid'] + 1
            df_cps_filtered['pwages'] = df_cps_filtered['pwages']/df_cps_filtered['hhwages']*ae_m_hh*AE
            df_cps_filtered['swages'] = df_cps_filtered['swages']/df_cps_filtered['hhwages']*ae_m_hh*AE
            df_cps_filtered['hhwages'] = df_cps_filtered['pwages'] + df_cps_filtered['swages']
            df_cps_filtered = df_cps_filtered.drop(columns=["hhwages","hhwages_ae","serial","statefip"])
            df_cps_filtered.to_csv(f"TAXSIM_input_output_{cpsyear}/taxsim_input_state_{state}_year_{year}_ae_{AE:3.1f}.csv", index=False)

#%%

def make_taxsim_inputs_v1():
    df_ebs = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    state_codes = df_ebs['IRS'].unique()
    years = df_ebs['Year'].unique()

    for state in state_codes:
        for year in years[:-1]:
            aes2010 = df_ebs[ (df_ebs['IRS'] == state) & (df_ebs['Year'] == 2010) ]['per capita income'].iloc[0]
            aes = df_ebs[ (df_ebs['IRS'] == state) & (df_ebs['Year'] == year) ]['per capita income'].iloc[0]
            df_cps2010 = pd.read_csv("CPS2010.csv")
            df_cps2010['pwages'] = df_cps2010['pwages']*aes/aes2010
            df_cps2010['swages'] = df_cps2010['swages']*aes/aes2010
            df_cps2010['state'] = state
            df_cps2010['year'] = year
            df_cps2010['hhwages'] = df_cps2010['pwages'] + df_cps2010['swages']
            df_cps2010 = df_cps2010.loc[ df_cps2010['hhwages'] >= 0.5*aes ]
            df_cps2010 = df_cps2010.reset_index(drop=True).reset_index(names="taxsimid")
            df_cps2010['taxsimid'] = df_cps2010['taxsimid'] + 1
            df_cps2010 = df_cps2010.drop(columns=["hhwages","serial","statefip"])
            df_cps2010.to_csv(f"TAXSIM_input_output_v1/taxsim_input_state_{state}_year_{year}.csv", index=False)


def make_taxsim_inputs_v2():
    import pickle

    with open('fips_to_irs.pickle', 'rb') as f:
        fips_to_irs = pickle.load(f)

    with open('irs_to_statename.pickle', 'rb') as f:
        irs_to_statename = pickle.load(f)

    df_cps2010 = pd.read_csv("CPS2010.csv")
    df_cps2010['state_irs'] = df_cps2010['statefip'].map(fips_to_irs)
    df_ebs = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    state_codes = df_ebs['IRS'].unique()
    years = df_ebs['Year'].unique()

    for state in state_codes:
        state_name = irs_to_statename[state]
        for i, year in enumerate(years[:-1]):
            df_state = df_cps2010.loc[ df_cps2010['state_irs'] == state ]
            if (i == 0): 
                print(f"{len(df_state)} observations in {state_name}")
            print(f"year: {year}")
            aes2010 = df_ebs[ (df_ebs['IRS'] == state) & (df_ebs['Year'] == 2010) ]['per capita income'].iloc[0]
            aes = df_ebs[ (df_ebs['IRS'] == state) & (df_ebs['Year'] == year) ]['per capita income'].iloc[0]
            df_state['pwages'] = df_state['pwages']*aes/aes2010
            df_state['swages'] = df_state['swages']*aes/aes2010
            df_state['state'] = state
            df_state['year'] = year
            df_state['hhwages'] = df_state['pwages'] + df_state['swages']
            df_state = df_state.loc[ df_state['hhwages'] >= 0.5*aes ]
            df_state = df_state.reset_index(drop=True).reset_index(names="taxsimid")
            df_state['taxsimid'] = df_state['taxsimid'] + 1
            df_state = df_state.drop(columns=["hhwages","serial","statefip","state_irs"])
            df_state.to_csv(f"TAXSIM_input_output_v2/taxsim_input_state_{state}_year_{year}.csv", index=False)


def make_input_ae_by_state():

    df = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    state_codes = df['IRS'].unique()
    years = df['Year'].unique()

    for state in state_codes:
        dfs = df[ df['IRS'] == state ]

        csv_file1 = open(f"TAXSIM/ae_state_taxsim_input_state{state}.csv", mode="w", newline='', encoding='utf-8')
        fieldnames = ['taxsimid','year','state','mstat','page','sage','pwages','swages','depx','dep13','dep17','dep18']
        writer1 = csv.DictWriter(csv_file1, fieldnames=fieldnames)
        writer1.writeheader()

        csv_file2 = open(f"TAXSIM/ae_state_taxsim_match_taxid_state{state}.csv", mode="w", newline='', encoding='utf-8')
        fieldnames = ['taxsimid','year','state','ae_mult']
        writer2 = csv.DictWriter(csv_file2, fieldnames=fieldnames)
        writer2.writeheader()

        taxid = 1

        for year in years[:-1]:
            aes = dfs[ dfs['Year'] == year ]['per capita income']
            for mult in [0.5, 1.0, 2.0, 3.0, 5.0]:
                hh_inc = aes*mult
                marst = 1 # 1 = single, 2 = joint (married)
                depx = 0
                dep13 = 0
                dep17 = 0
                dep18 = 0

                writer1.writerow({'taxsimid': taxid, 'year': year, 'state': state, 'mstat': marst,
                                 'page': 0, 'sage': 0, 'pwages': hh_inc.iloc[0], 'swages': 0, 'depx': depx,
                                 'dep13': dep13, 'dep17': dep17, 'dep18': dep18})
                writer2.writerow({'taxsimid': taxid, 'year': year, 'state': state, 'ae_mult': mult})

                taxid += 1

        csv_file1.close()
        csv_file2.close()
        print(f"State: {state}    done")


def collect_output():

    df_sc = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    state_codes = df_sc['IRS'].unique()

    df = pd.DataFrame(columns=['IRS Code', 'Year', 'AE Mult', 'State Tax Rate'])

    for state in state_codes:
        df_state_out = pd.read_csv(f"TAXSIM/ae_state_taxsim_output_state{state}.out")
        df_state_out['taxsimid'] = df_state_out['taxsimid'].astype('int')
        df_state_out = df_state_out[['taxsimid', 'year', 'state', 'srate']]
        df_state_aemult = pd.read_csv(f"TAXSIM/ae_state_taxsim_match_taxid_state{state}.csv")
        df_state_aemult = df_state_aemult[['taxsimid', 'ae_mult']]
        df_state_out = df_state_out.merge(df_state_aemult, on=['taxsimid'])
        df_state_out = df_state_out.rename(columns={'year': 'Year', 'state': 'IRS Code', 'srate': 'State Tax Rate', 'ae_mult': 'AE Mult'})
        df_state_out = df_state_out.drop(columns=['taxsimid'])

        df = pd.concat([df, df_state_out], axis=0, ignore_index=True)

    df_irs_fips = pd.read_csv("earnings_by_state/irs_fips_merged.csv")    
    df_irs_fips = df_irs_fips[['IRS_Code', 'FIPS_Code']]
    df_irs_fips = df_irs_fips.rename(columns={'FIPS_Code': 'FIPS Code', 'IRS_Code': 'IRS Code'})
    df = df.merge(df_irs_fips, on=['IRS Code'])
    df.to_csv('StateTaxRates_by_StateAE.csv', index=False)
    
# %%
def process_output_v3():    
    df_ebs = pd.read_csv("earnings_by_state/earnings_by_state.csv")
    state_codes = df_ebs['IRS'].unique()
    state_codes = np.delete(state_codes, 0)

    with open('irs_to_statename.pickle', 'rb') as f:
        irs_to_statename = pickle.load(f)

    with open('irs_to_fips.pickle', 'rb') as f:
        irs_to_fips = pickle.load(f)

    years = list(range(1977, 2024))
    results = []
    for state in state_codes:
        for year in years:
            for ae in [0.5, 1.0, 2.0, 3.0, 5.0, 10.0]:
                df_in = pd.read_csv(f"TAXSIM_input_output_v4/taxsim_input_state_{state}_year_{year}_ae_{ae:3.1f}.csv")
                df_out = pd.read_csv(f"TAXSIM_input_output_v4/taxsim_output_state_{state}_year_{year}_ae_{ae:3.1f}.out")
                df = pd.merge(df_in, df_out, on=['taxsimid'])
                #print(df.head())
                df['gross_income'] = df['swages'] + df['pwages'] + 0.5*df['fica']
                df['net_income'] = df['gross_income'] - df['fiitax'] - df['siitax'] - df['fica']
                df['total_tax'] = df['fiitax'] + df['siitax'] + df['fica']
                df['state_tax_rate'] = df['siitax']/df['gross_income']
                df['fed_tax_rate'] = df['fiitax']/df['gross_income']
                df['fica_rate'] = df['fica']/df['gross_income']
                df['total_tax_rate'] = df['total_tax']/df['gross_income']
                tr = df['total_tax_rate'].mean()
                sr = df['state_tax_rate'].mean()
                fr = df['fed_tax_rate'].mean()
                ficar = df['fica_rate'].mean()
                fmr = df['frate'].mean() 
                smr = df['srate'].mean()
                results.append({'year': year, 'state irs': state, 'ae': ae, 'total tax rate': tr, 'state tax rate': sr, 'fed tax rate': fr, 'fica rate': ficar, 'fed mrate': fmr, 'state mrate': smr})

    df_res = pd.DataFrame(results, columns=['year','state irs','ae','total tax rate', 'state tax rate', 'fed tax rate', 'fica rate', 'fed mrate', 'state mrate'])
    df_res['state name'] = df_res['state irs'].map(irs_to_statename)
    df_res['state fips'] = df_res['state irs'].map(irs_to_fips)
    df_res.to_csv('tax_rates_ss_ae_normalized.csv', index=False)

    return 0

# %%
if __name__ == "__main__":

    import sys

    print("Program started")
    print("Script name:", sys.argv[0])
    print("Arguments:", sys.argv[1:])
    arg1 = sys.argv[1]
    #arg1 = "step_1"
    print("Argument 1 = ", arg1)
    #make_input_ae_by_state()
    #collect_output()
    #process_cps_dataset_alt()
    #make_taxsim_inputs_v1()
    #make_taxsim_inputs_v2()

    if arg1 == "step_1":
        process_cps_dataset_alt(2005)
    elif arg1 == "step_2":
        for (AE, AE_cut) in [(0.5,0.5), (1.0,1.0), (2.0,2.0), (3.0,3.0), (5.0,5.0), (10.0,5.0)]:
            print(f"AE = {AE}, AE_cut = {AE_cut}")
            make_taxsim_inputs_v3(AE=AE, AE_cut=AE_cut, cpsyear=2005)
    elif arg1 == "step_3":
        process_output_v3()
    else:
        print("Intended usage: python gen_taxsim_ae.inputs.py [arg1]")
        print(" where [arg1] is [step_1] or [step_3]")
    
    print("End of program")


# %%
