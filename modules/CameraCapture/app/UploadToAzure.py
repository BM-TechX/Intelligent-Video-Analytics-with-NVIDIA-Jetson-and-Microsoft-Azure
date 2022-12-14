# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from azure.core.credentials import AzureNamedKeyCredential
from azure.data.tables import TableServiceClient

credential = AzureNamedKeyCredential("my_account_name", "my_access_key")

service = TableServiceClient(endpoint="https://<my_account_name>.table.core.windows.net", credential=credential)
import cv2, queue, threading, time
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955

# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread

import threading


# bufferless VideoCapture
class UploadToAzure:
    def __init__(connectionstring, containername, blobname):
        self.connectionstring = connectionstring
        self.containername = containername
        self.blobname = blobname
        self.service = None
    def connectToAzure(self):
        # Create the BlockBlobService that is used to call the Blob service for the storage account
        self.service = TableServiceClient(endpoint="https://<my_account_name>.table.core.windows.net/", credential=credential)
 