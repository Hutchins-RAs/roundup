from src.scraper.external_requests import request_soup
from ..generic_scraper import GenericScraper
import requests
from bs4 import BeautifulSoup

class BFIScraper(GenericScraper):
    def __init__(self):
        super().__init__(source = 'BFI')
        # Define headers once and use them throughout the class
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
    
    # Public method which is called from outside the class.
    def fetch_data(self):
        '''
        Sends a GET request to the source's main page and parses the 
        response using BeautifulSoup to get title, link, author, and date
        for each working paper entry. 
        A secondary GET request is made to each working paper's
        landing page and parsed using BeautifulSoup to extract
        number and abstract data.

        :return: A list of dictionaries containing Title, Author, Link, 
        Abstract, Number and Date for each working paper entry 
        :rtype: list
        '''
        url = 'https://bfi.uchicago.edu/working-papers/'
        # Bundle the arguments together for requests module
        session_arguments = requests.Request(method='GET', url=url, headers=self.headers)
        # Send request and get soup
        soup = request_soup(session_arguments)

        elements = soup.find('main').select('div.card.is-horizontal')

        Titles = []
        Links = []
        Dates = []
        Authors = []
        Abstracts = []
        Numbers = []

        for el in elements:
            title_tag = el.select_one('h3.card__title a')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            # Strip query params (e.g. ?occurrence_id=0) from the link
            link = title_tag['href'].split('?')[0]
            date = el.select_one('span.date').text.strip()
            author = el.select_one('div.card__authors').get_text(separator=' ', strip=True).replace('\xa0', ' ')

            # Visit landing page for abstract and paper number
            session_arguments = requests.Request(method='GET', url=link, headers=self.headers)
            landing_soup = request_soup(session_arguments)

            abstract_el = landing_soup.select_one('div.textblock')
            abstract = abstract_el.text.strip() if abstract_el else ''

            pdf_tag = landing_soup.find('a', href=lambda h: h and 'BFI_WP' in h)
            number = pdf_tag['href'].split('BFI_WP_')[1].replace('.pdf', '') if pdf_tag else None

            Titles.append(title)
            Links.append(link)
            Dates.append(date)
            Authors.append(author)
            Abstracts.append(abstract)
            Numbers.append(number)
            
        # Create a dictionary of the six lists, where the keys are the column names.
        data = {'Title': Titles,
                'Link': Links,
                'Date': Dates,
                'Author': Authors,
                'Number': Numbers,
                'Abstract': Abstracts}
        
        # Use the inherited process_data method to create and return the DataFrame
        return data
