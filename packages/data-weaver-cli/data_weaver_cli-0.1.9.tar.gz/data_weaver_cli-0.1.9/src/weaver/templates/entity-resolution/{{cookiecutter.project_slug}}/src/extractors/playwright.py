{% if cookiecutter.include_web_scraping == 'yes' -%}
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from typing import List, Dict, Optional, Any
import asyncio
import logging
from dataclasses import dataclass
import json

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


class PlaywrightBooksExtractor:
    """Web scraper for books.toscrape.com using Playwright."""

    def __init__(self, base_url: str = "https://books.toscrape.com", headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the browser and page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.page = await self.context.new_page()

    async def close(self):
        """Close the browser and playwright."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def _extract_rating_from_element(self, book_element) -> str:
        """Extract book rating from star classes."""
        rating_classes = {
            'One': '1',
            'Two': '2',
            'Three': '3',
            'Four': '4',
            'Five': '5'
        }

        try:
            rating_element = await book_element.query_selector('p.star-rating')
            if rating_element:
                class_name = await rating_element.get_attribute('class')
                for rating_word, rating_num in rating_classes.items():
                    if rating_word in class_name:
                        return f"{rating_num}/5"
        except Exception as e:
            logger.error(f"Error extracting rating: {e}")

        return "Unknown"

    async def scrape_book_list_page(self, page_url: str) -> List[Book]:
        """Scrape books from a catalog page."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto(page_url, wait_until='networkidle')

            # Wait for book containers to load
            await self.page.wait_for_selector('article.product_pod', timeout=10000)

            books = []
            book_elements = await self.page.query_selector_all('article.product_pod')

            for book_element in book_elements:
                try:
                    # Extract title and URL
                    title_element = await book_element.query_selector('h3 a')
                    title = await title_element.get_attribute('title') if title_element else ''
                    relative_url = await title_element.get_attribute('href') if title_element else ''
                    book_url = f"{self.base_url}/{relative_url}" if relative_url else ''

                    # Extract price
                    price_element = await book_element.query_selector('p.price_color')
                    price = await price_element.inner_text() if price_element else ''

                    # Extract availability
                    availability_element = await book_element.query_selector('p.instock.availability')
                    availability = await availability_element.inner_text() if availability_element else ''
                    availability = availability.strip()

                    # Extract rating
                    rating = await self._extract_rating_from_element(book_element)

                    # Extract image URL
                    image_element = await book_element.query_selector('div.image_container img')
                    image_src = await image_element.get_attribute('src') if image_element else ''
                    image_url = f"{self.base_url}/{image_src}" if image_src else ''

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
                    logger.error(f"Error extracting book from element: {e}")
                    continue

            return books

        except Exception as e:
            logger.error(f"Error scraping page {page_url}: {e}")
            return []

    async def scrape_book_details(self, book_url: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information from a book's individual page."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto(book_url, wait_until='networkidle')

            details = {}

            # Extract description
            description_element = await self.page.query_selector('#product_description')
            if description_element:
                # Get the next paragraph sibling
                description_p = await self.page.query_selector('#product_description + p')
                if description_p:
                    details['description'] = await description_p.inner_text()

            # Extract product information table
            table_rows = await self.page.query_selector_all('table.table-striped tr')
            for row in table_rows:
                th = await row.query_selector('th')
                td = await row.query_selector('td')
                if th and td:
                    key = await th.inner_text()
                    value = await td.inner_text()
                    # Clean up the key
                    key = key.strip().lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
                    details[key] = value.strip()

            return details

        except Exception as e:
            logger.error(f"Error extracting details from {book_url}: {e}")
            return None

    async def get_total_pages(self) -> int:
        """Get the total number of pages in the catalog."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto(self.base_url, wait_until='networkidle')

            # Find pagination
            current_page_element = await self.page.query_selector('li.current')
            if current_page_element:
                text = await current_page_element.inner_text()
                # Text format: "Page 1 of 50"
                try:
                    return int(text.split('of')[-1].strip())
                except (ValueError, IndexError):
                    pass

            return 1

        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 1

    async def scrape_all_books(self, max_pages: Optional[int] = None, include_details: bool = False) -> List[Book]:
        """Scrape all books from the website."""
        all_books = []
        total_pages = min(await self.get_total_pages(), max_pages or float('inf'))

        logger.info(f"Starting to scrape {total_pages} pages")

        for page_num in range(1, int(total_pages) + 1):
            if page_num == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}/catalogue/page-{page_num}.html"

            logger.info(f"Scraping page {page_num}/{total_pages}")
            books = await self.scrape_book_list_page(page_url)

            # Optionally get detailed information for each book
            if include_details:
                for book in books:
                    details = await self.scrape_book_details(book.url)
                    if details:
                        book.description = details.get('description')
                        book.upc = details.get('upc')
                        book.product_type = details.get('product_type')
                        book.price_excl_tax = details.get('price_excl_tax')
                        book.price_incl_tax = details.get('price_incl_tax')
                        book.tax = details.get('tax')

                        # Parse stock number
                        availability = details.get('availability', '')
                        if 'In stock' in availability:
                            try:
                                # Extract number from availability string
                                import re
                                stock_match = re.search(r'\((\d+)', availability)
                                if stock_match:
                                    book.stock = int(stock_match.group(1))
                            except (ValueError, AttributeError):
                                pass

            all_books.extend(books)
            logger.info(f"Found {len(books)} books on page {page_num}")

            # Add a small delay between pages
            await asyncio.sleep(0.5)

        logger.info(f"Total books scraped: {len(all_books)}")
        return all_books

    async def search_books_by_title(self, search_term: str) -> List[Book]:
        """Search for books by title using the search functionality."""
        if not self.page:
            await self.start()

        try:
            await self.page.goto(self.base_url, wait_until='networkidle')

            # Look for search input (if it exists on the site)
            # Note: books.toscrape.com doesn't have a search function,
            # so we'll scrape all and filter locally
            all_books = await self.scrape_all_books(max_pages=2)

            # Filter books by title
            matching_books = [
                book for book in all_books
                if search_term.lower() in book.title.lower()
            ]

            return matching_books

        except Exception as e:
            logger.error(f"Error searching for books: {e}")
            return []

    async def scrape_with_pagination_clicks(self, max_pages: Optional[int] = None) -> List[Book]:
        """Alternative scraping method using pagination clicks."""
        if not self.page:
            await self.start()

        all_books = []
        page_count = 0
        max_pages = max_pages or float('inf')

        try:
            await self.page.goto(self.base_url, wait_until='networkidle')

            while page_count < max_pages:
                page_count += 1
                logger.info(f"Scraping page {page_count}")

                # Scrape current page
                books = await self.scrape_book_list_page(self.page.url)
                all_books.extend(books)

                # Try to find and click the "next" button
                next_button = await self.page.query_selector('li.next a')
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_load_state('networkidle')
                else:
                    logger.info("No more pages found")
                    break

            return all_books

        except Exception as e:
            logger.error(f"Error in pagination scraping: {e}")
            return all_books

    async def take_screenshot(self, filename: str = "books_page.png"):
        """Take a screenshot of the current page."""
        if self.page:
            await self.page.screenshot(path=filename, full_page=True)
            logger.info(f"Screenshot saved as {filename}")


# Example usage
async def example_usage():
    """Example of how to use the PlaywrightBooksExtractor."""
    async with PlaywrightBooksExtractor(headless=True) as extractor:
        try:
            # Scrape first 2 pages with details
            books = await extractor.scrape_all_books(max_pages=2, include_details=True)

            print(f"Scraped {len(books)} books using Playwright")

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

            # Search for specific books
            search_results = await extractor.search_books_by_title("python")
            print(f"\nFound {len(search_results)} books with 'python' in title")

            # Take a screenshot
            await extractor.take_screenshot("books_homepage.png")

            # Convert to dictionaries for storage
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

        except Exception as e:
            logger.error(f"Error in example usage: {e}")
            return []


async def compare_extractors():
    """Compare the performance of different extraction methods."""
    print("Comparing Playwright extraction methods...")

    async with PlaywrightBooksExtractor() as extractor:
        # Method 1: Direct URL navigation
        start_time = asyncio.get_event_loop().time()
        books_method1 = await extractor.scrape_all_books(max_pages=2)
        time1 = asyncio.get_event_loop().time() - start_time

        # Method 2: Pagination clicking
        start_time = asyncio.get_event_loop().time()
        books_method2 = await extractor.scrape_with_pagination_clicks(max_pages=2)
        time2 = asyncio.get_event_loop().time() - start_time

        print(f"Method 1 (URL navigation): {len(books_method1)} books in {time1:.2f}s")
        print(f"Method 2 (pagination clicks): {len(books_method2)} books in {time2:.2f}s")


if __name__ == "__main__":
    asyncio.run(example_usage())
    # asyncio.run(compare_extractors())
{%- endif %}