#!/usr/bin/env python3
"""Shared KEGG timing tokens only. No source retrieval, filesystem or credentials exposed."""
import argparse,json,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
lock=threading.Lock();last={};intervals={'/kegg':0.4,'/nvd':6.2}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  global last
  if self.path not in intervals: self.send_error(404);return
  with lock:
   delay=max(0,intervals[self.path]-(time.monotonic()-last.get(self.path,0.0)))
   if delay: time.sleep(delay)
   last[self.path]=time.monotonic()
  body=json.dumps({'allowed':True}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18763);a=p.parse_args()
 ThreadingHTTPServer(('0.0.0.0',a.port),Handler).serve_forever()
