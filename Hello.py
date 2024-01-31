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

#Import libraries
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
from openpyxl import load_workbook
import os

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
def load_dataset(url):
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
        if link and any(link.endswith(ext) for ext in file_extensions):    # Only add link and name to the list if link is not None and ends with any of the file extensions
            if not link.startswith('https'):
                link = url + link   
            name = i.text.strip()  # remove leading/trailing white spaces
            names.append(name)
            hrefs.append(link)
    #Combine both name and refs as dictionary
    data_dict = {'Name': names, 'hrefs': hrefs}
    df = pd.DataFrame(data_dict).sort_values(by=['Name']).reset_index(drop=True)
    return df

#Display the available file names
@st.cache_data
def display_dataset(df):
    dataset_name = df['Name']
    return dataset_name

#User can select the file types
@st.cache_data
def group_files(df):
# Loop through rows of dataframe
    file_extension = []
    for index, row in df.iterrows():
            matches = row['hrefs'].rsplit('.', 1)[-1] #Extact file suffix to get file types, use regex backward
            file_extension.append(matches)
    file_extension = pd.DataFrame(file_extension, columns=['Name']).drop_duplicates()
    return(file_extension)

#Download the selected file
@st.cache_data
def get_file_type(file_url):
    return file_url.rsplit('.', 1)[-1] #Extact file suffix to get file types, use regex backward

@st.cache_data
def print_tab_names(file_paths):
    tab_names = []
    for file_path in file_paths:
        # Set up the headers to avoid access denied
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (Kpng, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/png,application/xpng+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
        response = requests.get(file_path,  headers=hdr)
        assert response.status_code == 200, 'Download failed'
        file_name = os.path.basename(file_path)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        xls = pd.ExcelFile(file_name)
        tab_names.extend(xls.sheet_names)
        os.remove(file_name)  # remove the file after reading it
    return tab_names

def read_file(file_url, tab_name, rows):
    extension = get_file_type(file_url)
    if extension == 'csv':
        return pd.read_csv(file_url, low_memory=False)
    elif extension == 'xlsx':
        return pd.read_excel(file_url, tab_name, skiprows=rows)
    elif extension == 'pdf':
        # Process PDF files
        # need a library like PyPDF2 or PDFMiner to read PDF files
        pass
    else:
        print(f'Unsupported file type: {extension}')
        return None

#Download the selected sheet data
def get_data(selected_rows, tab_name, rows):
    downloaded_data = {}
    for Name in selected_rows['Name']:
        file_url = selected_rows.loc[selected_rows['Name'] == Name, 'hrefs'].values[0]
        downloaded_data[Name] = read_file(file_url, tab_name, rows)
    return downloaded_data




def find_largest_nonmissing_block(data):
    largest_block_data = {}
    for key, df in data.items():
        largest_block = ''
        max_block_size = 0
        for column in df.columns:
            # Skip 'Unnamed' columns and columns with all null values
            if column.startswith('Unnamed') or df[column].isnull().all():
                continue

            # Drop null values and get the index of the remaining values
            non_null_indices = df[column].dropna().index

            if not non_null_indices.empty:
                # Find the largest continuous block of non-missing values
                blocks = [(start, end) for start, end in zip(non_null_indices, non_null_indices[1:]) if start+1 != end]
                blocks.append((non_null_indices[-1], non_null_indices[-1]))
                
                # Get the largest block
                largest_block_in_column = max(blocks, key=lambda block: block[1] - block[0])
                block_size = largest_block_in_column[1] - largest_block_in_column[0]

                # If this block is larger than the largest block so far, update the largest block
                if block_size > max_block_size:
                    max_block_size = block_size
                    # Convert the row indices to Excel-style cell references
                    min_cell = f'{column}{largest_block_in_column[0] + 1}'
                    max_cell = f'{column}{largest_block_in_column[1] + 1}'
                    largest_block = f'{min_cell}:{max_cell}'

        # Store the largest block in the dictionary
        largest_block_data[key] = largest_block
    return largest_block_data






#manipulate data   
@st.cache_data
def data_manipulate(myrange1):
    #data is saved as a dictionary, so need to loop through each dataframe
    for key, df in myrange1.items():
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #remove unnamed columns
        df = df.iloc[1: , :] #remove first row #######This will need chaning depending on the file layout#######
        df.reset_index(drop=True,inplace = True)
        df.rename(columns={"Dampener final": "SymAdj"},inplace = True) #rename column ####This needs changing as well########
        df['Date'] = pd.to_datetime(df['Calendar day'], format='%d.%m.%Y') 
        filtered_df = df.loc[(df['Date'] >= '2020-12-30')] #this also needs changing    
        myrange1[key] = filtered_df
    return myrange1

@st.cache_data
def get_tab_names():
    # Save the dataset as a dictionary
    sheets_data = {}
    for Name in selected_rows['Name']:
        file_url = selected_rows.loc[selected_rows['Name'] == Name, 'hrefs'].values[0]
        extension = file_url.rsplit('.', 1)[-1]
        
        #Adjust method when opening different file type
        if extension == 'xlsx':
            sheets_data_data[Name] = xlrd.open_workbook(file_url, on_demand=True)
        else:
            print(f'No sheets found in: {extension}')
            
            
            #****SAME CODE FOR PRA & EIOPA******
            myrange = myrange.loc[:, ~myrange.columns.str.contains('^Unnamed')]
            myrange = myrange.iloc[8: , :]
            myrange.reset_index(drop=True,inplace = True)
            myrange.rename(columns={"Main menu": "Term"},inplace = True)
            myrange = myrange.astype('float')
            myrange = myrange.astype({'Term': 'int32'})
            myrange['Date'] = mydate




#Plot chart
@st.cache_data
def plot_chart(filtered_df1, chart_name, site1):
    plt.clf()
    plt.suptitle(chart_name ,fontsize=15)
    plt.title("Source: "+site1 ,fontsize=8)
    plt.xticks(rotation=30, ha='right')
    plt.plot(filtered_df1['Date'],filtered_df1['SymAdj'],label='PRA')
    plt.legend()
    return plt
    
    


####App
##Title
st.header("Economic indicator automation")

##User Input
#User can input a link
url = st.text_input('URL:')

#Display whether we can webscrap from this link
if url:
  #User has inputted a URL
  st.write(check_acess(url))
  full_df = load_dataset(url)
  #st.write(full_df) # remove later
  df_names = pd.DataFrame(display_dataset(full_df))


  # Let the user select from the dataframe indices
  selected_names = st.multiselect('Select rows:', full_df.Name)
  selected_rows = full_df[full_df['Name'].isin(selected_names)]
  #st.write(selected_rows) # remove later
  tab_names = print_tab_names(selected_rows['hrefs'])
  selected_sheet = st.selectbox('Select sheet:', tab_names)
  #file_types = group_files(full_df)
  #selected_types = st.multiselect('Select file type:', file_types)
  data = get_data(selected_rows, selected_sheet, 0)
  st.write(data)

    

  complete_rows = find_largest_nonmissing_block(data)
  
  for key, cell_range in complete_rows.items():
    st.write(f'{key}: {cell_range}')  # Display the selected rows
  #st.write('### Selected Rows')
  #st.dataframe(selected_rows)
  
  #skip_rows = st.number_input('Skip rows:')
  #downloaded_data = get_data(selected_rows, "Calculations", skip_rows)###Need to add option to select sheets
  #downloaded_data2 = data_manipulate(downloaded_data)
  #for name, df in downloaded_data2.items():
    #st.write(f"### {name}")
    #st.table(df)
    #st.pyplot(plot_chart(df, selected_names, selected_rows['hrefs']))

else:
    # The user has not inputted a URL    
  st.write("Please input an URL above")


