try:
    import uasyncio as asyncio
except ImportError:
    # To test in cpython
    import asyncio

from .request import Request
from .response import Response
from . import router

class MiddleWare:
    def pre_request(self, req: Request, resp: Response):
        return True

    def post_request(self, req: Request, resp: Response):
        return True


def handle_request(req, server):
    func = server.route.match_url(req)
    resp = Response(req)

    middlewares = server.middlewares

    if func is None:
        print("Func not implament")
    else:
        try:
            break_pos = -1

            for (index, item) in enumerate(middlewares):
                res = item.pre_request(req, resp)
                if not res:
                    break_pos = index
                    break

            if break_pos < 0:
                func(req, resp)

            for item in middlewares[break_pos::-1]:
                res = item.post_request(req, resp)
                if res:
                    break

        except Exception as e:
            print("Handle request Error, request: {}, {}".format(req, e))
            resp.error(500)
    print("Request [{}], Method: {}, resp status: {}".format(
        req.raw_url, req.method, resp.status))
    return resp


class ProcessHandler():
    def __init__(self, server):
        self.server = server

    async def process(self, reader, writer):
        print("Start process request!")
        message = await reader.read(1024)  # max request size 1KB
        message = message.decode('utf-8')

        if len(message) > 1:
            request = Request(message)

            response = handle_request(request, self.server)
            resp = response.encode()
            try:
                await writer.awrite(resp)
            except Exception:
                # use in cpython
                writer.write(resp)

        writer.close()
        await writer.wait_closed()


class Server():
    def __init__(self, port=8080, addr="0.0.0.0", route=router.root):
        self.route = route
        self.port = port
        self.addr = addr
        self.middlewares = []
        self.socket_server = None

    def add_middleware(self, mw: MiddleWare):
        self.middlewares.append(mw)

    async def arun(self):
        print("start run server... port: {}".format(self.port))
        handler = ProcessHandler(self)
        s = await asyncio.start_server(handler.process, self.addr, self.port)
        self.socket_server = s

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.arun())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("closing")
            self.close()
            loop.close()

    def close(self):
        self.socket_server.close()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.socket_server.wait_closed())


if __name__ == "__main__":
    s = Server()
    s.run()
