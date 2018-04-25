# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 21:22:21 2018

@author: MagicPixel

@email : cyg1030@foxmail.com
"""

import os
import sys
from upload import UpLoadEngine
from watchdog.observers import Observer  

def LoadObservers():
	import re
	ObersverDrivers = {}
	#get all the py file
	files = os.listdir(os.getcwd())

	for filei in files:
		match =  re.match(re.compile('observer_(.*?).py'), filei)
		if match is not None:
			driver_name = "observer_" + match.group(1)
			driver_module = __import__(driver_name)
			ObersverDrivers[match.group(1)] = driver_module

	return ObersverDrivers

obersver_files = [
    {
        "driver": "create",
        "root": "Camera",
        "filetype" : ".jpg"
    },
    {
        "driver": "append",
        "root": "POS",
        "filetype" : ".txt"
    }
]

if __name__ == '__main__':

    args = sys.argv[1:]
    if len(args) < 2:
        print "Usage: python main.py jsonfile local_root"
        
    else:
        ObersverDrivers =  LoadObservers()
        print ObersverDrivers
        jsonfile = args[0]
        local_root = args[1]
        remote_root = args[2]

        import json
        if os.path.exists(jsonfile):
            Buckets = json.load(file(jsonfile))["caiyuangang"]
            
            observers = []
            for bucket in Buckets :
                access_key_id = bucket["parameter"]["accessKeyId"]
                access_key_secret = bucket["parameter"]["accessKeySecret"]
                bucket_name = bucket["parameter"]["bucket"]
                endpoint = bucket["parameter"]["connection"][0]["endpoint"]
                upload = UpLoadEngine(access_key_id, access_key_secret, bucket_name, endpoint)
                for obersver_file in obersver_files:
                    driver_name = obersver_file["driver"]
                    root = obersver_file["root"]
                    filetype = obersver_file["filetype"]
                    print (driver_name, root, filetype)
                    observer = ObersverDrivers[driver_name].Create(upload, remote_root + "/" + root, filetype)
                    _observer = Observer()
                    _observer.schedule(observer, path = local_root + "/" + root)
                    observers.append(_observer)
 
            for observer in observers:    
                observer.start()
                observer.join()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()