# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 21:22:21 2018

@author: MagicPixel

@email : cyg1030@foxmail.com
"""


from watchdog.events import PatternMatchingEventHandler 

def Create(upload_engine, filetype, remote_root):
    obersever_append = ObserverAppend()
    obersever_append.create(upload_engine, remote_root, filetype)
    return obersever_append

class ObserverAppend(PatternMatchingEventHandler):
    def create(self, upload_engine, remote_root, filetype):
        self.upload_engine = upload_engine
        self.remote_root = remote_root
        self.filetype = filetype


    def on_created(self, event):
		self.process(event)

    def on_modified(self, event):
        self.process(event)


    def process(self, event):
        if not event.is_directory:
            local = event.src_path
            filetype = os.path.splitext(local)[-1]
            if filetype == self.filetype:
                remote = self.remote_root + "/" + os.path.basename(local)
                self.upload_engine.upload_append(local, remote)
