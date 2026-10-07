import urllib.request
import xml.etree.ElementTree as ET
import re

FIXED_THUMBNAIL = "https://cdn.hashnode.com/uploads/covers/6a8c7f26549260acf3291b62/40f307aa-7b41-4d63-9afb-a0de90a33721.jpg"
RSS_URL = "https://robiulsuny.hashnode.dev/rss.xml"

def fetch_rss_items():
    req = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        tree = ET.fromstring(resp.read())
        return tree.find("channel").findall("item")

def generate_cards_html(items):
    # Take up to 6 latest posts for 2-column layout
    items = items[:6]

    cards_html = '<table width="100%" border="0" cellspacing="10" cellpadding="0">\n'
    for idx in range(0, len(items), 2):
        cards_html += "  <tr>\n"
        for j in range(2):
            if idx + j < len(items):
                item = items[idx + j]
                title = (item.find("title").text or "").strip()
                link = (item.find("link").text or "").strip()
                desc_elem = item.find("description")
                desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                clean_desc = re.sub(r"<[^>]+>", "", desc).replace("\n", " ").strip()
                clean_desc = re.sub(r"\s+", " ", clean_desc)
                if len(clean_desc) > 110:
                    clean_desc = clean_desc[:110] + "..."

                cards_html += f'''    <td width="50%" valign="top">
      <a href="{link}" target="_blank">
        <img src="{FIXED_THUMBNAIL}" alt="{title}" width="100%" style="border-radius: 8px; border: 1px solid #30363d; max-height: 220px; object-fit: cover;" />
      </a>
      <br/><br/>
      <a href="{link}" target="_blank" style="text-decoration: none;">
        <h3>{title}</h3>
      </a>
      <p>{clean_desc}</p>
    </td>\n'''
            else:
                cards_html += '    <td width="50%" valign="top"></td>\n'
        cards_html += "  </tr>\n"
    cards_html += "</table>"
    return cards_html

def update_readme(cards_html):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- HASHNODE-CARDS:START -->.*?<!-- HASHNODE-CARDS:END -->"
    replacement = f"<!-- HASHNODE-CARDS:START -->\n{cards_html}\n<!-- HASHNODE-CARDS:END -->"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README.md cards successfully updated from Hashnode RSS!")

def main():
    try:
        items = fetch_rss_items()
        if not items:
            print("No RSS items found.")
            return
        cards_html = generate_cards_html(items)
        update_readme(cards_html)
    except Exception as e:
        print(f"Error updating cards: {e}")
        raise

if __name__ == "__main__":
    main()
