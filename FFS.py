#!/usr/bin/env python
# coding: utf-8

# In[147]:


import pandas as pd
import numpy as np


# ## Data EDA

# In[148]:


#This dataset is super large, need to set low_memory=False, took aroud 30 min to run this line
#Only import relevant columns
fields = ['Rndrng_NPI','Rndrng_Prvdr_Mdcr_Prtcptg_Ind','HCPCS_Cd','Tot_Srvcs','Avg_Sbmtd_Chrg']
df = pd.read_csv("Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2019.csv",encoding='latin-1', low_memory=False, usecols=fields)


# In[149]:


df.head()


# In[150]:


#read the em_code file
em=pd.read_csv("EM_code.csv",encoding='utf-8')
#remove that weird \xa0 thing at the end
em['em_code'] = em['em_code'].apply(lambda x: str(x).replace(u'\xa0', u''))


# In[151]:


#Summary of null values
df.isnull().sum(axis = 0)


# In[152]:


# create a new column for total FFS revenue

df['Total_FFS_Rev'] = df['Tot_Srvcs'] * df['Avg_Sbmtd_Chrg']


# In[153]:


df.head()


# In[154]:


# add a column to indicate if a service is E&M, 0 = no, 1 = yes
df['EM_indicator'] = np.where(df["HCPCS_Cd"].isin(em['em_code']), "1", "0")


# In[155]:


# quick check
df.loc[df['HCPCS_Cd'] == '96160']


# In[156]:


# count values
df['EM_indicator'].value_counts()


# In[157]:


df.head(15)


# In[158]:


#get the sum of FFS revenue, group by NPI

df['npi_total_ffs_rev'] = df['Total_FFS_Rev'].groupby(df['Rndrng_NPI']).transform('sum')


# In[159]:


df.head(15)


# In[160]:


# add a column for EM revenue
df['em_rev'] = np.where(df["EM_indicator"]=='0', "0", df['Total_FFS_Rev'])


# In[161]:


df['em_rev'] = df['em_rev'].astype(float)
df['npi_total_ffs_rev'] = df['npi_total_ffs_rev'].round()


# In[163]:


# add a column for sum of EM revenue, group by NPI
df['npi_total_em_rev'] = df['em_rev'].groupby(df['Rndrng_NPI']).transform('sum')


# In[165]:


# only keeping the first record for each NPI
df_summary = df.drop_duplicates(subset=['Rndrng_NPI'], keep='first')


# In[169]:


#drop unrelevant columns
df_summary_final = df_summary.drop(columns=['Rndrng_Prvdr_Mdcr_Prtcptg_Ind', 'HCPCS_Cd','Tot_Srvcs','Avg_Sbmtd_Chrg','Total_FFS_Rev','EM_indicator','em_rev'])


# In[172]:


# add a column for % EM revenue
df_summary_final['%npi_total_em_rev'] = (df_summary_final['npi_total_em_rev']/df_summary_final['npi_total_ffs_rev'])*100


# In[177]:


# add a column for % non-EM revenue
df_summary_final['%non_npi_total_em_rev'] = 100-(df_summary_final['npi_total_em_rev']/df_summary_final['npi_total_ffs_rev'])*100


# In[179]:


df_summary_final['npi_total_em_rev'] = df_summary_final['npi_total_em_rev'].round()
df_summary_final['%npi_total_em_rev'] = df_summary_final['%npi_total_em_rev'].round()
df_summary_final['%non_npi_total_em_rev'] = df_summary_final['%non_npi_total_em_rev'].round()


# In[183]:


df_summary_final.rename(columns={'Rndrng_NPI': 'npi'}, errors="raise")


# In[185]:


df_summary_final.to_csv('/Users/zoey/Desktop/FFS/ffs_breakdown.csv',index=False)


# FFS income = capitation amount (E&M)  + non-PQEM (non-direct contracting, paid FFS) services
# 
# The average % of total FFS revenue that is covered by capitation amount (E&M) is only 16.2%. 
# 83.8% of the total FFS revenue is not covered by the capitation amount - the providers will continue to pay this amount FFS if they join a DCE/REACH. 
# 
# In short, it makes sense that our capitation estimate is lower than their total FFS income since as it is only 16.2% of the total.

# In[202]:


df_summary_final['npi_total_ffs_rev'].sum()


# In[203]:


df_summary_final['npi_total_em_rev'].sum()


# In[207]:


# % of total capitation amount 
(56041729985.0/345362320367.0)*100

