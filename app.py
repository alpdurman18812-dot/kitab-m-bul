from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    encoded_q = urllib.parse.quote(query.strip())
    url = f"https://www.kitapyurdu.com/index.php?route=product/search&filter_name={encoded_q}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    books = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        products = soup.select('.product-grid')

        for p in products[:20]:
            title_elem = p.select_one('.name a span')
            author_elem = p.select_one('.author span a span')
            price_elem = p.select_one('.price-new .value') or p.select_one('.price .value')
            img_elem = p.select_one('.image img')
            link_elem = p.select_one('.name a')

            title = title_elem.text.strip() if title_elem else "Bilinmeyen Kitap"
            author = author_elem.text.strip() if author_elem else "Yazar Belirtilmemiş"
            price = price_elem.text.strip() if price_elem else "Fiyat Belirtilmemiş"
            img = img_elem['src'] if img_elem else "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80"
            link = link_elem['href'] if link_elem else "#"

            books.append({
                "title": title,
                "author": author,
                "price": price,
                "image": img,
                "link": link
            })
    except Exception as e:
        print("Scraper Hatası:", e)

    return jsonify(books)

app = app
