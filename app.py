import http.server
import socketserver
import json
import urllib.parse
import os
import sys


from db import (
    init_db,
    save_transcription,
    get_dates_summary,
    get_transcriptions_by_date,
    get_recent_transcriptions,
    get_transcription_by_id,
    get_setting,
    set_setting,
    is_content_duplicate
)
import gemini_client

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

class HandwritingAppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status_code, data):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_error(self, status_code, message):
        self._send_json(status_code, {"error": message})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API Endpoints
        if path == "/api/dates":
            dates = get_dates_summary()
            return self._send_json(200, {"dates": dates})

        elif path == "/api/records":
            date_param = query.get("date", [None])[0]
            if date_param:
                records = get_transcriptions_by_date(date_param)
            else:
                records = get_recent_transcriptions(limit=30)
            return self._send_json(200, {"records": records})

        elif path.startswith("/api/records/"):
            rec_id_str = path.split("/api/records/")[1]
            try:
                rec_id = int(rec_id_str)
                record = get_transcription_by_id(rec_id)
                if record:
                    return self._send_json(200, {"record": record})
                else:
                    return self._send_error(404, "기록을 찾을 수 없습니다.")
            except ValueError:
                return self._send_error(400, "잘못된 ID 형식입니다.")

        elif path == "/api/settings":
            key = gemini_client.get_gemini_api_key()
            model = gemini_client.get_preferred_model()
            is_set = bool(key and len(key) > 5)
            masked = (key[:6] + "..." + key[-4:]) if is_set else ""
            return self._send_json(200, {
                "has_api_key": is_set,
                "masked_key": masked,
                "api_key": key if is_set else "",
                "preferred_model": model
            })

        # Static files fallback
        if path == "/" or path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/save":
            item = payload
            saved = save_transcription(
                title=item.get("title", "무제"),
                author=item.get("author", "작자 미상"),
                category=item.get("category", "문학"),
                content=item.get("content", "")
            )
            if not saved:
                recs = get_recent_transcriptions(limit=1)
                if recs:
                    saved = get_transcription_by_id(recs[0]["id"])
            if saved:
                saved["meta_message"] = item.get("meta_message", "")
                saved["source"] = item.get("source", "")
                return self._send_json(201, {"record": saved})
            else:
                return self._send_error(500, "저장에 실패했습니다.")

        elif path == "/api/generate":
            preferred_cat = payload.get("category")
            preferred_model = payload.get("model")

            item = gemini_client.generate_handwriting_text(
                preferred_category=preferred_cat,
                preferred_model=preferred_model
            )

            if not item or not item.get("content"):
                return self._send_error(500, "필사 글 생성 중 일시적인 문제가 발생했습니다.")

            saved = save_transcription(
                title=item["title"],
                author=item.get("author", "작자 미상"),
                category=item.get("category", "문학"),
                content=item["content"]
            )

            if saved:
                saved["meta_message"] = item.get("message", "")
                saved["source"] = item.get("source", "")
                return self._send_json(201, {"record": saved})
            else:
                return self._send_error(500, "필사 글 생성 중 일시적인 문제가 발생했습니다.")

        elif path == "/api/settings":
            new_key = payload.get("api_key", "").strip()
            new_model = payload.get("model", "").strip()
            if new_key:
                set_setting("gemini_api_key", new_key)
            if new_model:
                set_setting("gemini_model", new_model)
            return self._send_json(200, {"success": True, "message": "설정이 안전하게 저장되었습니다."})

        return self._send_error(404, "엔드포인트를 찾을 수 없습니다.")

def run_server(port=PORT):
    init_db()
    gemini_client.trigger_background_prefetch()
    server_address = ("", port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, HandwritingAppHandler) as httpd:
        print(f"==================================================")
        print(f" 필사 생성 & 보관 앱 서버 시작: http://localhost:{port}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")
            httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
