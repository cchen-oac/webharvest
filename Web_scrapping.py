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
import urllib.request as url
from bs4 import BeautifulSoup as soup
import openpyxl
from zipfile import ZipFile
import requests
from io import BytesIO

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



