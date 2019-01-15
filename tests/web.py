import logging

from tornado.ioloop import IOLoop
from tornado.gen import coroutine
from tornado.web import RequestHandler, Application

from realtimefunc import realtimefunc

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(module)s %(lineno)d %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger("game")


@coroutine
@realtimefunc
def test():
    print("test")
    print("I can change")
    return 1/0


class Say(RequestHandler):
    @coroutine
    @realtimefunc
    def get(self):
        global counter
        yield test()
        logger.info("log somethings")
        self.write("200 OK")


class MainHandler(RequestHandler):
    def get(self):
        self.write("200 OK")


def make_app():
    return Application([
        (r"/", MainHandler),
        (r"/say", Say),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
