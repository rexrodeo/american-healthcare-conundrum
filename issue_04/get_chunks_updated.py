#!/usr/bin/env python3
"""
get_chunks_updated.py — Generate chunked HTML payload for Issue #4 Substack injection
Run as: python3 /sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/get_chunks_updated.py
"""
import json, markdown, re

with open('/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/newsletter_issue_04.md', 'r') as f:
    raw = f.read()

# Strip the H1 title and H3 issue line (Substack owns those fields)
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
