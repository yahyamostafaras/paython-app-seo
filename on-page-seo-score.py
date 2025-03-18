import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import pandas as pd

def fetch_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

def extract_seo_data(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string.strip() if soup.title else "Title not found"
    
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag else "Meta description not found"
    
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else "H1 not found"
    
    word_count = len(soup.get_text().split())
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))
    
    canonical_tag = soup.find('link', rel='canonical')
    canonical_url = canonical_tag['href'] if canonical_tag else "Canonical URL not found"
    
    robots_tag = soup.find('meta', attrs={'name': 'robots'})
    robots_content = robots_tag['content'] if robots_tag else "Indexable"
    
    publisher_tag = soup.find('meta', attrs={'name': 'publisher'})
    publisher = publisher_tag['content'] if publisher_tag else "Publisher not found"
    
    json_ld_data = []
    for script in soup.find_all('script', {'type': 'application/ld+json'}):
        try:
            json_ld_data.append(json.loads(script.string))
        except (json.JSONDecodeError, TypeError):
            pass
    
    internal_links, external_links, broken_links = analyze_links(soup, url)
    
    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "canonical_url": canonical_url,
        "robots": robots_content,
        "publisher": publisher,
        "structured_data": json_ld_data,
        "total_links": len(internal_links) + len(external_links),
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "broken_links": len(broken_links),
    }

def analyze_links(soup, base_url):
    parsed_base = urlparse(base_url)
    internal_links = set()
    external_links = set()
    broken_links = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        
        if parsed_url.netloc == parsed_base.netloc:
            internal_links.add(full_url)
        else:
            external_links.add(full_url)
        
        try:
            response = requests.head(full_url, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                broken_links.add(full_url)
        except requests.RequestException:
            broken_links.add(full_url)
    
    return internal_links, external_links, broken_links

def calculate_seo_score(seo_data):
    score = 0
    improvements = []
    
    if 50 <= len(seo_data["title"]) <= 60:
        score += 15
    else:
        improvements.append("Title length should be between 50-60 characters.")
    
    if 120 <= len(seo_data["meta_description"]) <= 160:
        score += 15
    else:
        improvements.append("Meta description should be between 120-160 characters.")
    
    if seo_data["h1"] != "H1 not found":
        score += 10
    else:
        improvements.append("Add an H1 tag.")
    
    if seo_data["word_count"] >= 300:
        score += 15
    else:
        improvements.append("Increase content length to at least 300 words.")
    
    if seo_data["missing_alt"] == 0:
        score += 10
    else:
        improvements.append(f"Add ALT text to {seo_data['missing_alt']} images.")
    
    if seo_data["broken_links"] == 0:
        score += 10
    else:
        improvements.append(f"Fix {seo_data['broken_links']} broken links.")
    
    if seo_data["robots"].lower() == "indexable":
        score += 10
    else:
        improvements.append("Check robots meta tag settings.")
    
    return score, improvements

def main():
    st.title("SEO Audit Tool by Yahya")
    url = st.text_input("Enter a webpage URL:")
    
    if st.button("Analyze SEO"):
        if url:
            html = fetch_html(url)
            if html:
                seo_data = extract_seo_data(html, url)
                seo_score, improvements = calculate_seo_score(seo_data)
                
                st.subheader("SEO Score: ")
                st.markdown(f"### {seo_score} / 100")
                
                st.write("**Title:**", seo_data["title"])
                st.write("**Meta Description:**", seo_data["meta_description"])
                st.write("**H1:**", seo_data["h1"])
                st.write(f"**Word Count:** {seo_data['word_count']}")
                st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")
                st.write(f"**Canonical URL:** {seo_data['canonical_url']}")
                st.write(f"**Robots Tag:** {seo_data['robots']}")
                st.write(f"**Publisher:** {seo_data['publisher']}")
                st.write(f"**Total Links:** {seo_data['total_links']}")
                st.write(f"**Internal Links:** {seo_data['internal_links']}")
                st.write(f"**External Links:** {seo_data['external_links']}")
                st.write(f"**Broken Links:** {seo_data['broken_links']}")
                
                st.subheader("Structured Data (JSON-LD)")
                st.json(seo_data["structured_data"])
                
                if improvements:
                    st.subheader("Suggestions for Improvement")
                    for improvement in improvements:
                        st.write(f"- {improvement}")

if __name__ == "__main__":
    main()
