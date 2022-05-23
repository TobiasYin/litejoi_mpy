class CookieItem:
    # same_site could be Strict and Lax
    def __init__(self, key, value, expire=None, max_age=None, domain=None, path=None, secure=False, http_only=False,
                 same_site="Strict"):
        self.key = key
        self.value = value
        self.expire = expire
        self.max_age = max_age
        self.domain = domain
        self.path = path
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    def __str__(self):
        c = "{}={}".format(self.key, self.value)
        # if self.expire is not None:
        #     c += ";Expires={}".format(datetime_to_http_data(self.expire))
        if self.max_age is not None:
            c += ";Max-Age={}".format(self.max_age)
        if self.domain is not None:
            c += ";Domain={}".format(self.domain)
        if self.path is not None:
            c += ";Path={}".format(self.path)
        if self.secure:
            c += ";Secure"
        if self.http_only:
            c += ";HttpOnly"
        if self.same_site is not None:
            c += ";SameSite={}".format(self.same_site)
        return c

