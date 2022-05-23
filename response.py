from .cookie import CookieItem
import json
from .utils import get_content_type

class Response:
    def __init__(self, request):
        self.request = request
        self.status = -1
        self.headers = {}
        self.body = ""
        self.http_version = "HTTP/1.1"
        self.add_defult_headers()
        self.cookies = {}

    def add_defult_headers(self):
        self.headers["content-language"] = "en"
        # self.headers["date"] = datetime_to_http_data(datetime.datetime.now())

    def json(self, d, status=200):
        self.body = json.dumps(d)
        self.headers["Content-Type"] = "application/json;charset=UTF-8"
        self.status = status

    def html(self, t, status=200):
        self.body = t
        self.status = status
        self.headers["Content-Type"] = "text/html;charset=UTF-8"

    def static(self, path, status=200):
        self.status = status
        with open(path, "rb") as f:
            self.body = f.read()
        self.headers["Content-Type"] = get_content_type(path)

    def error(self, status, message=""):
        status_info = STATUS.get(str(status), "NOT DEFINE")
        self.html(
            "<h1>{} {}</h1><h2>{}</h2>".format(
                status, status_info, "" if not message else "error message:" + message),
            status)

    def basic_auth(self, title):
        self.headers["WWW-Authenticate"] = "Basic realm=\"{}\"".format(title)
        self.status = 401

    def redirect(self, url):
        self.status = 302
        self.headers["Location"] = url

    def add_cookie(self, cookie):
        self.cookies[cookie.key] = cookie

    def remove_cookie(self, key):
        self.add_cookie(CookieItem(key, "", max_age=0))

    def encode(self):
        status = self.status
        if status == -1:
            status = 202
        status_info = STATUS.get(str(status), "NOT DEFINE")
        encode_body = self.body
        if type(encode_body) == str:
            encode_body = encode_body.encode()
        bodylen = len(encode_body)
        self.headers["Content-Length"] = bodylen
        header_str = "{} {} {}".format(self.http_version, status, status_info) + '\r\n' + "\r\n".join(
            ["{}:{}".format(i, self.headers[i]) for i in self.headers])
        for k in self.cookies:
            header_str += "\r\nSet-Cookie:{}".format(str(self.cookies[k]))
        return (header_str + "\r\n\r\n").encode() + encode_body + b"\r\n"

STATUS = {'100': 'Continue',
              '101': 'Switching Protocol',
              '102': 'Processing',
              '103': 'Early Hints',
              '200': 'OK',
              '201': 'Created',
              '202': 'Accepted',
              '203': 'Non-Authoritative Information',
              '204': 'No Content',
              '205': 'Reset Content',
              '206': 'Partial Content',
              '207': 'Multi-Status',
              '208': 'Already Reported',
              '226': 'IM Used',
              '300': 'Multiple Choice',
              '301': 'Moved Permanently',
              '302': 'Found',
              '303': 'See Other',
              '304': 'Not Modified',
              '307': 'Temporary Redirect',
              '308': 'Permanent Redirect',
              '400': 'Bad Request',
              '401': 'Unauthorized',
              '403': 'Forbidden',
              '404': 'Not Found',
              '405': 'Method Not Allowed',
              '406': 'Not Acceptable',
              '407': 'Proxy Authentication Required',
              '408': 'Request Timeout',
              '409': 'Conflict',
              '410': 'Gone',
              '411': 'Length Required',
              '412': 'Precondition Failed',
              '413': 'Payload Too Large',
              '414': 'URI Too Long',
              '415': 'Unsupported Media Type',
              '416': 'Range Not Satisfiable',
              '417': 'Expectation Failed',
              '418': "I'm a teapot",
              '421': 'Misdirected Request',
              '422': 'Unprocessable Entity',
              '423': 'Locked',
              '424': 'Failed Dependency',
              '425': 'Too Early',
              '426': 'Upgrade Required',
              '428': 'Precondition Required',
              '429': 'Too Many Requests',
              '431': 'Request Header Fields Too Large',
              '451': 'Unavailable For Legal Reasons',
              '500': 'Internal Server Error',
              '501': 'Not Implemented',
              '502': 'Bad Gateway',
              '503': 'Service Unavailable',
              '504': 'Gateway Timeout',
              '505': 'HTTP Version Not Supported',
              '506': 'Variant Also Negotiates',
              '507': 'Insufficient Storage',
              '508': 'Loop Detected',
              '510': 'Not Extended',
              '511': 'Network Authentication Required'}