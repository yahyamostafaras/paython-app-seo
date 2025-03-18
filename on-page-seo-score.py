import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
        return None

def extract_seo_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else "Title not found"
    
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'] if meta_desc_tag else "Meta description not found"
    
    h1_tags = soup.find_all('h1')
    h1 = h1_tags[0].text.strip() if h1_tags else "H1 not found"
    h1_count = len(h1_tags)
    
    word_count = len(soup.get_text().split())
    images = soup.find_all('img')
    missing_alt = sum(1 for img in images if not img.get('alt'))
    
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    canonical = canonical_tag['href'] if canonical_tag else "Canonical tag not found"
    
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    mobile_friendly = "Yes" if viewport_meta else "No viewport meta tag found"
    
    schema_markup = "Yes" if soup.find('script', attrs={'type': 'application/ld+json'}) else "No schema markup found"
    
    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "h1_count": h1_count,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "canonical": canonical,
        "mobile_friendly": mobile_friendly,
        "schema_markup": schema_markup
    }

def calculate_seo_score(seo_data):
    score = 0
    improvements = []
    
    if 50 <= len(seo_data["title"]) <= 60:
        score += 10
    else:
        improvements.append("Optimize title length (50-60 characters).")
    
    if 120 <= len(seo_data["meta_description"]) <= 160:
        score += 10
    else:
        improvements.append("Optimize meta description (120-160 characters).")
    
    if seo_data["h1"] != "H1 not found":
        score += 10
    else:
        improvements.append("Ensure an H1 tag is present on the page.")
    
    if seo_data["h1_count"] == 1:
        score += 10
    else:
        improvements.append("Avoid multiple H1 tags. Use only one per page.")
    
    if seo_data["word_count"] >= 300:
        score += 10
    else:
        improvements.append("Increase content length (minimum 300 words).")
    
    if seo_data["missing_alt"] == 0:
        score += 10
    else:
        improvements.append(f"{seo_data['missing_alt']} images are missing ALT attributes.")
    
    if seo_data["canonical"] != "Canonical tag not found":
        score += 10
    else:
        improvements.append("Add a canonical tag to prevent duplicate content issues.")
    
    if seo_data["mobile_friendly"] == "Yes":
        score += 10
    else:
        improvements.append("Ensure mobile-friendliness by adding a viewport meta tag.")
    
    if seo_data["schema_markup"] == "Yes":
        score += 10
    else:
        improvements.append("Consider adding schema markup for better SEO.")
    
    return score, improvements

def main():
    st.title("Advanced SEO Analyzer")
    url = st.text_input("Enter a webpage URL:")
    
    if st.button("Analyze SEO") or st.session_state.get("enter_pressed"):
        if url:
            html = fetch_html(url)
            if html:
                seo_data = extract_seo_data(html)
                seo_score, improvements = calculate_seo_score(seo_data)
                
                st.subheader("SEO Score: ")
                st.markdown(f"### {seo_score} / 100")
                
                st.write("**Title:**", seo_data["title"])
                st.write("**Meta Description:**", seo_data["meta_description"])
                st.write("**H1:**", seo_data["h1"])
                st.write(f"**H1 Count:** {seo_data['h1_count']}")
                st.write(f"**Word Count:** {seo_data['word_count']}")
                st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")
                st.write(f"**Canonical URL:** {seo_data['canonical']}")
                st.write(f"**Mobile Friendly:** {seo_data['mobile_friendly']}")
                st.write(f"**Schema Markup Present:** {seo_data['schema_markup']}")
                
                if improvements:
                    st.subheader("SEO Improvements Suggested:")
                    for improvement in improvements:
                        st.write(f"- {improvement}")
    
    st.session_state["enter_pressed"] = st.text_input("Press ENTER to submit", key="enter_key")

if __name__ == "__main__":
    main()
