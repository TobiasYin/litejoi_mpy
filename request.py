import json

from .utils import parse_url, parse_query

class Request:
    async def read(self):
        self.reader.read()

    async def read_into(self, size):
        self.buffer += await self.reader.read(size)

    async def read_all(self, size):
        last_size = len(self.buffer)
        while True:
            self.read_into(100)
            size = len(self.buffer)
            if last_size == size:
                data = self.buffer
                self.buffer = b""
                return data

    async def read_until(self, sep):
        part_size = len(sep)
        if part_size < 100:
            part_size = 100
        if len(self.buffer) > part_size:
            r = self._find_sep(sep)
            if r:
                return r
        last_size = len(self.buffer)
        while True:
            await self.read_into(part_size)
            size = len(self.buffer)
            if last_size == size:
                return None
            r = self._find_sep(sep)
            if r:
                return r
     
    async def write_body(self, target):
        with open(target, 'wb') as f:
            await self.read_into(100)
            while self.buffer:
                f.write(self.buffer)
                self.buffer = b""
                self.read_into(100)
    
            


    def _find_sep(self, sep):
        f = self.buffer.find(sep)
        if f == -1:
            return None
        target = self.buffer[:f]
        self.buffer = self.buffer[f + len(sep):]
        return target
                
    def __init__(self, reader):
        self.reader = reader

    async def init(self):
        self.buffer = b""
        header = await self.read_until(b"\r\n\r\n")
        header = header.decode('utf-8')
        lines = header.split("\n")
        headers = {i[0]: i[1] for i in map(
            lambda x: [i.strip() for i in x.split(":", 1)], lines[1:])}
        method, url, http_version = lines[0].split()
        self.http_version = http_version
        self.headers = headers
        self.method = method.upper()
        self.raw_url = url
        self.url = parse_url(url)
        self.path = self.url.path
        self.query_params = parse_query(self.url.query)
        self.url_params = {}
        cookies = self.headers.get("Cookie")
        self.cookies = {}
        if cookies:
            self.cookies = {i[0]: i[1] for i in
                            map(lambda x: list(map(lambda y: y.strip(), x.split("=", 1))), cookies.split(";"))}

        # body for html form
        self.content_type = self.headers.get("Content-Type")
        self.post_params = self.get_post_params(self.content_type)

        self.params = {}
        self.params.update(self.query_params)
        self.params.update(self.post_params)
        self.params.update(self.url_params)

    def load_body(self):
        return self.read_all()
    def get_post_params(self, content_type):
        if content_type == "application/json":
            body = self.load_body()
            return json.loads(body)
        elif content_type == "application/x-www-form-urlencoded":
            body = self.load_body() 
            return {i[0]: i[1] for i in parse_query(body)}
        return {}