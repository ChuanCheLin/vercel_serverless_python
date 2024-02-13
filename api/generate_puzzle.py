# api/generate_puzzle.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from mirrorMazeSolver import generate_puzzle
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        height = int(query_components.get('height', [5])[0])
        width = int(query_components.get('width', [5])[0])

        puzzle_data = generate_puzzle(height, width)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(puzzle_data).encode())
