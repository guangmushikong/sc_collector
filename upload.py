# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 23:11:42 2018

@author: MagicPixel

@email : cyg1030@foxmail.com
"""

import os
import oss2
import sys
import time  
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler 


class UpLoad(PatternMatchingEventHandler):
    def set_params(self, access_key_id, access_key_secret, bucket_name,
                   endpoint, root):
        # 确认上面的参数都填写正确了
        for param in (access_key_id, access_key_secret, bucket_name, endpoint):
            assert '<' not in param, '请设置参数：' + param
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
        self.root = root
      

    def on_created(self, event):
		self.process(event)

    def process(self, event):
        time.sleep(1)
        src = event.src_path
        dst = self.root + "/" + os.path.basename(src)
        self.upload_resumable(src, dst)

    def upload_resumable(self, src, dst):
        print "upload resumable:" + str(src)
        print "to:" + str(dst)
        oss2.resumable_upload(self.bucket, dst, src, multipart_threshold = 100 * 1024)
        time.sleep(1)
        print "upload resumable ok!"
    
    def upload_mutipart(self, src, dst):
        print "upload mutipart"
        total_size = os.path.getsize(src)
        part_size = oss2.determine_part_size(total_size, preferred_size=128 * 1024)

        # 初始化分片上传，得到Upload ID。接下来的接口都要用到这个Upload ID。
        key = dst
        upload_id = self.bucket.init_multipart_upload(key).upload_id

        # 逐个上传分片
        # 其中oss2.SizedFileAdapter()把fileobj转换为一个新的文件对象，新的文件对象可读的长度等于num_to_upload
        with open(filepath, 'rb') as fileobj:
            parts = []
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                result = self.bucket.upload_part(key, upload_id, part_number,
                                    oss2.SizedFileAdapter(fileobj, num_to_upload))
                parts.append(oss2.models.PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1

            # 完成分片上传
            self.bucket.complete_multipart_upload(key, upload_id, parts)
        print "upload mutipart ok!"


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        print "Usage: python upload.py jsonfile srcroot dstroot"
        
    else:
        jsonfile = args[0]
        srcroot = args[1]
        dstroot = args[2]

        import json
        if os.path.exists(jsonfile):
            params = json.load(file(jsonfile))["caiyuangang"][0]["parameter"]
            access_key_id = params["accessKeyId"]
            access_key_secret = params["accessKeySecret"]
            bucket_name = params["bucket"]
            endpoint = params["connection"][0]["endpoint"]
            print access_key_id, access_key_secret, bucket_name, endpoint, srcroot
            observer = Observer()
            upload = UpLoad()
            upload.set_params(access_key_id, access_key_secret, bucket_name, 
                              endpoint, dstroot)

            observer.schedule(upload, path = srcroot)
            
            observer.start()
            observer.join()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()