# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableServiceClient
import cv2, queue, threading, time
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955

# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread

import threading


# bufferless VideoCapture
class UploadToAzure:
    def __init__(self,connectionstring,table):
        self.connectionstring = connectionstring
        self.service = None
        self.client = None
        self.table = table
        
    def connectToAzure(self):
        print("connecting to azure")
        # Create the BlockBlobService that is used to call the Blob service for the storage account
        try:
            self.service = TableServiceClient.from_connection_string(conn_str=self.connectionstring)
            print("connected to azure")
            return True
        except:
            return False
    
    def uploadtoTable(self,entity):
        try:
            self.client.create_entity(entity=entity)
            print ("uploaded to table" + entity.get("PartitionKey") + " " + entity.get("RowKey"))
            return True
        except Exception as e:
            print("error uploading to table " + str(e))
            return False
    def intiateTable(self,table):
        try:
            self.client = self.service.get_table_client(table_name=table)
            return True
        except:
            print("error initiating table")
            return False
    def createTable(self,table):
        try:
            self.client = self.service.create_table(table_name=table)
            return True
        except Exception as e:
            try:
                if (e.ErrorCode == "TableAlreadyExists"):
                    print("table already exists")
                    return True
            except:
                return False
            return False
    def test_con(self):
        try:
            if (self.client is None):
                return False
            return True
        except:
            return False
    def __uploadToAzure(self, counter, frame):
        try:
            print("uploading to azure")
            # blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net")
            # local_file_name = str(counter) +  ".jpg"
            # _, img_encode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 99])            
            # try:
            #     blob_client = blob_service_client.get_blob_client(container=self.AZURE_STORAGE_BLOB[0], blob=local_file_name)
            #     blob_client.upload_blob(img_encode.tobytes(), overwrite=True)
            # except:
            #     print("error")
        except Exception as e:
            print('__uploadToAzure Excpetion -' + str(e))
            return
