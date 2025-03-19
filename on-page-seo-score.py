import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO

# Inject Custom CSS for Modern Styling
def inject_custom_css():
    st.markdown(
        """
        <style>
        .stTitle { text-align: center !important; }
        .stButton { text-align: center !important; display: flex; justify-content: center; }
        .stTextInput>div>div>input { text-align: center !important; }
        body { font-family: 'Arial', sans-serif; background-color: #f8f9fa; color: #333; }
        .reportview-container { padding-top: 2rem; }
        .stMarkdown h2 { color: #007bff; }
        .seo-score { font-size: 2rem; font-weight: bold; text-align: center; color: #28a745; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Fetch HTML from the given URL
def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

# Extract Indexability Data
def extract_indexability_data(url, soup):
    canonical_tag = soup.find('link', rel='canonical')
    canonical_url = canonical_tag['href'].strip() if canonical_tag else "Missing"
    robots_meta = soup.find('meta', attrs={'name': 'robots'})
    robots_meta_content = robots_meta['content'] if robots_meta else "Missing"
    x_robots_tag = soup.find('meta', attrs={'http-equiv': 'X-Robots-Tag'})
    x_robots_content = x_robots_tag['content'] if x_robots_tag else "Missing"
    sitemap_url = f"{url}/sitemap.xml"
    robots_txt_url = f"{url}/robots.txt"
    hreflang_tags = soup.find_all('link', rel='alternate', hreflang=True)
    hreflangs = len(hreflang_tags) if hreflang_tags else "Missing"
    return {
        "Canonical URL": canonical_url,
        "Self-Canonical": "✅ Matches Entered URL" if canonical_url == url else "❌ Does Not Match Entered URL",
        "Robots.txt": robots_txt_url,
        "Robots Meta Tag": robots_meta_content,
        "X-Robots-Tag HTTP": x_robots_content,
        "Sitemaps": sitemap_url,
        "Hreflangs": hreflangs
    }

# Extract SEO-related data
def extract_seo_data(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title else "Title not found"
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    og_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag and meta_desc_tag.get('content') else og_desc_tag['content'].strip() if og_desc_tag and og_desc_tag.get('content') else "Meta description not found"
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else "H1 not found"
    word_count = len(soup.get_text().split())
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))
    headings = {f"H{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}
    words = soup.get_text().lower().split()
    word_freq = {word: words.count(word) for word in set(words)}
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    indexability_data = extract_indexability_data(url, soup)
    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "headings": headings,
        "keyword_density": sorted_keywords,
        "indexability": indexability_data
    }

# Streamlit UI
def main():
    inject_custom_css()
    st.title("SEO Analyzer by Yahya")
    url = st.text_input("Enter a webpage URL:", key="url_input")
    
    if st.button("Extract SEO Data"):
        if url:
            html = fetch_html(url)
            if html:
                seo_data = extract_seo_data(html, url)
                
                st.subheader("🔍 SEO Score:")
                st.write(f"**Title:** {seo_data['title']}")
                st.write(f"**Meta Description:** {seo_data['meta_description']}")
                st.write(f"**H1:** {seo_data['h1']}")
                st.write(f"**Word Count:** {seo_data['word_count']}")
                st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")
                
                st.subheader("📊 Heading Structure:")
                for h, count in seo_data["headings"].items():
                    st.write(f"**{h}:** {count}")
                
                st.subheader("🔑 Keyword Density (Top 10):")
                for word, count in seo_data["keyword_density"]:
                    st.write(f"**{word}**: {count} times")
                
                # Indexability Section
                st.subheader("🛠️ Indexability")
                indexability = seo_data["indexability"]
                st.write(f"**Canonical URL:** {indexability['Canonical URL']}")
                st.write(f"**Self-Canonical:** {indexability['Self-Canonical']}")
                st.write(f"**Robots.txt:** {indexability['Robots.txt']}")
                st.write(f"**Robots Meta Tag:** {indexability['Robots Meta Tag']}")
                st.write(f"**X-Robots-Tag HTTP:** {indexability['X-Robots-Tag HTTP']}")
                st.write(f"**Sitemaps:** {indexability['Sitemaps']}")
                st.write(f"**Hreflangs:** {indexability['Hreflangs']}")

if __name__ == "__main__":
    main()
