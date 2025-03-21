import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Inject Custom CSS
def inject_custom_css():
    st.markdown(
        """
        <style>
        .stTitle { text-align: center !important; }
        .stButton { text-align: center !important; display: flex; justify-content: center; }
        .stTextInput>div>div>input { text-align: center !important; }
        body { font-family: 'Arial', sans-serif; background-color: #f8f9fa; color: #333; }
        .seo-score { font-size: 2rem; font-weight: bold; text-align: center; color: #28a745; }
        .stTable { margin-top: 20px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# Fetch HTML from URL
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
    
    # Get Sitemap URL Correctly
    sitemap_tag = soup.find('link', rel='sitemap')
    if sitemap_tag and sitemap_tag.get('href'):
        sitemap_url = sitemap_tag['href']
    else:
        parsed_url = urlparse(url)
        sitemap_url = f"{parsed_url.scheme}://{parsed_url.netloc}/sitemap.xml"
    
    robots_txt_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    hreflang_tags = soup.find_all('link', rel='alternate', hreflang=True)
    hreflangs = len(hreflang_tags) if hreflang_tags else "Missing"
    
    return {
        "Canonical URL": canonical_url,
        "Self-Canonical": "✅ Matches URL" if canonical_url == url else "❌ Does Not Match",
        "Robots.txt": robots_txt_url,
        "Robots Meta Tag": robots_meta_content,
        "X-Robots-Tag HTTP": x_robots_content,
        "Sitemap": sitemap_url,
        "Hreflangs": hreflangs
    }

# Extract SEO Data
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

    seo_score = calculate_seo_score(title, meta_desc, h1, word_count, missing_alt, indexability_data)

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "headings": headings,
        "keyword_density": sorted_keywords,
        "indexability": indexability_data,
        "seo_score": seo_score
    }

# Calculate SEO Score
def calculate_seo_score(title, meta_desc, h1, word_count, missing_alt, indexability):
    score = 100

    if title == "Title not found":
        score -= 10
    if meta_desc == "Meta description not found":
        score -= 10
    if h1 == "H1 not found":
        score -= 10
    if word_count < 300:
        score -= 15
    if missing_alt > 0:
        score -= 10
    if indexability["Canonical URL"] == "Missing":
        score -= 10
    if indexability["Robots Meta Tag"] == "Missing":
        score -= 5
    if indexability["X-Robots-Tag HTTP"] == "Missing":
        score -= 5
    if indexability["Hreflangs"] == "Missing":
        score -= 5

    return max(score, 0)

# Generate To-Do List
def generate_todo_list(seo_data):
    todo_list = []

    if seo_data["title"] == "Title not found":
        todo_list.append(["Title Tag", "Add a proper title for SEO."])
    
    if seo_data["meta_description"] == "Meta description not found":
        todo_list.append(["Meta Description", "Add a relevant meta description."])
    
    if seo_data["h1"] == "H1 not found":
        todo_list.append(["H1 Tag", "Ensure there is a primary H1 tag."])
    
    if seo_data["word_count"] < 300:
        todo_list.append(["Content Length", "Increase word count to at least 300+."])
    
    if seo_data["missing_alt"] > 0:
        todo_list.append(["Image ALT Tags", f"Add ALT text to {seo_data['missing_alt']} images."])
    
    indexability = seo_data["indexability"]
    if indexability["Canonical URL"] == "Missing":
        todo_list.append(["Canonical URL", "Add a canonical URL to prevent duplicate content."])
    
    if indexability["Robots Meta Tag"] == "Missing":
        todo_list.append(["Robots Meta Tag", "Add a robots meta tag for better control."])
    
    if indexability["X-Robots-Tag HTTP"] == "Missing":
        todo_list.append(["X-Robots-Tag", "Consider setting an X-Robots-Tag HTTP header."])
    
    if indexability["Hreflangs"] == "Missing":
        todo_list.append(["Hreflang Tags", "Add hreflang tags for multilingual sites."])
    
    return todo_list

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
                st.markdown(f"<p class='seo-score'>{seo_data['seo_score']} / 100</p>", unsafe_allow_html=True)
                
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
                
                st.subheader("🛠️ Indexability")
                indexability = seo_data["indexability"]
                for key, value in indexability.items():
                    st.write(f"**{key}:** {value}")

                st.subheader("✅ SEO To-Do List")
                todo_list = generate_todo_list(seo_data)
                if todo_list:
                    st.table(pd.DataFrame(todo_list, columns=["Issue", "Recommended Action"]))
                else:
                    st.success("No major SEO issues found!")

if __name__ == "__main__":
    main()
