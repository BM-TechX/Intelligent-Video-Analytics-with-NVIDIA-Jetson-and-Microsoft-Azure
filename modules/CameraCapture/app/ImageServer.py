# Base on work from https://github.com/Bronkoknorb/PyImageStream
#import trollius as asyncio
import asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import base64
import os
import json


class ImageStreamHandler(tornado.websocket.WebSocketHandler):
    def editconfig(self,msg):
        try:
            with open('config.json') as json_file:
                data = json.load(json_file)
                if (msg.split(",")[0]=="activeLanes"):
                    
                    activelanes=  data['activeLanes'].split(",")
                    activeLanesar=[int(activelanes[0]),int(activelanes[1]),int(activelanes[2]),int(activelanes[3])]
                    activeLanesar[int(msg.split(",")[1])]=int(msg.split(",")[2])
                    data['activeLanes']=str(activeLanesar[0])+","+str(activeLanesar[1])+","+str(activeLanesar[2])+","+str(activeLanesar[3])
                if(msg.split(",")[0]=="activeUSB"):
                    activeUSB=  data['activeUSB'].split(",")
                    activeUSBar=[int(activeUSB[0]),int(activeUSB[1]),int(activeUSB[2]),int(activeUSB[3])]
                    activeUSBar[int(msg.split(",")[1])]=int(msg.split(",")[2])
                    data['activeUSB']=str(activeUSBar[0])+","+str(activeUSBar[1])+","+str(activeUSBar[2])+","+str(activeUSBar[3])
                    print(data['activeUSB'])
            with open('config.json', "w") as outfile:
                json.dump(data,outfile,indent=4)
        except Exception as e:
            print("Error in editconfig: ",e)
                   
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
        if 'activeLanes' in msg:
            self.editconfig(msg)
        if 'activeUSB' in msg:
            self.editconfig(msg)
                            
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