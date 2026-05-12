import os
import requests
import re
from collections import Counter
from bs4 import BeautifulSoup
import shutil
from urllib.parse import urlparse
import sqlite3
from urllib.parse import urljoin

SAVE_HTML = False

URL_List  = ["https://example.com/"]
counter = 0
current_url = URL_List[counter]


visited = set() 
seen_urls = set(URL_List)

def normalize(url: str) -> str:
    return url.rstrip('/')

conn = sqlite3.connect('crawler.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        word TEXT,
        word_count INTEGER,
        bigram TEXT,
        bigram_count INTEGER,
        trigram TEXT,
        trigram_count INTEGER,
        UNIQUE(url, word, bigram, trigram)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS page_words (
        page_url TEXT NOT NULL,
        word TEXT NOT NULL,
        word_count INTEGER NOT NULL,
        UNIQUE(page_url, word)
    )
''')


cursor.execute("SELECT DISTINCT url FROM pages")
rows = cursor.fetchall()
visited = {normalize(row[0]) for row in rows if row[0]}



def create_html(soup, domain):
    name = domain
    if not SAVE_HTML:
        return
    os.makedirs("Websites", exist_ok=True)
    with open(f"{name}.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    shutil.move(f"{name}.html", f"Websites/{name}.html") 

def create_soup(current_url):
    try:
        current_url_response = requests.get(current_url, verify=False, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {current_url}: {e}")
        return
    if current_url_response.status_code == 200:
        soup = BeautifulSoup(current_url_response.text, 'html.parser')
        getlinks(soup, current_url)
        
        # Only process details if not already visited
        if normalize(current_url) not in visited:
            visited.add(normalize(current_url))
            words, keywords = getkeywords(soup)

            for word, cnt in keywords:
                cursor.execute(
                    "INSERT OR REPLACE INTO page_words (page_url, word, word_count) VALUES (?, ?, ?)",
                    (current_url, word, cnt)
                )

            bigrams = Counter(get_bigrams(words)).most_common(10)
            for phrase, count in bigrams:
                cursor.execute(
                    "INSERT OR REPLACE INTO pages (url, bigram, bigram_count) VALUES (?, ?, ?)",
                    (current_url, phrase, count)
                )
            trigrams = Counter(get_trigrams(words)).most_common(10)
            for phrase, count in trigrams:
                cursor.execute(
                    "INSERT OR REPLACE INTO pages (url, trigram, trigram_count) VALUES (?, ?, ?)",
                    (current_url, phrase, count)
                )

            conn.commit()

        domain = URLtoTextDomain(current_url)
        create_html(soup, domain)
    else:
        print(f"failed : {current_url_response.status_code}")

def URLtoTextDomain(url):
    domain = url.split("//")[-1].split("/")[0]
    return domain

def getlinks(soup, base_url):
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href'].strip()
        if not href:
            continue
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        if not parsed.netloc or parsed.scheme not in ('http', 'https'):
            continue
        normalized = normalize(absolute_url)
        if normalized not in seen_urls:
            URL_List.append(normalized)
            seen_urls.add(normalized)

def getkeywords(soup):
    text = soup.get_text().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()
    ignorewords = {"the", "and", "is", "in", "to", "of", "a", "that", "it", "with", "as", "for", "was", "on", "are", "by", "this", "be", "or", "from", "at", "which", "but", "not", "all", "we", "they", "their", "has", "have", "if", "can", "do", "he", "she", "my", "me", "his", "her", "its", "our", "us", "them", "what", "who", "when", "where", "why", "how"}
    words = [w for w in words if w not in ignorewords and len(w) > 2]
    # The above one: for as the length of words in words, if the word is not in ignorewords and the length of the word is greater than 2, keep it in the list
    word_counts = Counter(words)
    return words, word_counts.most_common(25)

def get_bigrams(words):
    return [" ".join(words[i:i+2]) for i in range(len(words)-1)]

def get_trigrams(words):
    return [" ".join(words[i:i+3]) for i in range(len(words)-2)]



while counter < len(URL_List):
    current_url = URL_List[counter]
    create_soup(current_url)
    counter += 1
