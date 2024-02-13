# api/generate_puzzle.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from mirrorMazeSolver import generate_puzzle
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # List of allowed origins
        allowed_origins = ['https://portfolio-eric-lin.vercel.app', 'https://portfolio-eric-lin-git-dev-games-chuan-che-lins-projects.vercel.app', 'http://localhost:3000']

        # Get the origin of the incoming request
        origin = self.headers.get('Origin')

        query_components = parse_qs(urlparse(self.path).query)
        height = int(query_components.get('height', [5])[0])
        width = int(query_components.get('width', [5])[0])

        puzzle_data = generate_puzzle(height, width)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')

        # Check if the origin is in our list of allowed origins
        if origin in allowed_origins:
            self.send_header('Access-Control-Allow-Origin', origin)

        self.end_headers()
        self.wfile.write(json.dumps(puzzle_data).encode())
