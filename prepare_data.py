"""
prepare_data.py
Prepares Public Health Scotland delayed discharge open data for Power BI.

Steps:
1. Read the bed days (by council area) and census (by health board) files.
2. Remove pre-calculated totals ("All Delay Reasons", "18plus", Scotland rows)
   so Power BI rebuilds totals with measures and never double-counts.
3. Replace area codes with names using the PHS geography lookups.
4. Build small lookup tables (date, reason, age group).

Source: Public Health Scotland, Delayed Discharges in NHSScotland.
Contains public sector information licensed under the Open Government Licence v3.0.
"""
import pandas as pd
# Folder containing the four CSV files downloaded from opendata.nhs.scot
U='raw/'
b=pd.read_csv(U+'2026-08_delayed-discharge-beddays-council-area.csv',dtype={'MonthOfDelay':str})
c=pd.read_csv(U+'2026-08_delayed-discharge-census-health-board.csv',dtype={'MonthOfDelay':str})
hb=pd.read_csv(U+'hb14_hb19.csv',dtype=str); ca=pd.read_csv(U+'ca11_ca19.csv',dtype=str)
O='data/'  # cleaned output files for Power BI
import os; os.makedirs(O,exist_ok=True)
age={'18-74':'18-74','75plus':'75+'}
rs=['Health and Social Care Reasons','Patient and Family Related Reasons','Code 9 AWI','Code 9 Non-AWI']
def date(m): return pd.to_datetime(m+'01',format='%Y%m%d')
fb=b[(b.CA!='S92000003')&b.AgeGroup.isin(age)&b.ReasonForDelay.isin(rs)].copy()
fb['Date']=date(fb.MonthOfDelay).dt.strftime('%Y-%m-%d'); fb['CouncilAreaCode']=fb.CA.fillna('UNKNOWN')
fb['AgeGroup']=fb.AgeGroup.map(age); fb=fb.rename(columns={'ReasonForDelay':'ReasonGroup','NumberOfDelayedBedDays':'BedDays'})
fb[['Date','CouncilAreaCode','AgeGroup','ReasonGroup','BedDays']].to_csv(O+'fact_bed_days.csv',index=False)
fc=c[(c.HBT!='S92000003')&c.AgeGroup.isin(age)&c.ReasonForDelay.isin(rs)].copy()
fc['Date']=date(fc.MonthOfDelay).dt.strftime('%Y-%m-%d'); fc['AgeGroup']=fc.AgeGroup.map(age)
fc=fc.rename(columns={'HBT':'HealthBoardCode','ReasonForDelay':'ReasonGroup','NumberOfCensusDelays':'CensusDelays'})
fc[['Date','HealthBoardCode','AgeGroup','ReasonGroup','CensusDelays']].to_csv(O+'fact_census_delays.csv',index=False)
cur=ca.sort_values('HSCPDateEnacted').drop_duplicates('CA',keep='last')
dca=cur[['CA','CAName','HSCPName','HBName']].rename(columns={'CA':'CouncilAreaCode','CAName':'CouncilArea','HSCPName':'HSCP','HBName':'HealthBoard'})
dca=dca[dca.CouncilAreaCode.isin(fb.CouncilAreaCode)]
dca=pd.concat([dca,pd.DataFrame([{'CouncilAreaCode':'UNKNOWN','CouncilArea':'Not known','HSCP':'Not known','HealthBoard':'Not known'}])])
dca.sort_values('CouncilArea').to_csv(O+'dim_council_area.csv',index=False)
dhb=hb[hb.HB.isin(fc.HealthBoardCode)][['HB','HBName']].rename(columns={'HB':'HealthBoardCode','HBName':'HealthBoard'})
dhb.sort_values('HealthBoard').to_csv(O+'dim_health_board.csv',index=False)
print('CA codes',fb.CouncilAreaCode.nunique(),'dim',len(dca),'missing',set(fb.CouncilAreaCode)-set(dca.CouncilAreaCode), 'dup',dca.CouncilAreaCode.duplicated().sum())
print('HB codes',fc.HealthBoardCode.nunique(),'dim',len(dhb),'missing',set(fc.HealthBoardCode)-set(dhb.HealthBoardCode))
pd.DataFrame({'ReasonGroup':rs,'ReasonShort':['Health & social care','Patient & family','Adults with Incapacity (Code 9)','Other complex (Code 9)'],
 'Description':['Waiting for health or social care arrangements, for example an assessment, a care home place or a home care package.',
 'Related to the patient, family or carer, for example disagreement about care home choice, or legal and financial matters.',
 'Complex cases where the person lacks capacity and a legal process under the Adults with Incapacity (Scotland) Act 2000 is needed.',
 'Other complex cases, for example waiting for a specialist facility where no suitable place is available.'],'SortOrder':[1,2,3,4]}).to_csv(O+'dim_reason.csv',index=False)
pd.DataFrame({'AgeGroup':['18-74','75+'],'SortOrder':[1,2]}).to_csv(O+'dim_age_group.csv',index=False)
d=pd.DataFrame({'Date':pd.date_range('2016-07-01','2026-08-01',freq='MS')})  # one row per month
d['Year']=d.Date.dt.year; d['MonthNumber']=d.Date.dt.month; d['Month']=d.Date.dt.strftime('%b'); d['YearMonth']=d.Date.dt.strftime('%b %Y')
d['YearMonthSort']=d.Year*100+d.MonthNumber; d['DaysInMonth']=d.Date.dt.days_in_month
f=d.Year.where(d.MonthNumber>=4,d.Year-1); d['FinancialYear']=f.astype(str)+'/'+((f+1)%100).astype(str).str.zfill(2)
d.insert(6,'MonthIndex',range(1,len(d)+1))
d['Date']=d.Date.dt.strftime('%Y-%m-%d'); d.to_csv(O+'dim_date.csv',index=False)
