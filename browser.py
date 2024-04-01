import socket
import ssl

class URL:
  def __init__(self, url):
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https"]
    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443
    if "/" not in url:
      url += "/"
    self.host, url = url.split("/", 1)
    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)
    self.path = "/" + url
  def request(self):
    s = socket.socket(
      family=socket.AF_INET,
      type=socket.SOCK_STREAM,
      proto=socket.IPPROTO_TCP
    )
    if self.scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname=self.host)
    s.connect((self.host, self.port))
    s.send(("GET {} HTTP/1.0\r\n".format(self.path) + \
      "Host: {}\r\n\r\n".format(self.host)) \
      .encode("utf8"))
    response = s.makefile("r", encoding="utf8", newline="\r\n")
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    response_headers = {}
    while True:
        line = response.readline()
        if line == "\r\n": break
        header, value = line.split(":", 1)
        response_headers[header.casefold()] = value.strip()
    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers 

    body = response.read()
    s.close()
    return body

def show(body):
    in_tag = False
    for c in body:
      if c == "<":
          in_tag = True
      elif c == ">":
          in_tag = False
      elif not in_tag:
          print(c, end="")
  

import tkinter
WIDTH, HEIGHT = 800, 600
class Browser:
  def __init__(self):
    self.window = tkinter.Tk()
    self.canvas = tkinter.Canvas(
      self.window,
      width=WIDTH,
      height=HEIGHT
    )
    self.canvas.pack()

  def load(self, url):
    body = url.request()
    show(body)
    self.canvas.create_rectangle(10, 20, 400, 300)
    self.canvas.create_oval(100, 100, 150, 150)
    self.canvas.create_text(200, 150, text="Hi!")


if __name__ == "__main__":
  import sys
  Browser().load(URL(sys.argv[1]))
  tkinter.mainloop()
