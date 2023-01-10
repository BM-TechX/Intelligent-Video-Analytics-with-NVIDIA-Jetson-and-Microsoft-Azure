import json

def read_json():
    ROI1 = None
    ROI2 = None
    ROI3 = None
    ROI4 = None
    genral_rotation=None
    roi1_rotation=None
    roi2_rotation=None
    roi3_rotation=None
    roi4_rotation=None
    roi1a=None
    roi2a=None
    roi3a=None
    roi4a=None
    try:
        print("Reading config file")
        with open('config.json') as json_file:
            data = json.load(json_file)
            ROI1 = data['roi1']
            ROI2 = data['roi2']
            ROI3 = data['roi3']
            ROI4 = data['roi4']
            genral_rotation=data['genral_rotation']
            roi1_rotation=data['roi1_rotation']
            roi2_rotation=data['roi2_rotation']
            roi3_rotation=data['roi3_rotation']
            roi4_rotation=data['roi4_rotation']
            roi1a=data['roi1a']
            roi2a=data['roi2a']
            roi3a=data['roi3a']
            roi4a=data['roi4a']
    except Exception as e:
        print("Error reading config file " + str(e))
    return ROI1, ROI2, ROI3, ROI4, genral_rotation, roi1_rotation, roi2_rotation, roi3_rotation, roi4_rotation, roi1a, roi2a, roi3a, roi4a

ROI1, ROI2, ROI3, ROI4, genral_rotation, roi1_rotation, roi2_rotation, roi3_rotation, roi4_rotation, roi1a, roi2a, roi3a, roi4a = read_json()

def convertROIstringToTuple(roiString):
    roi = roiString[0].split(',')
    return (int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3]))
def convertROIstringToTuple2(roi):
    roi = roi.split(',')
    return (int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3]))

print("general_rotation",genral_rotation)
print("roi1_rotation",roi1_rotation)

genral_rotation = float(genral_rotation)
roi1_rotation=float(roi1_rotation)
roi2_rotation=float(roi2_rotation)
roi3_rotation=float(roi3_rotation)
roi4_rotation=float(roi4_rotation)
print ("roi1a",roi1a)
print("roi2a",roi2a)
print("roi3a",roi3a)
print("roi4a",roi4a)
roi1a =convertROIstringToTuple(roi1a)
roi2a =convertROIstringToTuple2(roi2a) 
roi3a =convertROIstringToTuple2(roi3a)
roi4a =convertROIstringToTuple2(roi4a)