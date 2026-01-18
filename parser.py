import re
import os

def classify_link(link):
    """Return category based on URL domain."""
    link_lower = link.lower()
    
    if 'twitter.com' in link_lower or 'x.com' in link_lower:
        return 'twitter'
    
    tech_domains = [
        'github.com', 'stackoverflow.com', 'arxiv.org', 'huggingface.co', 
        'dev.to', 'medium.com', 'hashnode.com', 'kaggle.com', 
        'news.ycombinator.com', 'python.org', 'docs.google.com', 
        'youtube.com', 'youtu.be',
        'linkedin.com/jobs', 'linkedin.com/posts', 'careers'
    ]
    
    for domain in tech_domains:
        if domain in link_lower:
            return 'tech'
            
    return 'misc'

def extract_tweet_id(url):
    """Extract tweet ID from URL."""
    match = re.search(r'/status/(\d+)', url)
    if match:
        return match.group(1)
    return None

def generate_site():
    input_file = './cht_history/_chat180626.txt'
    output_file = 'bookmarks.md'
    
    url_pattern = r'https?://\S+'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    raw_links = re.findall(url_pattern, content)
    clean_links = [link.strip(',').strip(')') for link in raw_links]
    unique_links = list(dict.fromkeys(clean_links))
    unique_links.reverse()

    twitter_links = []
    tech_links = []
    misc_links = []

    for link in unique_links:
        category = classify_link(link)
        if category == 'twitter':
            tweet_id = extract_tweet_id(link)
            if tweet_id:  # Only include if we can extract the ID
                twitter_links.append((link, tweet_id))
        elif category == 'tech':
            tech_links.append(link)
        else:
            if "whatsapp.com" not in link:
                misc_links.append(link)

    tweets_per_page = 6  # Fewer per page for better loading
    total_tweet_pages = (len(twitter_links) + tweets_per_page - 1) // tweets_per_page

    md_content = [
        "---",
        "layout: default",
        "title: Bookmarks",
        "---",
        "",
        "# Link Vault",
        "",
        "---",
        ""
    ]

    if twitter_links:
        md_content.append("## X / Twitter")
        md_content.append("")
        md_content.append(f'<p class="small-text">{len(twitter_links)} posts • Page <span id="current-page">1</span> of {total_tweet_pages}</p>')
        md_content.append("")
        
        # CSS for tweet iframe grid
        md_content.append("""
<style>
.tweet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}
.tweet-frame {
  border: 1px solid #e1e8ed;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  min-height: 250px;
}
.tweet-frame iframe {
  width: 100%;
  height: 350px;
  border: none;
}
.page-nav { 
  margin: 30px 0; 
  text-align: center; 
}
.page-nav button { 
  background: #fff; 
  border: 1px solid #ddd; 
  padding: 10px 20px; 
  margin: 0 4px; 
  cursor: pointer; 
  border-radius: 6px; 
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.page-nav button:hover:not(:disabled) { 
  border-color: #e06e2e; 
  color: #e06e2e; 
}
.page-nav button.active { 
  background: #e06e2e; 
  color: white; 
  border-color: #e06e2e; 
}
.page-nav button:disabled { 
  opacity: 0.4; 
  cursor: not-allowed; 
}
.tweet-page { 
  display: none; 
}
.tweet-page.active { 
  display: block; 
}
@media (max-width: 768px) {
  .tweet-grid {
    grid-template-columns: 1fr;
  }
}
</style>
""")
        
        md_content.append('<div id="twitter-section">')
        
        # Generate pages with tweet iframes
        for page_num in range(total_tweet_pages):
            start_idx = page_num * tweets_per_page
            end_idx = min(start_idx + tweets_per_page, len(twitter_links))
            page_tweets = twitter_links[start_idx:end_idx]
            
            active = " active" if page_num == 0 else ""
            md_content.append(f'<div class="tweet-page{active}" data-page="{page_num}">')
            md_content.append('<div class="tweet-grid">')
            
            for original_url, tweet_id in page_tweets:
                # Use Twitter's embed iframe directly
                iframe_url = f"https://platform.twitter.com/embed/Tweet.html?id={tweet_id}&theme=light"
                md_content.append(f'''<div class="tweet-frame">
<iframe src="{iframe_url}" loading="lazy" allowtransparency="true"></iframe>
</div>''')
            
            md_content.append('</div>')
            md_content.append('</div>')
        
        md_content.append('<div class="page-nav" id="page-nav"></div>')
        md_content.append('</div>')
        
        # Pagination JS
        md_content.append(f"""
<script>
(function() {{
  const totalPages = {total_tweet_pages};
  const pages = document.querySelectorAll('.tweet-page');
  const nav = document.getElementById('page-nav');
  const currentPageSpan = document.getElementById('current-page');
  
  function show(idx) {{
    pages.forEach((p, i) => {{
      p.classList.toggle('active', i === idx);
    }});
    render(idx);
    currentPageSpan.textContent = idx + 1;
    document.getElementById('twitter-section').scrollIntoView({{behavior: 'smooth', block: 'start'}});
  }}
  
  function render(idx) {{
    nav.innerHTML = '';
    
    const prev = document.createElement('button');
    prev.textContent = '← Previous';
    prev.disabled = idx === 0;
    prev.onclick = () => show(idx - 1);
    nav.appendChild(prev);
    
    let start = Math.max(0, idx - 2);
    let end = Math.min(totalPages - 1, start + 4);
    if (end - start < 4) start = Math.max(0, end - 4);
    
    for (let i = start; i <= end; i++) {{
      const btn = document.createElement('button');
      btn.textContent = i + 1;
      if (i === idx) btn.classList.add('active');
      btn.onclick = () => show(i);
      nav.appendChild(btn);
    }}
    
    const next = document.createElement('button');
    next.textContent = 'Next →';
    next.disabled = idx === totalPages - 1;
    next.onclick = () => show(idx + 1);
    nav.appendChild(next);
  }}
  
  render(0);
}})();
</script>
""")

    # Tech Section
    if tech_links:
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## Tech & Engineering")
        md_content.append("")
        md_content.append('<ul class="link-list">')
        for link in tech_links:
            domain = re.search(r'https?://(?:www\.)?([^/]+)', link)
            domain_name = domain.group(1) if domain else link
            md_content.append(f'<li><a href="{link}" target="_blank">{domain_name}</a></li>')
        md_content.append('</ul>')

    # Misc Section
    if misc_links:
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        md_content.append("## Other Links")
        md_content.append("")
        md_content.append('<ul class="link-list">')
        for link in misc_links:
            domain = re.search(r'https?://(?:www\.)?([^/]+)', link)
            domain_name = domain.group(1) if domain else link
            md_content.append(f'<li><a href="{link}" target="_blank">{domain_name}</a></li>')
        md_content.append('</ul>')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Generated bookmarks with {len(unique_links)} total links:")
    print(f"  - Twitter: {len(twitter_links)} ({total_tweet_pages} pages)")
    print(f"  - Tech: {len(tech_links)}")
    print(f"  - Misc: {len(misc_links)}")

if __name__ == "__main__":
    generate_site()
