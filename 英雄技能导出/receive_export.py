from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(r"C:\Users\admin\Documents\ChatGPT\安装\英雄技能导出\英雄技能_原始关联.json")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        OUT.write_bytes(self.rfile.read(length))
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def log_message(self, *args):
        pass


HTTPServer(("127.0.0.1", 8788), Handler).handle_request()
