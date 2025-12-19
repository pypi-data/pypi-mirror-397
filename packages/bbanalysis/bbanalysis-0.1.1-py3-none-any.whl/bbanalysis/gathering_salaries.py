import numpy as np
import pandas as pd
import asyncio
import json
import time
import aiohttp
import cloudscraper
from bs4 import BeautifulSoup, Comment
from typing import Optional

def add_one(x):
    return x + 1

def calculate_mean(numbers):
    return np.mean(numbers)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}



def create_http_headers() -> dict[str, str]:
    """Create headers that mimic a real browser to avoid being blocked"""
    return {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def parse_salary_table_from_soup(soup: BeautifulSoup) -> dict[int, int]:
    """Extract salary data from the baseball-reference salary table using BeautifulSoup"""
    salary_dict = {}
   
    # First try to find the table normally
    salary_table = soup.find('table', {'id': 'br-salaries'})
   
    # If not found, look for it in HTML comments (common pattern for baseball-reference)
    if not salary_table:
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if 'id="br-salaries"' in comment:
                comment_soup = BeautifulSoup(comment, 'html.parser')
                salary_table = comment_soup.find('table', {'id': 'br-salaries'})
                if salary_table:
                    break
   
    if not salary_table:
        return salary_dict
   
    rows = salary_table.find_all('tr')
    if not rows:
        return salary_dict
   
    header_row = rows[0]
    headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
   
    try:
        year_col_idx = headers.index('Year')
        salary_col_idx = headers.index('Salary')
    except ValueError:
        return salary_dict
   
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) <= max(year_col_idx, salary_col_idx):
            continue
           
        year_text = cells[year_col_idx].get_text().strip()
        salary_text = cells[salary_col_idx].get_text().strip()
       
        if year_text.isdigit() and len(year_text) == 4:
            try:
                year = int(year_text)
                if 2018 <= year <= 2025:
                    if salary_text and salary_text.startswith('$'):
                        salary_clean = salary_text.replace("$", "").replace(",", "").strip()
                        if salary_clean:
                            try:
                                salary = int(salary_clean)
                                salary_dict[year] = salary
                            except ValueError:
                                pass
            except ValueError:
                continue
   
    return salary_dict

# async def scrape_salary_from_url(url: str, session: aiohttp.ClientSession) -> dict[int, int]:
#     """Scrape salary data from a baseball-reference player page using HTTP GET"""
#     print(f"Starting to scrape {url}.")
   
#     try:
#         async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
#             if response.status != 200:
#                 print(f"Failed to fetch {url}: HTTP {response.status}")
#                 return {}
           
#             html = await response.text()
#             soup = BeautifulSoup(html, 'html.parser')
#             salary_dict = parse_salary_table_from_soup(soup)
           
#             print(f"Done scraping {url}. Found {len(salary_dict)} salary entries.")
#             return salary_dict
           
#     except asyncio.TimeoutError:
#         print(f"Timeout while scraping {url}")
#         return {}
#     except aiohttp.ClientError as e:
#         print(f"HTTP error while scraping {url}: {e}")
#         return {}
#     except Exception as e:
#         print(f"Unexpected error while scraping {url}: {e}")
#         return {}

# csv_path='MLB_2018_2025_Cleaned.csv'
# output_json_path='unique_links.json'

def extract_unique_links(csv_path: str, output_json_path: str) -> None:
    """Extract unique player links from CSV and save as JSON"""
    df = pd.read_csv(csv_path)
   
    url_to_player = df.dropna(subset=['Player_Link']).drop_duplicates(subset=['Player_Link']).set_index('Player_Link')['Player'].to_dict()
    unique_urls = df['Player_Link'].dropna().unique().tolist()
    links_with_ids = [{"id": i + 1, "url": url, "player": url_to_player[url]} for i, url in enumerate(unique_urls)]
   
    with open(output_json_path, 'w') as f:
        json.dump(links_with_ids, f, indent=2)
   
    print(f"Extracted {len(links_with_ids)} unique links and saved to {output_json_path}")

def scrape_with_cloudscraper(url: str, scraper) -> dict[int, int]:
    print(f"Scraping {url}")
    try:
        html = scraper.get(url, timeout=30).text
        soup = BeautifulSoup(html, 'html.parser')
        return parse_salary_table_from_soup(soup)
    except Exception as e:
        print(f"Failed {url}: {e}")
        return {}
    
def churn_with_cloudscraper():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        delay=10
    )

    with open("unique_links.json", "r") as f:
        links = json.load(f)

    # Resume logic same as yours
    try:
        with open("salaries_again.json", "r") as f:
            existing = json.load(f)
    except:
        existing = []

    existing_ids = {x['id'] for x in existing}
    remaining = [l for l in links if l['id'] not in existing_ids]

    results = {e['id']: e for e in existing}

    for link in remaining:
        salary_data = scrape_with_cloudscraper(link['url'], scraper)
        results[link['id']] = {
            "id": link['id'],
            "player": link['player'],
            "salaries": salary_data
        }

        
        with open("salaries.json", "w") as f:
            json.dump(sorted(results.values(), key=lambda x: x['id']), f, indent=2)

        print(f"Success: Saved {link['player']} → {len(salary_data)} years")
        time.sleep(4)  

    print("All done!")

if __name__ == "__main__":
    # Uncomment to extract unique links from CSV
    # extract_unique_links("MLB_2018_2025_Cleaned.csv", "unique_links.json")
   
    # Uncomment to test single scrape
    # async def test_single_scrape():
    #     async with aiohttp.ClientSession(headers=create_http_headers()) as session:
    #         result = await scrape_salary_from_url("https://www.baseball-reference.com/players/l/lindofr01.shtml", session)
    #         print(result)
    # asyncio.run(test_single_scrape())
   
    ## Uncomment to run full scraping
    ## asyncio.run(churn_with_cloudscraper())

    # Remove asyncio.run() since churn_with_cloudscraper is not async
    # churn_with_cloudscraper()
    pass

## if you want to process the resulting JSON into a CSV --------------------
import json
import pandas as pd

def salaries_json_to_csv(json_path: str, csv_path: str) -> None:
    """
    Convert salaries.json to a tidy long-format CSV.

    Args:
        json_path: Path to the input JSON file (e.g., salaries.json)
        csv_path: Path to the output CSV file (e.g., salaries.csv)
    """
    # Load JSON
    with open(json_path) as f:
        data = json.load(f)

    # Flatten nested JSON
    df = pd.json_normalize(data)

    # Convert wide to long format
    long_df = df.melt(
        id_vars=["id", "player"],           # keep these columns
        var_name="year",
        value_name="salary"
    )

    # Remove 'salaries.' prefix if present and convert year to int
    long_df["year"] = long_df["year"].str.replace("salaries.", "", regex=False).astype(int)

    # Save to CSV
    long_df.to_csv(csv_path, index=False)

    print(f"Saved long-format salaries to {csv_path}")
