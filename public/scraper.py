from bs4 import BeautifulSoup
import requests


url = "https://www.google.com"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
print(soup.p.text)
