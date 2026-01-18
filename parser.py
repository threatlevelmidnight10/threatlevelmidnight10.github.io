import re
import os

# Client-side pagination script for Twitter section + Standard Twitter Widget
PAGINATION_SCRIPT = '''
<script>
window.twttr = (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0],
    t = window.twttr || {};
  if (d.getElementById(id)) return t;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);

  t._e = [];
  t.ready = function(f) {
    t._e.push(f);
  };

  return t;
}(document, "script", "twitter-wjs"));

document.addEventListener('DOMContentLoaded', function() {
  const pages = document.querySelectorAll('.tweet-page');
  const paginationContainer = document.getElementById('pagination-controls');
  
  if (pages.length > 0) {
    let currentPage = 0;
    
    function showPage(index) {
      pages.forEach((page, i) => {
        if (i === index) {
          page.classList.add('active');
          // Important: Trigger render on the active page
          twttr.ready(function() {
             twttr.widgets.load(page);
          });
        } else {
          page.classList.remove('active');
        }
      });
      updateButtons(index);
      currentPage = index;
    }

    function updateButtons(index) {
      paginationContainer.innerHTML = '';
      
      // Prev Button
      const prevBtn = document.createElement('button');
      prevBtn.innerText = '← Prev';
      prevBtn.disabled = index === 0;
      prevBtn.onclick = () => {
         showPage(index - 1);
         document.getElementById('twitter-section').scrollIntoView({behavior: 'smooth'});
      };
      paginationContainer.appendChild(prevBtn);

      // Page Numbers (Window of 5)
      let start = Math.max(0, index - 2);
      let end = Math.min(pages.length - 1, start + 4);
      if (end - start < 4) start = Math.max(0, end - 4);

      for (let i = start; i <= end; i++) {
        const btn = document.createElement('button');
        btn.innerText = i + 1;
        if (i === index) btn.classList.add('active');
        btn.onclick = () => {
            showPage(i);
            document.getElementById('twitter-section').scrollIntoView({behavior: 'smooth'});
        };
        paginationContainer.appendChild(btn);
      }

      // Next Button
      const nextBtn = document.createElement('button');
      nextBtn.innerText = 'Next →';
      nextBtn.disabled = index === pages.length - 1;
      nextBtn.onclick = () => {
          showPage(index + 1);
          document.getElementById('twitter-section').scrollIntoView({behavior: 'smooth'});
      };
      paginationContainer.appendChild(nextBtn);
    }

    // Initial Load
    showPage(0);
  }
});
</script>
'''

def classify_link(link):
    """Return category based on URL domain."""
    link = link.lower()
    
    # Twitter / X
    if 'twitter.com' in link or 'x.com' in link:
        return 'twitter'
    
    # Tech / Dev
    tech_domains = [
        'github.com', 'stackoverflow.com', 'arxiv.org', 'huggingface.co', 
        'dev.to', 'medium.com', 'hashnode.com', 'kaggle.com', 
        'news.ycombinator.com', 'python.org', 'docs.google.com', 
        'youtube.com/playlist', 'youtu.be', 'youtube.com', # Assuming playlists/videos are often tech talks in context
        'linkedin.com', 'jobs', 'careers' # Grouping jobs with tech/professional
    ]
    
    for domain in tech_domains:
        if domain in link:
            return 'tech'
            
    # Everything else
    return 'misc'

def generate_site():
    input_file = './cht_history/_chat180626.txt'
    output_file = 'bookmarks.md'
    
    # Matches URLs
    url_pattern = r'https?://\S+'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all links
    raw_links = re.findall(url_pattern, content)
    
    # Remove trailing punctuation (common in chat exports)
    clean_links = [link.strip(',').strip(')') for link in raw_links]
    
    # Deduplicate while preserving order (using dict)
    unique_links = list(dict.fromkeys(clean_links))
    
    # REVERSE Logic: Newest links are usually at the bottom of chat logs
    unique_links.reverse()

    # Categorize
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
            if "whatsapp.com" not in link: # Filter noise
                misc_links.append(link)

    # Begin Markdown Construction
    md_content = [
        "---",
        "layout: default",
        "title: Bookmarks",
        "---",
        "",
        "# Link Vault",
        "Curated from my personal chat history.",
        "",
        "---",
        "",
        PAGINATION_SCRIPT
    ]

    # SECTION 1: X / Twitter (Paginated)
    if twitter_links:
        md_content.append('<div id="twitter-section">')
        md_content.append('<h3 class="category-header">X / Twitter Updates</h3>')
        
        chunk_size = 20
        # Split into chunks
        page_chunks = [twitter_links[i:i + chunk_size] for i in range(0, len(twitter_links), chunk_size)]
        
        for i, chunk in enumerate(page_chunks):
            # Page container
            active_class = " active" if i == 0 else ""
            md_content.append(f'<div class="tweet-page{active_class}" id="page-{i}">')
            for link in chunk:
                md_content.append(f'<blockquote class="twitter-tweet"><a href="{link}"></a></blockquote>')
            md_content.append('</div>')
            
        md_content.append('<div id="pagination-controls" class="pagination"></div>')
        md_content.append('</div>')

    # SECTION 2: Tech & Dev
    if tech_links:
        md_content.append('<h3 class="category-header">Tech, AI & Engineering</h3>')
        md_content.append('<ul class="link-list">')
        for link in tech_links:
            md_content.append(f'<li><a href="{link}" target="_blank">{link}</a></li>')
        md_content.append('</ul>')

    # SECTION 3: Misc
    if misc_links:
        md_content.append('<h3 class="category-header">Miscellaneous</h3>')
        md_content.append('<ul class="link-list">')
        for link in misc_links:
            md_content.append(f'<li><a href="{link}" target="_blank">{link}</a></li>')
        md_content.append('</ul>')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Site updated with {len(unique_links)} total links.")
    print(f"- Twitter: {len(twitter_links)} ({len(page_chunks)} pages)")
    print(f"- Tech: {len(tech_links)}")
    print(f"- Misc: {len(misc_links)}")

if __name__ == "__main__":
    generate_site()
