# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 21:22:21 2018

@author: MagicPixel

@email : cyg1030@foxmail.com
"""

import os
from watchdog.events import PatternMatchingEventHandler 

def Create(upload_engine, remote_root, filetype):
    obersever_create = ObserverCreate()
    obersever_create.create(upload_engine, remote_root, filetype)
    return obersever_create

class ObserverCreate(PatternMatchingEventHandler):
    def create(self, upload_engine, remote_root, filetype):
        self.upload_engine = upload_engine
        self.remote_root = remote_root
        self.filetype = filetype

    def on_created(self, event):
        print event.src_path
        self.process(event)

    def process(self, event):
        if not event.is_directory:
            local = event.src_path
            filetype = os.path.splitext(local)[-1]
            print filetype
            if filetype == self.filetype:
                remote = self.remote_root + "/" + os.path.basename(local)
                print remote
                try:
                    self.upload_engine.upload_resumable(local, remote)
                except:
                    return
