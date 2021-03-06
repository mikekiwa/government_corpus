"""
Scraper for US Presidential documents from http://www.presidency.ucsb.edu/index_docs.php

Author: Aaron Penne

Created: 2018-04-28
"""

import os
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape(url):
    result = requests.get(url)
    if result.status_code != 200:
        print('ERROR: Scrape status code {}'.format(result.status_code))
        return ''
    return BeautifulSoup(result.content, 'lxml')

def get_years(soup):
    # I think this more readable than list comprehension
    years_available = []
    for node in soup.find_all('option'):
        year = node.find_all(text=True)[0]
        years_available.append(year)
    return years_available

code_dir = os.path.dirname(__file__)
data_dir = os.path.join(code_dir, 'data') 
output_dir = os.path.join(code_dir, 'output')
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

# -----------------------------------------------------------------------------
# Executive Orders
# -----------------------------------------------------------------------------
soup = scrape('http://www.presidency.ucsb.edu/executive_orders.php')
years_available = get_years(soup)

# Get metadata for each executive order from year page
metadata = {'pres': [],
            'date': [],
            'title': [],
            'link': [],
            'filename': []}
print('Getting metadata')
for year in years_available:
    soup = scrape('http://www.presidency.ucsb.edu/executive_orders.php?year={}&Submit=DISPLAY'.format(year))
    table = soup.select('table')[10]
    for i, row in enumerate(table.select('tr')):
        # Skip header
        if i == 0:
            continue
        cell = row.select('td')
        metadata['pres'].append(''.join(c[0] for c in cell[0].text.split()))  # Get abbreviated name ()
        date = cell[1].text.split()
        year = date[2]
        month = date[0]
        day = date[1][:-1]
        if int(date[1][:-1]) < 1 or int(date[1][:-1]) > 31:
            print('Fixing date: {}'.format(cell[1].text))
            day = '1'
        date = '{} {} {}'.format(month, day, year)
        metadata['date'].append(datetime.strptime(date, '%B %d %Y').strftime('%Y%m%d'))
        metadata['title'].append(cell[2].text)
        metadata['link'].append('http://www.presidency.ucsb.edu{}'.format(cell[2].a.get('href')[2:]))

# Pull down all the docs
print('Getting executive orders')
for i, date in enumerate(metadata['date']):
    if i % 10 == 0:
        print('{:0.2f}%'.format(100*i/len(metadata['date'])))
    date = metadata['date'][i]
    pres = metadata['pres'][i]
    filename = '{}_Executive_Order_{}.txt'.format(date, pres)
    metadata['filename'].append(filename)
    output_file = os.path.join(output_dir, filename)
    if not os.path.isfile(output_file):
        soup = scrape(metadata['link'][i])
        text = soup.find('span', class_='displaytext')
        text = text.get_text('\n')
        with open(output_file, 'w+') as f:
            f.write(text)

# -----------------------------------------------------------------------------
# Proclamations
# -----------------------------------------------------------------------------
soup = scrape('http://www.presidency.ucsb.edu/proclamations.php')
years_available = get_years(soup)

# Get metadata for each doc from year page
print('Getting metadata')
for year in years_available:
    soup = scrape('http://www.presidency.ucsb.edu/proclamations.php?year={}&Submit=DISPLAY'.format(year))
    table = soup.select('table')[10]
    for i, row in enumerate(table.select('tr')):
        # Skip header
        if i == 0:
            continue
        cell = row.select('td')
        metadata['pres'].append(''.join(c[0] for c in cell[0].text.split()))  # Get abbreviated name ()
        date = cell[1].text.split()
        year = date[2]
        month = date[0]
        day = date[1][:-1]
        if int(date[1][:-1]) < 1 or int(date[1][:-1]) > 31:
            print('Fixing date: {}'.format(cell[1].text))
            day = '1'
        date = '{} {} {}'.format(month, day, year)
        metadata['date'].append(datetime.strptime(date, '%B %d %Y').strftime('%Y%m%d'))
        metadata['title'].append(cell[2].text)
        metadata['link'].append('http://www.presidency.ucsb.edu{}'.format(cell[2].a.get('href')[2:]))

# Pull down all the docs
print('Getting proclamations')
for i, date in enumerate(metadata['date']):
    if i % 10 == 0:
        print('{:0.2f}%'.format(100*i/len(metadata['date'])))
    date = metadata['date'][i]
    pres = metadata['pres'][i]
    filename = '{}_Proclamations_{}.txt'.format(date, pres)
    metadata['filename'].append(filename)
    output_file = os.path.join(output_dir, filename)
    if not os.path.isfile(output_file):
        soup = scrape(metadata['link'][i])
        text = soup.find('span', class_='displaytext')
        text = text.get_text('\n')
        with open(output_file, 'w+') as f:
            f.write(text)

print('Saving metadata')
df = pd.DataFrame(metadata, columns=['date', 'pres', 'filename', 'link', 'title'])
df.index.name = 'index'
df.to_csv('corpus_listing.csv')
