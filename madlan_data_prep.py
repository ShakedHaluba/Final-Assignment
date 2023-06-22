# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 15:38:03 2023

@author: noyha
"""

import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import re

#excel_file = 'output_all_students_Train_v10.xlsx'
#dataframe= pd.read_excel(excel_file)

def price(dataframe):
    dataframe['price']=dataframe['price'].astype(str)
    dataframe['price']=dataframe['price'].apply(lambda x: re.sub('[^\d\.]+','', x))
    dataframe['price'] = pd.to_numeric(dataframe['price'], errors='coerce').dropna().astype(int)
    dataframe=dataframe.dropna(subset = ['price'] ,axis=0, inplace=True)
    
def Area(dataframe):
    dataframe['Area']= dataframe['Area'].astype(str)
    dataframe['Area'] = dataframe['Area'].apply(lambda x: re.sub('[^\d\.]+','', x))
    dataframe['Area'] =pd.to_numeric(dataframe['Area'], errors='coerce')
    dataframe['Area']=dataframe['Area'].replace(1000, np.nan)
    dataframe['Area'] = dataframe['Area'].replace('', np.nan)
    group_means = dataframe.groupby(['City', 'room_number'])['Area'].transform('mean').round()
    dataframe['Area'] = dataframe['Area'].fillna(group_means)
    dataframe.dropna(subset=['Area'], inplace=True)
    
def clean_pun(dataframe):
    columns_to_replace = ['Street', 'city_area', 'furniture ','condition ', 'description ']
    dataframe[columns_to_replace] = dataframe[columns_to_replace].replace(r'[^\w\s]','', regex=True)
    for index, row in dataframe.iterrows():
        dataframe.loc[index, 'City'] = row['City'].strip()
    dataframe['City']=dataframe['City'].replace(' נהרייה','נהריה')
    dataframe['City']=dataframe['City'].replace('נהרייה','נהריה')
    dataframe['City']=dataframe['City'].replace(' שוהם','שוהם')
    dataframe['City']=dataframe['City'].replace('שוהם','שוהם')
    
def floor_totalFloor(dataframe):
    for index, row in dataframe.iterrows():
        floor_value = row['floor_out_of']
        if pd.isna(floor_value):
            continue
        floors = str(floor_value).lstrip().split(" ")
        try:
            if 'מרתף' in floors:
                dataframe.at[index, 'floor'] = '-1'
                dataframe.at[index, 'total_floors'] = '0'
            elif 'קרקע' in floors:
                dataframe.at[index, 'floor'] = '0'
                dataframe.at[index, 'total_floors'] = '0'
            else:
                dataframe.at[index, 'floor'] = floors[1]
                dataframe.at[index, 'total_floors'] = floors[-1]
        except IndexError:
            pass
    dataframe['total_floors'] = dataframe['total_floors'].replace('', '0')
    dataframe['floor'] = dataframe['floor'].fillna(value=0).astype(float)
    dataframe['total_floors'] = dataframe['total_floors'].fillna(value=0).astype(float)
    
def update_entrance_date(dataframe):
    for index, row in dataframe.iterrows():
        val = row['entranceDate ']
        try:
            entrance_time = (val - datetime.now()).days
            if entrance_time < 183:
                dataframe.at[index, 'entrance_date'] = 'less_than_6_months'
            elif entrance_time > 365:
                dataframe.at[index, 'entrance_date'] = 'above_year'
            else:
                dataframe.at[index, 'entrance_date'] = 'months_6_12'
        except:
            if pd.isna(val) or "לא צויין" in val or val == False:
                dataframe.at[index, 'entrance_date'] = "not_defined"
            if "גמיש" in val or "flexible" in val:
                dataframe.at[index, 'entrance_date'] = "flexible"
            if "מיידי" in val or "immediate" in val:
                dataframe.at[index, 'entrance_date'] = "less_than_6_months"
    dataframe=dataframe.drop(columns=['entranceDate '], axis=1, inplace = True)
 
def replace_values(dataframe, columns_dict):
    for col, value_dict in columns_dict.items():
        try:
            dataframe[col] = dataframe[col].replace(value_dict)#.astype(float)
            dataframe[col] =  dataframe[col].fillna(value=0)#.astype(float)
        except:
            continue    
    
def room_number(dataframe):
    dataframe['room_number'] = dataframe['room_number'].astype(str)
    dataframe['room_number'] = dataframe['room_number'].apply(lambda x: re.sub(r'[^\d.]', '', x))
    dataframe['room_number'] = dataframe['room_number'].replace('', np.nan)
    dataframe['room_number'] = dataframe['room_number'].astype(float)
    dataframe.loc[dataframe['room_number'] > 10, 'room_number'] = np.nan
    dataframe['room_number'].fillna(0.0, inplace=True)    

def prepare_data(dataframe):
    price(dataframe)
    Area(dataframe)
    clean_pun(dataframe)
    floor_totalFloor(dataframe)
    update_entrance_date(dataframe)
    columns_dict = {
    'hasElevator ': { True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'לא': '0', 'כן':'1', 'אין מעלית':'0', 'יש מעלית':'1', 'אין':'0', 'יש':'1'   
    },
    
    'hasParking ': { True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no':'0', 'יש':'1' , 'אין':'0' , 'יש חניה':'1', 'אין חניה':'0', 'יש חנייה':'1', 'כן':'1' ,'לא':'0'  
    },
    
    'hasBars ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'לא': '0', 'כן':'1', 'אין סורגים':'0', 'יש סורגים':'1', 'אין':'0', 'יש':'1'      
    },
    
    'hasStorage ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'לא': '0', 'כן':'1', 'אין מחסן':'0', 'יש מחסן':'1', 'אין':'0', 'יש':'1'   
    },
    
    'hasAirCondition ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'יש מיזוג אוויר':'1', 'לא': '0', 'כן':'1', 'אין מיזוג אויר':'0', 'יש מיזוג אויר':'1', 'אין':'0', 'יש':'1'
    },
    
    'hasBalcony ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'לא': '0', 'כן':'1', 'אין מרפסת':'0', 'יש מרפסת':'1', 'אין':'0', 'יש':'1'   
    },
    
    'hasMamad ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'יש ממ"ד':'1', 'לא': '0', 'כן':'1', 'אין ממ״ד':'0', 'יש ממ״ד':'1', 'אין':'0', 'יש':'1', 'אין ממ"ד':'0'     
    },
    
    'handicapFriendly ':{True:'1', False:'0', 'TRUE': '1', 'FALSE': '0', 'yes': '1', 'no': '0', 'לא': '0', 'כן':'1', 'לא נגיש':'0', 'נגיש':'1', 'לא נגיש לנכים':'0', 'נגיש לנכים':'1'      
    },
    'condition ':{None:'לא צויין', False:'לא צויין', 'ישן':'דורש שיפוץ'
    },
    'type': {"מיני פנטהאוז":'פנטהאוז' , "קוטג' טורי":"קוטג'"
    }
}
    dataframe['condition '] = dataframe['condition '].replace(['None', False], 'לא צויין')
    dataframe['condition '] = dataframe['condition '].replace('דורש שיפוץ', 'ישן')
    replace_values(dataframe, columns_dict)
    room_number(dataframe)
    values_to_drop = ['טריפלקס', 'בניין', 'אחר', 'מגרש', 'דירת נופש','נחלה']
    dataframe = dataframe.drop(dataframe[dataframe['type'].isin(values_to_drop)].index)
    dataframe.drop(['number_in_street','Street','city_area','num_of_images','publishedDays ','description ','floor_out_of','hasAirCondition ', 'condition ', 'floor', 'total_floors', 'handicapFriendly ', 'hasElevator ','hasBars ','furniture ','hasStorage ','hasBalcony ','hasMamad ','entrance_date'], axis = 1, inplace = True)
    dataframe.columns = dataframe.columns.str.strip()
    return dataframe
