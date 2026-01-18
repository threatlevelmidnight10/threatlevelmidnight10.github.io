import re
import os

LAZY_LOAD_SCRIPT = '''<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
<script>
// Lazy load Twitter embeds to fix the issue where only first few tweets render
document.addEventListener('DOMContentLoaded', function() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const tweet = entry.target;
        if (!tweet.dataset.loaded && window.twttr && window.twttr.widgets) {
          window.twttr.widgets.load(tweet);
          tweet.dataset.loaded = 'true';
        }
        observer.unobserve(tweet);
      }
    });
  }, { rootMargin: '200px' });

  // Wait for Twitter widgets to be ready
  function observeTweets() {
    document.querySelectorAll('blockquote.twitter-tweet').forEach(tweet => {
      if (!tweet.dataset.loaded) {
        observer.observe(tweet);
      }
    });
  }

  if (window.twttr && window.twttr.ready) {
    window.twttr.ready(observeTweets);
  } else {
    // Retry after widgets.js loads
    setTimeout(observeTweets, 2000);
  }
});
</script>'''

def generate_site():
    input_file = './cht_history/_chat180626.txt'
    output_file = 'bookmarks.md'
    
    # Updated regex: captures Twitter/X and general web links
    url_pattern = r'https?://\S+'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all links and remove trailing punctuation often found in WhatsApp exports
    raw_links = re.findall(url_pattern, content)
    unique_links = list(dict.fromkeys([link.strip(',').strip(')') for link in raw_links]))

    # Minimal Jekyll Setup
    md_content = [
        "---",
        "layout: default",
        "title: Bookmarks",
        "---",
        "",
        "# Bookmarks",
        "",
        "---",
        "",
        "## X / Twitter",
        "",
        LAZY_LOAD_SCRIPT
    ]

    twitter_links = []
    other_links = []

    for link in unique_links:
        if 'twitter.com' in link or 'x.com' in link:
            twitter_links.append(link)
        else:
            # Filter out known non-content links like WhatsApp's internal learn more 
            if "whatsapp.com" not in link:
                other_links.append(link)

    # Render Twitter links as embeds
    for link in twitter_links:
        md_content.append(f'<blockquote class="twitter-tweet"><a href="{link}"></a></blockquote>')

    md_content.append("\n---\n## Other Links")
    
    # Render other links as a clean list
    for link in other_links:
        md_content.append(f"* [{link}]({link})")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print(f"Site updated with {len(unique_links)} total links.")

if __name__ == "__main__":
    generate_site()
