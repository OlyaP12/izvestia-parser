import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class WebScraper:
    def __init__(self):
        self.base_url = ('https://iz.ru/search?type=&prd=3&text=%D1%8D%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D0%BA%D0%B0'
                         '%20%D0%B7%D0%B0%202022%20%D0%B3%D0%BE%D0%B4&date_from=2023-01-01&date_to=2023-12-31&sort=1')
        self.user_agent = UserAgent().chrome
        self.links = set()

    def get_soup(self, link):
        page = requests.get(link, headers={'User-Agent': self.user_agent})
        page = page.content.decode('utf-8')
        soup = BeautifulSoup(page, features='html.parser')
        return soup

    def parse_links(self):
        temp_links = set()
        count_of_page = 0
        while count_of_page < 260:
            soup = self.get_soup(f'{self.base_url}&from={count_of_page}')
            links = soup.find_all("div", attrs={'class': 'view-search__title'})
            temp_links.update([(x.a['href'], x.a.text) for x in links])
            count_of_page += 10
        return temp_links

    def create_clear_text(self, link):
        try:
            data = requests.get(link, headers={'User-Agent': self.user_agent})
            page = data.content.decode('utf-8')
            soup = BeautifulSoup(page, features='html.parser')
            div = soup.find('div', attrs={'class': 'text-article__inside'})
            while True:
                try:
                    div.select_one('img').decompose()
                except:
                    break
            while True:
                try:
                    div.select_one('a').decompose()
                except:
                    break
            text = ' '.join(list(map(str, div.find_all('p')))).replace('<u>', '').replace('</u>', '') \
                .replace('<p>', '').replace('</p>', '')
            return text
        except:
            return None

    def scrape(self):
        self.links = self.parse_links()
        news_added_count = 0
        article_counter = 1
        added_links = set()
        with open('Известия3_news_2023.txt', "w", encoding='utf-8') as outfile:
            while article_counter <= 250 and len(self.links) > 0:
                link = self.links.pop()
                link_url, name = link
                if link_url in added_links:
                    continue
                text = self.create_clear_text(link_url)
                if text:
                    print(f"{article_counter}. {name}\n\n{text}", file=outfile)
                    print(file=outfile)
                    added_links.add(link_url)
                    news_added_count += 1
                    article_counter += 1
                    if news_added_count % 10 == 0:
                        print(f"Added 10 news articles to the file. Total: {news_added_count}")
        print("Scraping completed.")


scraper = WebScraper()
scraper.scrape()
