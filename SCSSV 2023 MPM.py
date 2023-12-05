import pandas as pd
import numpy as np
import os
from tqdm import tqdm #for progress bar
import streamlit as st

def getWellName5(dfUPD,colName,minCount=5):
    # usage==> getWellName5(dfUPD,'Well', 5)
    wellName_Accepted=dfUPD[colName].value_counts().rename_axis(colName)
    wellName_Accepted = wellName_Accepted.to_frame()
    wellName_Accepted.rename(columns ={colName:'Freq'}, inplace= True)
    filt = (wellName_Accepted['Freq']>=minCount)
    wellName_Accepted=wellName_Accepted.loc[filt]
    wellName_Accepted.reset_index(inplace=True)
    wellName_accepted=wellName_Accepted[colName]
    wellName_freq = list(wellName_Accepted['Freq'])
    wellName_accepted= list(wellName_accepted)
    return wellName_accepted, wellName_freq
    
def getUPD_Accepted(dfUPD, colName, minCount=5):
    wellName_Accepted, Freq = getWellName5(dfUPD,colName,minCount=minCount)
    # print(f"wellName_Accepted={wellName_Accepted}")
    # print(f"Freq={Freq}")
    filt = dfUPD[colName].isin(wellName_Accepted)
    return dfUPD.loc[filt] , wellName_Accepted , Freq  #<-- columns to be collected
    
# dfUPD_Accepted, WellName, Freq = getUPD_Accepted(dfUPD, 'WELL', minCount = 5)

# pd.set_option('display.max_rows',81)
def getPredictorLabel(SheetName, excelObj):
    if 'PCP' in SheetName:
        colLabelPI = 'PCP'
    elif 'CHP' in SheetName:
        colLabelPI = 'CHP'    
    elif 'THP' in SheetName:
        colLabelPI = 'THP'
    elif 'THT'  in SheetName:
        colLabelPI = 'THT'        
    elif 'ICP' in SheetName:
        colLabelPI = 'ICP'
    df = excelObj.parse(SheetName)     # this takes time to complete !!!
    df.drop([0,1,2,3,5], axis=0, inplace= True)
    df.columns = df.iloc[0]
    df.drop([4],axis =0, inplace=True)
    df.rename(columns={"Well No":"Date"}, inplace=True)
    df.reset_index(inplace = True, drop=True)   
    return df, colLabelPI# dfUPD_Accepted['WELL'].value_counts()

def getUnPivotPI(df,colLabelPI,WellNameUPD):
    colNames = df.columns[1:]

    #UNPIVOT BigData
    #---------------
    dfUnpiv= pd.DataFrame()
    pbar = tqdm(total = len(colNames)) #progress bar
    ctrWELL = 0
    for col in colNames:  # iterate well name, unpivot
        pbar.update(1)
        if col in WellNameUPD:
            ctrWELL += 1
            dftemp = df.loc[:,['Date', col]]
            dftemp["Well"]=col
            dftemp.rename(columns={col:colLabelPI}, inplace=True)
            dfUnpiv = pd.concat([dfUnpiv,dftemp], ignore_index=True)
    pbar.close()
    print(f"ctrWELL={ctrWELL}")
    print(f"-----------------------------")
    
    dfUnpiv['Date'] = pd.to_datetime(dfUnpiv['Date'])
    #extract Date and time
    dfUnpiv["newDate"] = dfUnpiv['Date'].dt.date
    dfUnpiv["Time"] = dfUnpiv['Date'].dt.hour
    
    dfUnpiv.drop(['Date'], axis=1, inplace =True)
    dfUnpiv.rename(columns={'newDate':'Date'}, inplace =True)
    dfUnpiv['Date']=pd.to_datetime(dfUnpiv['Date'])
#     dfPCP = dfUnpiv.groupby('Time').get_group(0).copy()
    dfUnpiv = dfUnpiv.groupby('Time').get_group(0) #Return daily PI Data at time =0
    dfUnpiv.reset_index(inplace=True, drop=True)
    return dfUnpiv 

root_path = 'C:/Users/jale_ahmad/Downloads/2023/SCSSV/P2/Data/'
dfUPD = pd.read_excel('C:/Users/jale_ahmad/Downloads/2023/SCSSV/P2/Data/Dulang/UPD/Latest Dulang UPD.xlsx', parse_dates=['OPNS DATE'])
dfUPD.rename(columns={'OPNS DATE':'Date'}, inplace= True)

dfUPD_Accepted, WellNameUPD, Freq = getUPD_Accepted(dfUPD, 'WELL', minCount = 1)

#-----
# GUI
#-----
st.title("SCSSV 2023 Ver 2.0")
st.sidebar.image("logos/pet.jpg",width =100)
st.sidebar.title("Configuration")



# st.sidebar.header("Platforms")
# text = st.sidebar.text_area("Paste Well Name Here")

# bar_col1, bar_col2= st.sidebar.columns(2)
# bar_col1= st.sidebar.columns(1)

# platform = st.sidebar.selectbox("Platforms",
                                # ("Dulang","Samarang","Bokor","TapisC"))

form1 = st.sidebar.form(key="Options")
platform = form1.radio("Platforms",
                        ["Dulang","Samarang","Bokor","TapisC"])
btnReadUPD = form1.form_submit_button("Read UPD File")
if btnReadUPD:
    #st.sidebar.write(f"{platform}")
    WellSelected = st.sidebar.selectbox(f"{platform} Wells",WellNameUPD)
    



                                # ("Dulang","Samarang","Bokor","TapisC"))


# platform = bar_col2.selectbox("Platforms",
                                # ("Dulang","Samarang","Bokor","TapisC"))
# platform = st.sidebar.radio("Platforms",
#                                 ("Dulang","Samarang","Bokor","TapisC"))

col1, col2 = st.columns(2)

col1_expander = col1.expander(f"Viz {platform} UPD Data")
with col1_expander :
    col1_expander.write(f"{platform} UPD Data")

col2_expander = col2.expander(f"Viz {platform} PI Data")
with col2_expander:
    col2_expander.write(f"{platform} PI Data")

# button1 = st.sidebar.button("Read UPD Data")
# if button1:
    # col1, col2 = st.columns(2)
    # col1_expander = col1.expander("Viz UPD Data")
    # with col1_expander :
    #     col1_expander.write("UPD Data")
    # col2_expander = col2.expander("Viz PI Data")
    # with col2_expander:
    #     col2_expander.write("PI Data")

# options = st.sidebar.multiselect("Animals",["Lion","Tiger","Bear"])

# button5 = st.sidebar.button("Submit Animal")
# if button5:
#     st.write(options)
