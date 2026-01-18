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

def extract_tweet_info(url):
    """Extract username and tweet ID from URL."""
    match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)', url)
    if match:
        username = match.group(1)
        tweet_id = match.group(2)
        if username != 'i':
            return username, tweet_id
    
    id_match = re.search(r'/status/(\d+)', url)
    if id_match:
        return None, id_match.group(1)
    
    return None, None

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
            twitter_links.append(link)
        elif category == 'tech':
            tech_links.append(link)
        else:
            if "whatsapp.com" not in link:
                misc_links.append(link)

    # Smaller pages = better loading performance
    tweets_per_page = 10
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
        md_content.append(f'<p class="small-text">{len(twitter_links)} saved posts • Page <span id="current-page">1</span> of {total_tweet_pages}</p>')
        md_content.append("")
        
        # CSS for tweet grid with loading states
        md_content.append("""
<style>
.tweet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.tweet-container {
  min-height: 200px;
  background: #f8f9fa;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}
.tweet-container.loading::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.tweet-container.loading::after {
  content: '𝕏 Loading...';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 14px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.tweet-container iframe,
.tweet-container .twitter-tweet-rendered {
  margin: 0 !important;
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
</style>
""")
        
        md_content.append('<div id="twitter-section">')
        
        # Generate pages with tweet embeds
        for page_num in range(total_tweet_pages):
            start_idx = page_num * tweets_per_page
            end_idx = min(start_idx + tweets_per_page, len(twitter_links))
            page_tweets = twitter_links[start_idx:end_idx]
            
            active = " active" if page_num == 0 else ""
            md_content.append(f'<div class="tweet-page{active}" data-page="{page_num}">')
            md_content.append('<div class="tweet-grid">')
            
            for link in page_tweets:
                # Wrap each tweet in a container with loading state
                md_content.append(f'''<div class="tweet-container loading">
<blockquote class="twitter-tweet" data-dnt="true" data-theme="light">
<a href="{link}"></a>
</blockquote>
</div>''')
            
            md_content.append('</div>')
            md_content.append('</div>')
        
        md_content.append('<div class="page-nav" id="page-nav"></div>')
        md_content.append('</div>')
        
        # JavaScript: Twitter widget + Pagination + Lazy loading
        md_content.append(f"""
<script>
// Twitter widget loader
window.twttr = (function(d, s, id) {{
  var js, fjs = d.getElementsByTagName(s)[0], t = window.twttr || {{}};
  if (d.getElementById(id)) return t;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);
  t._e = [];
  t.ready = function(f) {{ t._e.push(f); }};
  return t;
}}(document, "script", "twitter-wjs"));

(function() {{
  const totalPages = {total_tweet_pages};
  const pages = document.querySelectorAll('.tweet-page');
  const nav = document.getElementById('page-nav');
  const currentPageSpan = document.getElementById('current-page');
  
  function loadTweets(container) {{
    twttr.ready(function(twttr) {{
      twttr.widgets.load(container);
      // Remove loading state when tweets are rendered
      twttr.events.bind('rendered', function(event) {{
        const tweetContainer = event.target.closest('.tweet-container');
        if (tweetContainer) {{
          tweetContainer.classList.remove('loading');
        }}
      }});
    }});
  }}
  
  function show(idx) {{
    pages.forEach((p, i) => {{
      const isActive = i === idx;
      p.classList.toggle('active', isActive);
      if (isActive) {{
        loadTweets(p);
      }}
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
  
  // Initial load
  render(0);
  twttr.ready(function() {{
    loadTweets(pages[0]);
  }});
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
    
    print(f"Generated bookmarks with {len(unique_links)} links:")
    print(f"  - Twitter: {len(twitter_links)} ({total_tweet_pages} pages of {tweets_per_page})")
    print(f"  - Tech: {len(tech_links)}")
    print(f"  - Misc: {len(misc_links)}")

if __name__ == "__main__":
    generate_site()
