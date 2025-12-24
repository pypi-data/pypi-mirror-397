from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Template

from trame import Trame


PORT = 8021


def main(markdown_file):
    """Start the server with hardcoded configuration"""
    Handler = factory_handler(markdown_file)
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"Server running at http://localhost:{PORT}")
    print(f"Serving file: {markdown_file}")
    server.serve_forever()


def factory_handler(markdown_path):
    """Factory function to create handler with markdown_path in closure"""
    markdown_dir = Path(markdown_path).parent

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Serve image files
            if self.path.endswith((".jpg", ".jpeg", ".png", ".gif", ".svg")):
                file_path = markdown_dir / self.path.lstrip("/")
                if file_path.exists():
                    self.send_response(200)
                    self.send_header("Content-type", self._get_content_type(self.path))
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        self.wfile.write(f.read())
                    return

            # Serve HTML
            trame = Trame.from_file(markdown_path)
            template = factory_template()
            html = template.render(trame=trame)

            # print(html)  # XXX Uncomment to debug

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def _get_content_type(self, path):
            if path.endswith(".jpg") or path.endswith(".jpeg"):
                return "image/jpeg"
            elif path.endswith(".png"):
                return "image/png"
            elif path.endswith(".gif"):
                return "image/gif"
            elif path.endswith(".svg"):
                return "image/svg+xml"
            return "application/octet-stream"

    return RequestHandler


def factory_template():
    """Create Jinja2 template with basic styling"""
    template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Trame Viewer</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            background-color: #F0EEF7;
            padding: 10px;
        }

    </style>
</head>
<body>
    <h1>{{ trame.path }}</h1>
    <hr>
    
    {% for piece in trame.pieces %}
    <div class="piece">
    
        {{ piece.html | safe }}
    </div>
    {% endfor %}
</body>
</html>
"""
    return Template(template_str)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("markdown_file")
    args = parser.parse_args()

    main(args.markdown_file)
