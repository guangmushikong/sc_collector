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

from watchdog.events import PatternMatchingEventHandler 


class UpLoadEngine():
    def __init__(self, access_key_id, access_key_secret, bucket_name,
                   endpoint):
        # 确认上面的参数都填写正确了
        for param in (access_key_id, access_key_secret, bucket_name, endpoint):
            assert '<' not in param, '请设置参数：' + param
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
      
    def upload_resumable(self, local, remote):
        oss2.resumable_upload(self.bucket, remote, local, multipart_threshold = 100 * 1024)
        time.sleep(1)
    
    def upload_append(self, local, remote):
        with open(local, 'rb') as f:
            data_end = os.path.getsize(local) 
            data_start = 0
            exist = self.bucket.object_exists(remote)

            if exist:
                print('object exist ')
                result = self.bucket.head_object(remote)
                data_start = result.content_length

            print(data_start, data_end)   
            result = self.bucket.append_object(remote,  data_start,  f.read(data_end - data_start) )
        f.close()
            

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

