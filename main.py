import pandas as pd
import cloudscraper
import requests
from bs4 import BeautifulSoup
import sys

def getSheetLink(url):
    scraper = cloudscraper.create_scraper()  
    ret = scraper.get(url)
    sts = ret.status_code
    if sts != 200:
        return None
        # return sts

    html = ret.text
    soup = BeautifulSoup(html,"html.parser")
    tb_sources = soup.html.find_all("iframe")
    tb_source = None
    for source in tb_sources:
        if 'google' in source['src']:
            tb_source = source['src']
    
    return tb_source
    
def getData(tb_source):
    ret = requests.get(tb_source)
    if ret.status_code != 200:
        return None
        # return ret.status_code

    html = ret.content
    soup = BeautifulSoup(html,"html.parser")
    table = soup.html.find_all("table")
    if len(table) != 1 :
        return None
        # return 0
    return [ [item.text for item in row_data.select("th,td")] for row_data in table[0].select("tr")]

def transformData(tab_data):
    header = tab_data[3][1:] + tab_data[2][2:] 
    data = [[data for data in rows[1:]] for rows in tab_data[4:]]

    i = 0
    for row in data:
        if len(row) == 1:
            break
        else:
            i+=1

    tab2 = data[i+1:]
    data = data[:i-1]

    header2 = tab2[1][:3] + tab2[0][1:] 
    data2 = tab2[2:]
    
    diff = len(header) - len(data[0])
    diff2 = len(header2) - len(data2[0])
    
    if diff2<0:
        for n in range(-diff2):
            header2.append('')
    if diff<0:
        for n in range(-diff):
            header.append('')
    
    if diff2>0:
        header2 = header2[:-diff2]
    if diff>0:
        header = header[:-diff]
    
    return (header, header2), (data, data2)

def getTableFromUrlasDF(url):
    tb_source = getSheetLink(url)
    if tb_source is None:
        return None
    
    tb_data = getData(tb_source)
    if tb_data is None:
        return None

    header, data = transformData(tb_data)

    df_pilotos = pd.DataFrame(data[0], columns=header[0])
    df_equipes = pd.DataFrame(data[1], columns=header[1])

    df_pilotos.to_csv('pilotos.csv')
    df_equipes.to_csv('equipes.csv')



if __name__ == "__main__":
    # url = 'https://www.f1bc.com/2022-2-f1bc-gt3-competizione/'
    url = sys.argv[1]
    data = getTableFromUrlasDF(url)