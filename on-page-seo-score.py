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
def extract_seo_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Title extraction
    title = soup.title.string.strip() if soup.title else "Title not found"

    # Meta description extraction
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag else "Meta description not found"

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
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]  # Top 10 words

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1,
        "word_count": word_count,
        "missing_alt": missing_alt,
        "headings": headings,
        "keyword_density": sorted_keywords
    }

# Calculate SEO Score & Improvement Suggestions
def calculate_seo_score(seo_data):
    score = 0
    suggestions = []

    # Title length
    title_len = len(seo_data["title"])
    if 50 <= title_len <= 60:
        score += 15
    else:
        suggestions.append("✅ Optimize Title: Keep it between 50-60 characters.")

    # Meta description length
    meta_len = len(seo_data["meta_description"])
    if 120 <= meta_len <= 160:
        score += 15
    else:
        suggestions.append("✅ Improve Meta Description: Keep it between 120-160 characters.")

    # H1 presence
    if seo_data["h1"] != "H1 not found":
        score += 15
    else:
        suggestions.append("✅ Add an H1 tag: Every page should have a clear H1.")

    # Word count
    if seo_data["word_count"] >= 300:
        score += 15
    else:
        suggestions.append("✅ Add More Content: Aim for at least 300 words for SEO-friendly content.")

    # Image ALT attributes
    if seo_data["missing_alt"] == 0:
        score += 15
    else:
        suggestions.append(f"✅ Fix ALT Tags: {seo_data['missing_alt']} images are missing ALT attributes.")

    # H2 & H3 presence (for structure)
    if seo_data["headings"]["H2"] > 0 and seo_data["headings"]["H3"] > 0:
        score += 10
    else:
        suggestions.append("✅ Improve Headings: Add H2s and H3s for better content structure.")

    # Keyword density optimization
    top_keywords = [word for word, _ in seo_data["keyword_density"][:5]]
    suggestions.append(f"🔍 Top Keywords: {', '.join(top_keywords)} (Ensure they're relevant & used naturally).")

    return score, suggestions

# Convert SEO Data to Excel
def convert_to_excel(seo_data):
    output = BytesIO()
    df = pd.DataFrame.from_dict(seo_data, orient='index', columns=['Value'])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="SEO Data")
    output.seek(0)
    return output

# Streamlit UI
def main():
    inject_custom_css()  # Apply Custom CSS
    
    st.title("SEO Analyzer by Yahya")
    url = st.text_input("Enter a webpage URL:", key="url_input")

    if st.button("Extract SEO Data") or st.session_state.get("enter_pressed"):
        if url:
            html = fetch_html(url)
            if html:
                seo_data = extract_seo_data(html)
                seo_score, suggestions = calculate_seo_score(seo_data)

                # Display results
                st.subheader("🔍 SEO Score:")
                st.markdown(f"<div class='seo-score'>{seo_score} / 100</div>", unsafe_allow_html=True)

                st.write("**Title:**", seo_data["title"])
                st.write("**Meta Description:**", seo_data["meta_description"])
                st.write("**H1:**", seo_data["h1"])
                st.write(f"**Word Count:** {seo_data['word_count']}")
                st.write(f"**Images Missing ALT:** {seo_data['missing_alt']}")

                st.subheader("📊 Heading Structure:")
                for h, count in seo_data["headings"].items():
                    st.write(f"**{h}:** {count}")

                st.subheader("🔑 Keyword Density (Top 10):")
                for word, count in seo_data["keyword_density"]:
                    st.write(f"**{word}**: {count} times")

                # Display improvement suggestions
                if suggestions:
                    st.subheader("🚀 Suggested SEO Improvements:")
                    for suggestion in suggestions:
                        st.write("- " + suggestion)

                # Download button for Excel
                excel_data = convert_to_excel(seo_data)
                st.download_button("📥 Download SEO Report", excel_data, "SEO_Report.xlsx")

    st.session_state["enter_pressed"] = False

if __name__ == "__main__":
    main()
