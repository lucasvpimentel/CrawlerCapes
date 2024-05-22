from crawler import Crawler
import requests
import lxml
import json

import lxml.html
from bs4 import BeautifulSoup



#####################################################################


class CrawlerCAPES(Crawler):
    def __init__(self):
        super().__init__()
        self.url = r'https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados-capes'

#####################################################################

    def getResearchNotes(self):

        print('--------------------NOTES---------------------')
        site = requests.get(self.url)
        html_content = site.content

        soup = BeautifulSoup(html_content,
                             'lxml')
        
        tree = lxml.html.fromstring(str(soup))

        xpath = r'/html/body/div[2]/div[1]/main/div[2]/div/div[3]/div/div/div/div/ul'
        ul = tree.xpath(xpath)

        if ul:
            ul_soup = BeautifulSoup(lxml.html.tostring(ul[0]), 'html.parser')

            for li in ul_soup.find_all('li'):
                a_tag = li.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    inner_text = a_tag.text
                    print(f"Href: {href}, Text: {inner_text}")
                    self.title.append(inner_text)
                    self.homepage.append(href)

        else:
            print('Element not found')
        
        return [self.title,self.homepage]


    def getDate(self):
        if self.homepage:
            print('-----------------DATE--------------------')
            for adress in self.homepage:
                response = requests.get(adress)
                html_content = response.content

                tree = lxml.html.fromstring(html_content)
                xpath_published = r'/html/body/div[2]/div[1]/main/div[2]/div/div[3]/div[2]/span[1]/span[2]'
                xpath_updated = r'/html/body/div[2]/div[1]/main/div[2]/div/div[3]/div[2]/span[2]/span[2]' 


                element_published = tree.xpath(xpath_published)
                if element_published:
                    self.datePublished.append(element_published[0].text_content())
                    # print(f"Inner Text Published: {self.datePublished}")
                else:
                    self.datePublished.append('No Information')
                    print('Element not Found')


                element_updated = tree.xpath(xpath_updated)
                if element_updated:
                    self.dateUpdated.append(element_updated[0].text_content())
                    # print(f"Inner Text Updated: {self.dateUpdated}")
                else:
                    self.dateUpdated.append('No Information')
                    print('Element not Found')
                

            print(f"Inner Text Published: {self.datePublished}")
            print(f"Inner Text Updated: {self.dateUpdated}")
        return [self.datePublished,self.dateUpdated]

########################################################################

    def getDownloadLink(self):
        if self.homepage:
            print('------------------DOWNLOAD-------------------')
            down_list = []
            for adress in self.homepage:
                response = requests.get(adress)
                html_content = response.content

                tree = lxml.html.fromstring(html_content)

                table_xpath = '/html/body/div[2]/div[1]/main/div[2]/div/div[5]/div/table[2]'

                table = tree.xpath(table_xpath)
                
                if table:
                    rows = table[0].xpath('.//tr')
                    for row in rows:
                        cols = row.xpath('.//td')
                        if len(cols) >= 2:
                            anchor = cols[1].xpath('.//a')
                            if anchor:
                                href = anchor[0].get('href')
                                if href:
                                    down_list.append(href)
                                    print(href)
                                else:
                                    print('Element not Found')
                                    down_list.append('No Information')
                main_note = down_list[-1]
                self.download_link.append(main_note)    

        return self.download_link
    
    def dumpJson(self):
        if self.title:
            data = []
            for title,homepage,datePublished,dateUpdated, downloadLink in zip(self.title,
                                                                            self.homepage,
                                                                            self.datePublished,
                                                                            self.dateUpdated,
                                                                            self.download_link):
                details_dict = {'Title':title,
                                'Link':homepage,
                                'Published':datePublished,
                                'Updated':dateUpdated,
                                'Dowload Link':downloadLink}
                
                data.append(details_dict)

            with open('notes.json','w') as json_file:
                json.dump(data,
                          json_file,
                          indent=4,
                          ensure_ascii=True)



#####################################################################
if __name__ == '__main__':
    crawler = CrawlerCAPES()
    crawler.getResearchNotes()
    crawler.getDate()
    crawler.getDownloadLink()
    crawler.dumpJson()
