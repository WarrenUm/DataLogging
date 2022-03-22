import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm.notebook import tqdm_notebook
import time
import os


def load_raw_data(file):
    '''Load raw data, set column names, make code and acceleration dataframes'''
    df = pd.read_csv(file,header=None)
    df.columns = ['time','code','value']
    
    times_list = df['time'].unique()

    codes = pd.DataFrame(index=times_list,columns=['10C', '10D', '111', '104', '24', '11', '10', 'A', 'B', 'C', 'D', 'F'])

    acc = pd.DataFrame(index=times_list,columns=['acc1','acc2','acc3','acc4'])
    
    return df, codes, acc, times_list

def first_process(df, times_list, codes, acc):
    '''Sorts data into two dataframes'''
    for time in tqdm_notebook(times_list):

        accel = 1
        timedf = df.loc[df['time'] == time].copy().reset_index()
        for row, val in enumerate(timedf['code']):

            if val == '20':
                #put in other dataframe
                acc['acc' + str(accel)][time] = timedf['value'][row]
                accel = accel + 1
            else:
                codes[val][time] = timedf['value'][row]
                
    return df, times_list, codes, acc

def map_codes(conv_codes):
    '''Maps codes to readable values'''
    
    code_map = {'104':'engine_load','10C':'rpm','10D':'speed','111':'throt_pos','24':'bat_volt','11':'utcdate','10':'utctime',
            'A':'lat','B':'long','C':'alt','D':'speed_kmph','F':'n_sats'}
    
    conv_codes.columns = conv_codes.columns.map(code_map)
    
    return conv_codes

def obd_cleaner(conv_codes):
    
    '''Cleans up and makes dataframe of obd data'''
    
    obd_data = conv_codes[['rpm','speed','throt_pos','engine_load','bat_volt']]
    
    obd_data = obd_data.dropna(how='all')
    
    obd_data['rpm'] = obd_data['rpm'].astype('float',errors='ignore')
    obd_data['speed'] = obd_data['speed'].astype('float',errors='ignore')
    obd_data['bat_volt'] = obd_data['bat_volt'].astype('float',errors='ignore')


    #convert to mph
    obd_data['speed'] = obd_data['speed'] * 0.621371
    #bat volt
    obd_data['bat_volt'] = obd_data['bat_volt'] / 100
    
    return obd_data

def gps_cleaner(conv_codes):
    
    '''Cleans and makes dataframe for gps data'''
    
    gps_data = conv_codes[['utcdate','utctime','lat','long','alt','speed_kmph','n_sats']]
    
    gps_data['lat'] = gps_data['lat'].astype('float',errors='ignore')
    gps_data['long'] = gps_data['long'].astype('float',errors='ignore')
    gps_data['speed_kmph'] = gps_data['speed_kmph'].astype('float',errors='ignore')
    gps_data['speed_kmph'] = gps_data['speed_kmph'] * 0.621371

    gps_data.rename(columns={'speed_kmph':'speed_mph'},inplace=True)

    #div lat and long my 1mil to get right number
    gps_data['lat'] = gps_data['lat'] / 1000000
    gps_data['long'] = gps_data['long'] / 1000000
    
    gps_data = gps_data.dropna(how='all')
    
    return gps_data

def gps_datetime_format(gps_data):
    
    '''Handles datetime formating'''
    
    #get utc date
    utc_date_format = '%d%m%y'
    utc_time_format = '%H%M%S%f'

    #apply formats
    gps_data['utcdate'] = pd.to_datetime(gps_data['utcdate'].iloc[0],format=utc_date_format)
    
#     date = pd.to_datetime(gps_data['utcdate'].iloc[0],format=utc_date_format)

    gps_data['utcdate'] = gps_data['utcdate'].iloc[0]
    
    gps_data['utctime'] = pd.to_datetime(gps_data['utctime'],format=utc_time_format,errors='coerce')
    
    gps_data['utctime'] = pd.DatetimeIndex(gps_data['utctime']).time
    
    return gps_data

def trip_organizer(gps_data, acc, obd_data, trip_count, remove_location=True):
    
    '''Places each set of dataframes into the same folder labeled with the start date and time. Saves all three dataframes inside.'''
    
    #add duration column to each dataframe
    gps_data['duration'] = gps_data.index
    acc['duration'] = acc.index
    obd_data['duration'] = obd_data.index

    
    #add trip count to each df
    gps_data['trip_id'] = trip_count
    acc['trip_id'] = trip_count
    obd_data['trip_id'] = trip_count

    
    #reset indices
    gps_data.reset_index(drop=True,inplace=True)
    acc.reset_index(drop=True,inplace=True)
    obd_data.reset_index(drop=True,inplace=True)

    #add date to other dfs
    acc['utcdate'] = gps_data['utcdate'].iloc[0]
    obd_data['utcdate'] = gps_data['utcdate'].iloc[0]
    
    time_str = str(gps_data['utctime'][gps_data.index[0]])
    hour = time_str[:2]
    minute = time_str[3:5]
    second = time_str[6:8]
    
    date_str = str(gps_data['utcdate'][gps_data.index[0]])[:10]
    
    if remove_location==True:
        folder_path = 'Converted/' + date_str + '__' + hour + '-' + minute + '-' + second + '_sans_location'
        gps_data.drop(labels=['lat','long'],axis=1,inplace=True)
    else:
        folder_path = 'Converted/' + date_str + '__' + hour + '-' + minute + '-' + second

    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    gps_data.to_csv(f'{folder_path}/gps_data_{date_str}.csv')
    acc.to_csv(f'{folder_path}/acc_data_{date_str}.csv')
    obd_data.to_csv(f'{folder_path}/obd_data_{date_str}.csv')
    
    return gps_data, acc, obd_data
    
def add_gps_item(conn, gps):
    query = """INSERT INTO gps_data (trip_id, alt, speed_mph, n_sats, duration, date, time) VALUES(?,?,?,?,?,?,?)"""
    
    cur = conn.cursor()
    cur.execute(query, gps)
    conn.commit()
    return cur.lastrowid

def add_gps_data(conn, gps_df):
    
    for row in range(0,len(gps_df)):
        trip_id = int(gps_df.iloc[row]['trip_id'])
        alt = int(gps_df.iloc[row]['alt'])
        speed = float(gps_df.iloc[row]['speed_mph'])
        sats = int(gps_df.iloc[row]['n_sats'])
        duration = int(gps_df.iloc[row]['duration'])
        date = str(gps_df.iloc[row]['utcdate'])
        time = str(gps_df.iloc[row]['utctime'])
        
        gps_data = (trip_id,alt,speed,sats,duration,date,time)
        add_gps_item(conn, gps_data)
        
    conn.close()