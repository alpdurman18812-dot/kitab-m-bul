from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    encoded_q = urllib.parse.quote(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    books = []

    # 1. Deneme: Kitapyurdu Canlı Kazıma
    try:
        url = f"https://www.kitapyurdu.com/index.php?route=product/search&filter_name={encoded_q}"
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            products = soup.select('.product-grid')
            for p in products[:15]:
                title_elem = p.select_one('.name a span')
                author_elem = p.select_one('.author span a span')
                price_elem = p.select_one('.price-new .value') or p.select_one('.price .value')
                img_elem = p.select_one('.image img')
                link_elem = p.select_one('.name a')

                if title_elem:
                    books.append({
                        "title": title_elem.text.strip(),
                        "author": author_elem.text.strip() if author_elem else "Yazar Belirtilmemiş",
                        "price": price_elem.text.strip() if price_elem else "Stokta",
                        "image": img_elem['src'] if img_elem else "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80",
                        "link": link_elem['href'] if link_elem else f"https://www.kitapyurdu.com/index.php?route=product/search&filter_name={encoded_q}"
                    })
    except Exception as e:
        print("Kitapyurdu hatası:", e)

    # 2. Yedek Motor: Eğer Kitapyurdu bot korumasına takılırsa Türkiye Kütüphane API'sinden anında doldur
    if len(books) == 0:
        try:
            api_url = f"https://www.googleapis.com/books/v1/volumes?q={encoded_q}&maxResults=15&langRestrict=tr"
            api_res = requests.get(api_url, timeout=6).json()
            for item in api_res.get('items', []):
                info = item.get('volumeInfo', {})
                title = info.get('title', 'İsimsiz')
                authors = ", ".join(info.get('authors', ['Yazar Belirtilmemiş']))
                img = info.get('imageLinks', {}).get('thumbnail', "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80").replace('http://', 'https://')
                
                books.append({
                    "title": title,
                    "author": authors,
                    "price": "Pazarda Mevcut",
                    "image": img,
                    "link": f"https://www.kitapyurdu.com/index.php?route=product/search&filter_name={urllib.parse.quote(title)}"
                })
        except Exception as e:
            print("Yedek API hatası:", e)

    return jsonify(books)

# Vercel Serverless Tanımı
handler = app
