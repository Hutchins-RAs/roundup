from ..generic_scraper import GenericScraper
from src.scraper.external_requests import request_json
import re

class NBERScraper(GenericScraper):
    def __init__(self):
        super().__init__(source = 'NBER')
        # Define generic headers to be used later in the class
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }

    # Public method which is called from outside the class.
    def fetch_data(self):
        '''
        Sends a GET request to the source's API and parses the JSON
        response to get title, link, date, number, author, and abstract
        for each working paper entry. All fields are sourced from the API
        directly; no secondary requests are made to landing pages.
        Note: abstracts are truncated at ~200 characters by the API.

        :return: A list of dictionaries containing Title, Author, Link,
        Abstract, Number and Date for each working paper entry
        :rtype: list
        '''
        url = 'https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/_/_/search?page=1&perPage=100'
        # Send request and parse JSON-formatted response
        response = request_json(method = 'GET',
                            url = url,
                            headers = self.headers)
        elements = response['results']

        # Initialize `data`
        data = []

        for el in elements:
            # Title
            title = el['title']

            # Link
            link = 'https://www.nber.org' + el['url']

            # Date
            date = el['displaydate']

            # Number
            number = el['url'].split('/papers/w')[1]

            # Authors come back from the API as a list of HTML anchor tags
            # e.g. ['<a href="/people/david_cutler">David M. Cutler</a>', ...]
            # Strip the tags to get plain names
            author = ', '.join(re.sub(r'<[^>]+>', '', a) for a in el['authors'])

            # Abstract is available directly from the API.
            # Note: the API truncates abstracts at ~200 characters.
            abstract = el['abstract']

            # Append title, link, date, number, abstract, author to `data`
            data.append({
                'Title': title,
                'Link': link,
                'Date': date,
                'Number': number,
                'Abstract': abstract,
                'Author': author
            })
        
        return(data)


