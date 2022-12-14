import UploadToAzure
from UploadToAzure import UploadToAzure
import datetime
connectionstring= "DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net"


test = UploadToAzure(connectionstring,"mytable1")
if(test.connectToAzure()):
   
    test.createTable("mytable1")
    test.intiateTable("mytable1")
    
    entity = {
                'PartitionKey': 'pasrt213',
                'RowKey': str(datetime.date),
                'description': 'my description',
                'priority': 200
            }
        
    test.uploadtoTable(entity)
else:
    print("error")