from bs4 import BeautifulSoup

def clean_html_description(html_text):
    try:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return html_text
