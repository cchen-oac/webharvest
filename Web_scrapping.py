# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import streamlit as st
from streamlit.logger import get_logger
import matplotlib.pyplot as plt
import pandas as pd
#import urllib.request as url
from bs4 import BeautifulSoup
import openpyxl
from zipfile import ZipFile
import requests
from io import BytesIO
import re

##Defining functions
#Check that the website is allowed for acces
#<Response [200]>#means able to access
#url = "https://www.bankofengland.co.uk/prudential-regulation/key-initiatives/solvency-ii/technical-information"
@st.cache_data
def check_acess(url):
    #Initially access was denied without using hdr settings, set up below setting for access
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (Kpng, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/png,application/xpng+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}
    response = requests.get(url, headers=hdr)
    if response.status_code == 200:
        notification = "Access to URL is granted!"
    else:
        notification = "Access to URL is denied!, please input a different link!"
    return notification    

#Load all available csv from url and list out all dataset names
@st.cache_data
def load_dataset(html):
    html = requests.get(url)    
    #parse html info
    soup = BeautifulSoup(html.text, 'html.parser')

    #list of file extensions interested in
    file_extensions = ['.xlsx', '.csv', '.pdf']

    #extract all links available from html and their names
    names = []
    hrefs = []
    for i in soup.find_all('a'):
        link = i.get('href')
        name = i.text.strip()  # remove leading/trailing white spaces
        if link and any(link.endswith(ext) for ext in file_extensions):    # Only add link and name to the list if link is not None and ends with any of the file extensions
            names.append(name)
            hrefs.append(link)

    #Combine both name and refs as dictionary
    dict = {'names': names, 'hrefs': hrefs}
    df = pd.DataFrame(dict).sort_values(by=['names']).reset_index(drop=True)
    return df

def group_files(df):
# Loop through rows of dataframe
    file_extension = []
    for index, row in df.iterrows():
            matches = row['hrefs'].rsplit('.', 1)[-1] #Extact file suffix to get file types, use regex backward
            file_extension.append(matches)
    file_extension = pd.DataFrame(file_extension).drop_duplicates()
    return(file_extension)







#Display whether we can webscrap from this link
if url:
  #User has inputted a URL
  st.write(check_acess(url))
  full_df = load_dataset(url)
  csv_df = pd.DataFrame(display_dataset(full_df))

  # Let the user select from the dataframe indices
  selected_names = st.multiselect('Select rows:', full_df.Name)
  selected_rows = full_df[full_df['Name'].isin(selected_names)]

  # Display the selected rows
  st.write('### Selected Rows')
  st.dataframe(selected_rows)
  downloaded_data = get_data(selected_rows)
  downloaded_data
  #downloaded_data[downloaded_data['Name'].isin(selected_names)]

else:
    # The user has not inputted a URL    
  st.write("Please input an URL above")