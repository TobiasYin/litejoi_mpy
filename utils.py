class UrlType:
    def __init__(self, path, query):
        self.path = path
        self.query = query

def not_found(req, resp):
    resp.html(
        "<html><h1>404 Not Found</h1><h2>Sorry, The page request is Not Found.</h2></html>", 404)

def parse_url(url):
    u = url.split("?")
    p = u[0]
    q = ""
    if len(u) > 1:
        q = u[1]
    return UrlType(p, q)

def parse_query(q):
    items = q.split("&")
    querys = {}
    for i in items:
        if not i:
            continue
        p = i.split("=", 1)
        k = p[0]
        v = ""
        if len(p) > 1:
            v = p[1]
        querys[k] = v

    return querys

def get_content_type(path):
    if path.endswith(".html"):
        return "text/html;charset=UTF-8"
    elif path.endswith(".js"):
        return "application/javascript;charset=UTF-8"
    elif path.endswith(".css"):
        return "text/css;charset=UTF-8"
    elif path.endswith(".jpg"):
        return "image/jpeg"
    elif path.endswith(".png"):
        return "image/png"
    elif path.endswith(".gif"):
        return "image/gif"
    else:
        return "text/plain;charset=UTF-8"