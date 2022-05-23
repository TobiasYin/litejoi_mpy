import json

from utils import parse_url, parse_query

class Request:
    def __init__(self, message):
        m = message.split("\r\n\r\n", 1)
        header, body = "", ""
        if len(m) == 1:
            m = m.split("\n\n", 1)
            header = m[0]
            if len(m) > 1:
                body = m[1]
        elif len(m) >= 2:
            header = m[0]
            body = m[1]
        body = body.strip()
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
        self.params = parse_query(self.url.query)
        self.body = body
        self.url_params = {}
        cookies = self.headers.get("Cookie")
        self.cookies = {}
        if cookies:
            self.cookies = {i[0]: i[1] for i in
                            map(lambda x: list(map(lambda y: y.strip(), x.split("=", 1))), cookies.split(";"))}

        # body for html form
        self.content_type = self.headers.get("Content-Type")
        self.post_params = self.get_post_params(self.content_type, self.body)

    @staticmethod
    def get_post_params(content_type, body):
        if content_type == "application/json":
            return json.loads(body)
        elif content_type == "application/x-www-form-urlencoded":
            return {i[0]: i[1] for i in parse_query(body)}
        return {}