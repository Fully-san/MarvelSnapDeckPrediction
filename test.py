import re
from updateData import *

MARVELSNAPZONE_PATCH_NOTES_URL = 'https://marvelsnapzone.com/news/patch-notes/'

driver.get(MARVELSNAPZONE_PATCH_NOTES_URL)
soup = BeautifulSoup(driver.page_source, 'html.parser')

articles = soup.findAll('article', {'class': 'entry-card'})
link = articles[0].contents[0]['href'].title()

driver.get(link)
soup = BeautifulSoup(driver.page_source, 'html.parser')

updatedCards = []

links = soup.findAll('a', {'class': 'cardblock'})
for link in links:
    name = re.sub("[ '\-]","", link.contents[1].contents[1]['title'].title())
    if name not in updatedCards:
        updatedCards.append(name)

print(updatedCards)