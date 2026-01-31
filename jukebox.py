# -*- coding: utf-8 -*-
import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
import threading

MUSIC_DIR = r"C:\hudba"
PORT = 8080

class JukeboxHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_songs.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            songs = []
            music_path = Path(MUSIC_DIR)
            
            if music_path.exists():
                for mp3_file in music_path.rglob('*.mp3'):
                    try:
                        relative_path = mp3_file.relative_to(music_path)
                        parts = relative_path.parts
                        
                        artist = parts[0] if len(parts) > 0 else 'Neznámý interpret'
                        album = parts[1] if len(parts) > 1 else 'Neznámé album'
                        filename = mp3_file.stem
                        
                        # Odstranění čísla tracku
                        import re
                        title = re.sub(r'^\d+\s*-\s*', '', filename)
                        
                        songs.append({
                            'title': title,
                            'artist': artist,
                            'album': album,
                            'file': str(relative_path).replace('\\', '/')
                        })
                    except Exception as e:
                        print(f"Chyba při zpracování {mp3_file}: {e}")
            
            # Seřazení podle interpreta a alba
            songs.sort(key=lambda x: (x['artist'], x['album']))
            
            response = json.dumps(songs, ensure_ascii=False).encode('utf-8')
            self.wfile.write(response)
            
        elif self.path.startswith('/music/'):
            # Přehrávání MP3
            file_path = unquote(self.path[7:])  # Odstranění /music/
            full_path = os.path.join(MUSIC_DIR, file_path)
            
            if os.path.exists(full_path):
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'Soubor nenalezen')
        else:
            # Hlavní HTML stránka
            if self.path == '/' or self.path == '/index.html':
                self.path = '/jukebox.html'
            super().do_GET()

def start_server():
    server = HTTPServer(('localhost', PORT), JukeboxHandler)
    print(f"✓ Jukebox server běží na http://localhost:{PORT}")
    print(f"✓ Hudební složka: {MUSIC_DIR}")
    print("✓ Otevírám prohlížeč...")
    server.serve_forever()

if __name__ == '__main__':
    # Automatické otevření prohlížeče
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    start_server()
