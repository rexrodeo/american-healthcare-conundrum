#!/usr/bin/env python3
"""Save each chunk's JS to a separate file for injection"""
import json, markdown, re, os

with open('/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/newsletter_issue_04.md', 'r') as f:
    raw = f.read()

lines = raw.split('\n')
body_lines = [l for l in lines if not l.startswith('# The American Healthcare Conundrum')
                                and not l.startswith('### Issue #')]
body = '\n'.join(body_lines)

body = re.sub(r'\*\[Chart (\d+)[^:]*: ([^\]]+)\]\*', r'> 📷 *Insert image here: Chart \1 — \2*', body)
body = re.sub(r'\*\[Chart (\d+)[^\]]*\]\*', r'> 📷 *Insert image here: Chart \1*', body)

html = markdown.markdown(body, extensions=['fenced_code', 'tables'])

chunk_size = 4000
chunks = [html[i:i+chunk_size] for i in range(0, len(html), chunk_size)]
print(f'HTML length: {len(html)}, Total chunks: {len(chunks)}')

outdir = '/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/chunks'
os.makedirs(outdir, exist_ok=True)

for i, chunk in enumerate(chunks):
    encoded = json.dumps(chunk)
    op = '=' if i == 0 else '+='
    js = f'window.__html4 {op} {encoded}; "chunk {i} done: " + window.__html4.length;'
    with open(f'{outdir}/chunk_{i:02d}.js', 'w') as f:
        f.write(js)
    print(f'Chunk {i}: {len(chunk)} chars raw, saved to chunk_{i:02d}.js')

print(f'\nAll {len(chunks)} chunks saved to {outdir}/')
