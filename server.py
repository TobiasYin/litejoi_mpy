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


async def handle_request(req, server):
    resp = Response(req)
    if not req:
        resp.error(500)
        return resp

    middlewares = server.middlewares
    func = server.route.match_url(req)

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
                await func(req, resp)

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


class writerWrap:
    def __init__(self, writer):
        self.writer = writer
        self.cpy = False

    async def write(self, data):
        if self.cpy:
            self.writer.write(data)
        else:
            try:
                await self.writer.awrite(data)
            except Exception as e:
                self.cpy = True
                self.writer.write(data)


class ProcessHandler():
    def __init__(self, server):
        self.server = server

    async def process(self, reader, writer):
        request = None
        w = writerWrap(writer)
        try:
            request = Request(reader, w)
            await request.init()
        except Exception as e:
            print("parse request Error, request: {}".format(e))
        try:
            response = await handle_request(request, self.server)
            await response.write_resp()
        except Exception as e:
            print("handler or write error, request: {}".format(e))

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
