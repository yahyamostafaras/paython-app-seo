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
        /* Center the Title and Content */
        .stTitle { text-align: center !important; }
        .stButton { text-align: center !important; display: flex; justify-content: center; }
        .stTextInput>div>div>input { text-align: center !important; }
        
        /* Custom Fonts & Styling */
        body { font-family: 'Arial', sans-serif; background-color: #f8f9fa; color: #333; }
        .reportview-container { padding-top: 2rem; }
        .stMarkdown h2 { color: #007bff; }
        
        /* SEO Score Styling */
        .seo-score { font-size: 2rem; font-weight: bold; text-align: center; color: #28a745; }
        
        /* Dark Mode (Optional) */
        @media (prefers-color-scheme: dark) {
            body { background-color: #121212; color: #ddd; }
            .stMarkdown h2 { color: #1abc9c; }
            .seo-score { color: #1abc9c; }
        }
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

# Extract SEO-related data
def extract_seo_data(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Title extraction
    title = soup.title.string.strip() if soup.title else "Title not found"
    
    # Meta Description Extraction
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    og_desc_tag = soup.find('meta', attrs={'property': 'og:description'})
    
    if meta_desc_tag and meta_desc_tag.get('content'):
        meta_desc = meta_desc_tag['content'].strip()
    elif og_desc_tag and og_desc_tag.get('content'):
        meta_desc = og_desc_tag['content'].strip()
    else:
        meta_desc = "Meta description not found"
    
    # Canonical URL Extraction
    canonical_tag = soup.find('link', rel='canonical')
    canonical_url = canonical_tag['href'].strip() if canonical_tag else "Canonical tag not found"
    is_canonical_correct = "✅ Matches Entered URL" if canonical_url == url else "❌ Does Not Match Entered URL"
    
    # H1 extraction
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else "H1 not found"
    
    # Word count
    word_count = len(soup.get_text().split())
    
    # Image ALT analysis
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))
    
    # Heading structure
    headings = {f"H{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}
    
    # Keyword density (most frequent words)
    words = soup.get_text().lower().split()
    word_freq = {word: words.count(word) for word in set(words)}
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "title": title,
        "meta_description": meta_desc,
        "canonical_url": canonical_url,
        "canonical_status": is_canonical_correct,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "headings": headings,
        "keyword_density": sorted_keywords
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
                
                # Display results
                st.subheader("🔍 SEO Score:")
                st.write(f"**Title:** {seo_data['title']}")
                st.write(f"**Meta Description:** {seo_data['meta_description']}")
                st.write(f"**Canonical URL:** {seo_data['canonical_url']}")
                st.write(f"**Canonical Status:** {seo_data['canonical_status']}")
                st.write(f"**H1:** {seo_data['h1']}")
                st.write(f"**Word Count:** {seo_data['word_count']}")
                st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")
                
                st.subheader("📊 Heading Structure:")
                for h, count in seo_data["headings"].items():
                    st.write(f"**{h}:** {count}")
                
                st.subheader("🔑 Keyword Density (Top 10):")
                for word, count in seo_data["keyword_density"]:
                    st.write(f"**{word}**: {count} times")
                
                # Display Instructions in a Table
                st.subheader("📌 SEO Improvement Instructions:")
                instructions = {
                    "Improve Title": "Ensure the title is 50-60 characters.",
                    "Optimize Meta Description": "Keep it between 120-160 characters.",
                    "Fix Canonical URL": "Make sure the canonical URL matches the entered URL.",
                    "Add H1": "Ensure an H1 tag is present.",
                    "Increase Word Count": "Aim for at least 300 words.",
                    "Fix ALT Tags": "Add ALT attributes to all images.",
                    "Improve Heading Structure": "Use H2s and H3s for better readability.",
                    "Optimize Keywords": "Use relevant keywords naturally."
                }
                df_instructions = pd.DataFrame(list(instructions.items()), columns=["Action", "Instruction"])
                st.table(df_instructions)

if __name__ == "__main__":
    main()
