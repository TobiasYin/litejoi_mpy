from .utils import not_found

class Router:
    GROUP = 1
    FUNC = 2
    NAMED_LIST = 3
    NAMED_GROUP = 4
    HTTP_METHODS = {"GET", "POST", "HEAD", "PUT",
                    "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"}

    def __init__(self, type=GROUP, param_name="", top=False):
        self.routes = {}
        self.type = type
        self.functions = {}
        self.named_list = []
        self.param_name = param_name
        self.has_not_found = False

    def bind_not_found(self, func=not_found):
        if not self.has_not_found or func != not_found:
            self.add_url("*", not_found, ['*'])
            self.has_not_found = True

    def bind_func(self, methods, func):
        for m in methods:
            m = m.upper()
            if m in self.functions:
                raise IndexError("{} already declare".format(m))
            if m in self.HTTP_METHODS or m == "*":
                self.functions[m] = func

    def match_func(self, method):
        m = method.upper()
        if m in self.functions:
            return self.functions[m]
        if "*" in self.functions:
            return self.functions['*']

    @staticmethod
    def split_path(path):
        if len(path) == 0:
            return "", ""
        start_index = 1 if path[0] == '/' else 0
        slash_index = path.find('/', start_index)
        if slash_index == -1:
            slash_index = len(path)
        f = path[start_index:slash_index]
        s = path[slash_index:]
        return f, s

    def add_url(self, url, func, methods):
        if len(url) == 0 or url == "/": 
            self.routes[""] = Router(self.FUNC)
            self.routes[""].bind_func(methods, func)
            return
        f, s = self.split_path(url)

        if not f.startswith(":"):
            if f not in self.routes:
                self.routes[f] = Router(self.GROUP)

            self.routes[f].add_url(s, func, methods)
            return

        if ":" not in self.routes:
            self.routes[":"] = Router(self.NAMED_LIST)
        r = Router(self.NAMED_GROUP, param_name=f[1:])
        self.routes[":"].named_list.append(r)
        r.add_url(s, func, methods)

    def match_url(self, request):
        path = request.path
        func, params = self.__match_url(path, request.method)
        request.url_params = params
        return func

    def __match_url(self, path, method):
        if self.type == self.FUNC:
            return self.match_func(method), {}
        if self.type == self.NAMED_LIST:
            for i in self.named_list:
                func, params = i.__match_url(path, method)
                if func != None:
                    return func, params
            return None, {}
        f, s = self.split_path(path)
        func, params = None, {}

        if self.type == self.NAMED_GROUP:
            nf, ns = self.split_path(s)
            if nf in self.routes:
                func, params = self.routes[nf].__match_url(ns, method)

        if func is None and f in self.routes:
            func, params = self.routes[f].__match_url(s, method)

        if func is None and ":" in self.routes:
            func, params = self.routes[":"].__match_url(path, method)

        if func is None and "*" in self.routes:
            func, params = self.routes["*"].__match_url(s, method)

        if func is not None and self.type == self.NAMED_GROUP:
            params[self.param_name] = f

        return func, params


root = Router()
root.bind_not_found()

def url(url, methods, router=root):
    if type(methods) is str:
        methods = [methods]

    def decorator(func):
        async def w(req, resp):
            func(req, resp)
        router.add_url(url, w, methods)
        return w

    return decorator

def aurl(url, methods, router=root):
    if type(methods) is str:
        methods = [methods]

    def decorator(func):
        router.add_url(url, func, methods)
        return func

    return decorator