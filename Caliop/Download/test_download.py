import requests
from bs4 import BeautifulSoup

url = 'https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20/2020/05/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

filenames = []
for a in soup.find_all('a', href=True):
    if a['href'].endswith('.hdf'):
        filenames.append(a['href'])

print(filenames)