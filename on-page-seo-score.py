import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to fetch HTML content
def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

# Function to extract SEO data
def extract_seo_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract Title
    title = soup.title.string.strip() if soup.title else "Title not found"

    # Extract Meta Description with fallback to og:description
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc_tag:
        meta_desc_tag = soup.find('meta', attrs={'property': 'og:description'})  # Open Graph fallback
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag else "Meta description not found"

    # Extract H1 tag
    h1_tag = soup.find('h1')
    h1 = h1_tag.text.strip() if h1_tag else "H1 not found"

    # Word count
    word_count = len(soup.get_text().split())

    # Count images missing ALT attributes
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
    }

# Function to calculate SEO score
def calculate_seo_score(seo_data):
    score = 0
    
    # Title length check
    if 50 <= len(seo_data["title"]) <= 60:
        score += 20  # More weight since title is important

    # Meta Description scoring
    if "not found" not in seo_data["meta_description"].lower():
        if 120 <= len(seo_data["meta_description"]) <= 160:
            score += 20
        else:
            score += 10  # Partial score if found but incorrect length

    # H1 presence
    if seo_data["h1"] != "H1 not found":
        score += 15

    # Word count
    if seo_data["word_count"] >= 300:
        score += 10

    # Image ALT tags (Gradual scoring)
    if seo_data["missing_alt"] == 0:
        score += 15
    elif seo_data["missing_alt"] <= 5:
        score += 10
    elif seo_data["missing_alt"] <= 10:
        score += 5

    return score

# Streamlit App UI
def main():
    st.title("🚀 SEO Analyzer Tool")

    url = st.text_input("Enter a webpage URL:", key="url_input")

    # If Enter is pressed or button clicked
    analyze = st.button("🔍 Analyze SEO") or st.session_state.get("enter_pressed")

    if analyze and url:
        html = fetch_html(url)
        if html:
            seo_data = extract_seo_data(html)
            seo_score = calculate_seo_score(seo_data)

            # Display SEO Score
            st.subheader("SEO Score:")
            st.markdown(f"### {seo_score} / 100")

            # Display Extracted SEO Data
            st.write("**Title:**", seo_data["title"])
            st.write("**Meta Description:**", seo_data["meta_description"])
            st.write("**H1:**", seo_data["h1"])
            st.write(f"**Word Count:** {seo_data['word_count']}")
            st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")

    # Capture Enter Key Press
    st.session_state["enter_pressed"] = st.text_input("Press ENTER to analyze", key="enter_key")

# Run Streamlit App
if __name__ == "__main__":
    main()
