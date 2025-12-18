{% if cookiecutter.include_web_scraping == 'yes' -%}
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Book:
    """Data class for book information."""
    title: str
    price: str
    availability: str
    rating: str
    url: str
    image_url: str
    description: Optional[str] = None
    upc: Optional[str] = None
    product_type: Optional[str] = None
    price_excl_tax: Optional[str] = None
    price_incl_tax: Optional[str] = None
    tax: Optional[str] = None
    stock: Optional[int] = None


class BooksToScrapeExtractor:
    """Web scraper for books.toscrape.com using requests and BeautifulSoup."""

    def __init__(self, base_url: str = "https://books.toscrape.com", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(self.delay)  # Be respectful to the server
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _extract_rating(self, article) -> str:
        """Extract book rating from star classes."""
        rating_classes = {
            'One': '1',
            'Two': '2',
            'Three': '3',
            'Four': '4',
            'Five': '5'
        }

        rating_element = article.find('p', class_='star-rating')
        if rating_element:
            for rating_word, rating_num in rating_classes.items():
                if rating_word in rating_element.get('class', []):
                    return f"{rating_num}/5"
        return "Unknown"

    def scrape_book_list_page(self, page_url: str) -> List[Book]:
        """Scrape books from a catalog page."""
        soup = self._get_page(page_url)
        if not soup:
            return []

        books = []
        book_containers = soup.find_all('article', class_='product_pod')

        for article in book_containers:
            try:
                # Extract basic information
                title_element = article.find('h3').find('a')
                title = title_element.get('title', '')
                relative_url = title_element.get('href', '')
                book_url = urljoin(self.base_url, relative_url)

                price_element = article.find('p', class_='price_color')
                price = price_element.text.strip() if price_element else ''

                availability_element = article.find('p', class_='instock availability')
                availability = availability_element.text.strip() if availability_element else ''

                rating = self._extract_rating(article)

                image_element = article.find('div', class_='image_container').find('img')
                image_url = urljoin(self.base_url, image_element.get('src', '')) if image_element else ''

                book = Book(
                    title=title,
                    price=price,
                    availability=availability,
                    rating=rating,
                    url=book_url,
                    image_url=image_url
                )

                books.append(book)

            except Exception as e:
                logger.error(f"Error extracting book from article: {e}")
                continue

        return books

    def scrape_book_details(self, book_url: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information from a book's individual page."""
        soup = self._get_page(book_url)
        if not soup:
            return None

        try:
            details = {}

            # Extract description
            description_element = soup.find('div', id='product_description')
            if description_element:
                description_p = description_element.find_next_sibling('p')
                details['description'] = description_p.text.strip() if description_p else ''

            # Extract product information table
            table = soup.find('table', class_='table table-striped')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        key = th.text.strip().lower().replace(' ', '_')
                        value = td.text.strip()
                        details[key] = value

            return details

        except Exception as e:
            logger.error(f"Error extracting details from {book_url}: {e}")
            return None

    def get_total_pages(self) -> int:
        """Get the total number of pages in the catalog."""
        soup = self._get_page(self.base_url)
        if not soup:
            return 1

        # Find pagination
        pager = soup.find('li', class_='current')
        if pager:
            text = pager.text.strip()
            # Text format: "Page 1 of 50"
            try:
                return int(text.split('of')[-1].strip())
            except (ValueError, IndexError):
                pass

        return 1

    def scrape_all_books(self, max_pages: Optional[int] = None, include_details: bool = False) -> List[Book]:
        """Scrape all books from the website."""
        all_books = []
        total_pages = min(self.get_total_pages(), max_pages or float('inf'))

        logger.info(f"Starting to scrape {total_pages} pages")

        for page_num in range(1, int(total_pages) + 1):
            if page_num == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}/catalogue/page-{page_num}.html"

            logger.info(f"Scraping page {page_num}/{total_pages}")
            books = self.scrape_book_list_page(page_url)

            # Optionally get detailed information for each book
            if include_details:
                for book in books:
                    details = self.scrape_book_details(book.url)
                    if details:
                        book.description = details.get('description')
                        book.upc = details.get('upc')
                        book.product_type = details.get('product_type')
                        book.price_excl_tax = details.get('price_(excl._tax)')
                        book.price_incl_tax = details.get('price_(incl._tax)')
                        book.tax = details.get('tax')
                        # Parse stock number
                        availability = details.get('availability', '')
                        if 'In stock' in availability:
                            try:
                                stock_text = availability.split('(')[1].split(' ')[0]
                                book.stock = int(stock_text)
                            except (IndexError, ValueError):
                                pass

            all_books.extend(books)
            logger.info(f"Found {len(books)} books on page {page_num}")

        logger.info(f"Total books scraped: {len(all_books)}")
        return all_books

    def search_books_by_category(self, category: str) -> List[Book]:
        """Search books by category (not implemented for this simple example)."""
        # This would require analyzing the category navigation
        # For now, just return all books
        logger.warning("Category search not implemented, returning all books")
        return self.scrape_all_books(max_pages=2)

    def close(self):
        """Close the session."""
        self.session.close()


# Example usage
async def example_usage():
    """Example of how to use the BooksToScrapeExtractor."""
    extractor = BooksToScrapeExtractor(delay=0.5)  # Be respectful with delays

    try:
        # Scrape first 2 pages
        books = extractor.scrape_all_books(max_pages=2, include_details=True)

        print(f"Scraped {len(books)} books")

        # Print first few books
        for i, book in enumerate(books[:3]):
            print(f"\nBook {i+1}:")
            print(f"  Title: {book.title}")
            print(f"  Price: {book.price}")
            print(f"  Rating: {book.rating}")
            print(f"  Availability: {book.availability}")
            print(f"  URL: {book.url}")
            if book.description:
                print(f"  Description: {book.description[:100]}...")
            if book.upc:
                print(f"  UPC: {book.upc}")

        # Example: Convert to dictionaries for storage
        book_dicts = []
        for book in books:
            book_dict = {
                'title': book.title,
                'price': book.price,
                'rating': book.rating,
                'availability': book.availability,
                'url': book.url,
                'image_url': book.image_url,
                'description': book.description,
                'upc': book.upc,
                'stock': book.stock
            }
            book_dicts.append(book_dict)

        return book_dicts

    finally:
        extractor.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
{%- endif %}