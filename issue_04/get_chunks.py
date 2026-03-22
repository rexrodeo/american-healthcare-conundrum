# get_chunks.py — run as: python3 /sessions/trusting-festive-planck/mnt/healthcare/issue_04/get_chunks.py
import json, re

try:
    import markdown
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'markdown', '--break-system-packages', '-q'])
    import markdown

with open('/sessions/trusting-festive-planck/mnt/healthcare/issue_04/newsletter_issue_04.md', 'r') as f:
    raw = f.read()

lines = raw.split('\n')
body_lines = [l for l in lines if not l.startswith('# The American Healthcare Conundrum')
                                and not l.startswith('### Issue #')]
body = '\n'.join(body_lines)

# Convert chart placeholders to blockquote image markers
body = re.sub(r'\*\[Chart (\d+)[^:]*: ([^\]]+)\]\*', r'> 📷 *Insert image here: Chart \1 — \2*', body)
body = re.sub(r'\*\[Chart (\d+)[^\]]*\]\*', r'> 📷 *Insert image here: Chart \1*', body)

html = markdown.markdown(body, extensions=['fenced_code', 'tables'])

chunk_size = 4000
chunks = [html[i:i+chunk_size] for i in range(0, len(html), chunk_size)]
print(f'HTML length: {len(html)}, Total chunks: {len(chunks)}')

# Print JS for each chunk
for i, chunk in enumerate(chunks):
    encoded = json.dumps(chunk)
    op = '=' if i == 0 else '+='
    js = f'window.__html4 {op} {encoded}; "chunk {i} done: " + window.__html4.length;'
    print(f'\n=== CHUNK {i} ({len(chunk)} chars raw) ===')
    print(js)
