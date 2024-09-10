import streamlit as st
import pandas as pd
import requests
import time
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fetch_html(url, use_fake_agent, delay):
    headers = {
        "User-Agent": get_random_user_agent() if use_fake_agent else "Python Requests",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    try:
        time.sleep(delay / 1000)  # Convert milliseconds to seconds
        
        if "etstur.com" in url:
            headers["Referer"] = "https://www.etstur.com/"
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.ConnectionError as conn_err:
        return f"Error connecting: {conn_err}"
    except requests.Timeout as timeout_err:
        return f"Timeout error: {timeout_err}"
    except requests.RequestException as req_err:
        return f"Error fetching HTML: {req_err}"

def analyze_url(url, char_count, search_phrase, use_fake_agent, delay):
    html = fetch_html(url, use_fake_agent, delay)
    if html.startswith(("Error", "HTTP error", "Timeout error")):
        return {
            "URL": url,
            "Status": "Error",
            "Last Characters": "",
            "Includes Phrase": False,
            "Error Message": html
        }
    
    last_part = html[-char_count:]
    
    return {
        "URL": url,
        "Status": "Success",
        "Last Characters": last_part,
        "Includes Phrase": search_phrase.lower() in last_part.lower(),
        "Error Message": ""
    }

st.title("Advanced Raw HTML Analyzer")

urls = st.text_area("Enter URLs (one per line)")
char_count = st.number_input("Character count to analyze from the end", min_value=1, value=100)
search_phrase = st.text_input("Search phrase")

# New options
use_fake_agent = st.checkbox("Use fake user agent", value=True, help="Enable to use random user agents for requests")
delay = st.number_input("Delay between requests (milliseconds)", min_value=0, value=1000, step=100, help="Time to wait between each URL request")

if st.button("Analyze URLs"):
    url_list = [url.strip() for url in urls.split('\n') if url.strip()]
    total_urls = len(url_list)
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, url in enumerate(url_list, 1):
        status_text.text(f"Processing URL {i} of {total_urls}: {url}")
        result = analyze_url(url, char_count, search_phrase, use_fake_agent, delay)
        results.append(result)
        progress_bar.progress(i / total_urls)
    
    status_text.text("Analysis complete!")
    
    df = pd.DataFrame(results)
    
    # Display results in a table
    st.subheader("Analysis Results")
    st.dataframe(df)
    
    # Show detailed results in expandable sections
    st.subheader("Detailed Results")
    for index, row in df.iterrows():
        with st.expander(f"Details for {row['URL']}"):
            st.write(f"Status: {row['Status']}")
            if row['Status'] == "Success":
                st.text(f"Last {char_count} characters:")
                st.code(row['Last Characters'], language='html')
                st.write(f"Includes search phrase: {'Yes' if row['Includes Phrase'] else 'No'}")
            else:
                st.error(row['Error Message'])
    
    # Provide CSV download option for table data
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results Table as CSV",
        data=csv,
        file_name="url_analysis_summary.csv",
        mime="text/csv",
    )
