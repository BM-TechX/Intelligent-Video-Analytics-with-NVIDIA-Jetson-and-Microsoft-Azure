# Base on work from https://github.com/Bronkoknorb/PyImageStream
#import trollius as asyncio
import asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import base64
import os


class ImageStreamHandler(tornado.websocket.WebSocketHandler):

    def initialize(self, camera):
        self.clients = []
        self.camera = camera
        self.counter=0
        self.maxcounter=10
    def check_origin(self, origin):
        return True

    def open(self):
        self.clients.append(self)
        print("Image Server Connection::opened")
    def on_data(self, data):
        self.write_message(data, binary=True)
    def on_message(self, msg):
        if msg == 'next':
            frame = self.camera.get_display_frame()
            if frame != None:
                #entity = {'frame': frame, 'message': str(message)}
                #entity = tornado.escape.json_encode(entity)
                encoded = base64.b64encode(frame)
                
                self.write_message(encoded, binary=False)
                self.write_message(self.camera.get_LaneState(), binary=False)
                #self.write_message(''.join(random.choice(letters) for i in range(10)), binary=False)

                #self.write_message(entity, binary=True)
    def data_received(self, dat):
        self.write_message(dat, binary=True)
        
    
    def on_close(self):
        self.clients.remove(self)
        print("Image Server Connection::closed")


class ImageServer(threading.Thread):

    def __init__(self, port, cameraObj):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.camera = cameraObj

    def run(self):
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())

            indexPath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), 'templates')
            app = tornado.web.Application([
                (r"/stream", ImageStreamHandler, {'camera': self.camera}),
                (r"/(.*)", tornado.web.StaticFileHandler,
                 {'path': indexPath, 'default_filename': 'index.html'})
            ])
            app.listen(self.port)
            print('ImageServer::Started.')
            tornado.ioloop.IOLoop.current().start()
        except Exception as e:
            print('ImageServer::exited run loop. Exception - ' + str(e))

    def close(self):
        print('ImageServer::Closed.')