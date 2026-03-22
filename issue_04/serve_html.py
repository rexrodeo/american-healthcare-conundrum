#!/usr/bin/env python3
"""Simple HTTP server to serve the HTML payload for Substack injection"""
import http.server, json, markdown, re, threading

with open('/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/newsletter_issue_04.md', 'r') as f:
    raw = f.read()

lines = raw.split('\n')
body_lines = [l for l in lines if not l.startswith('# The American Healthcare Conundrum')
                                and not l.startswith('### Issue #')]
body = '\n'.join(body_lines)

body = re.sub(r'\*\[Chart (\d+)[^:]*: ([^\]]+)\]\*', r'> 📷 *Insert image here: Chart \1 — \2*', body)
body = re.sub(r'\*\[Chart (\d+)[^\]]*\]\*', r'> 📷 *Insert image here: Chart \1*', body)

html = markdown.markdown(body, extensions=['fenced_code', 'tables'])

# Save the HTML for serving
with open('/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/payload.html', 'w') as f:
    f.write(html)

print(f'HTML length: {len(html)} chars')
print(f'Saved to payload.html')
print(f'Starting server on port 8765...')

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    def log_message(self, format, *args):
        print(f'Request served: {args[0]}')

server = http.server.HTTPServer(('0.0.0.0', 8765), Handler)
print('Server running at http://localhost:8765')
server.serve_forever()
