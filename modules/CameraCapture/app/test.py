import usb
import cv2

dev = usb.core.find(find_all=True)

# get next item from the generator


def serial_number(us):
        """ Return the USB device's serial number string descriptor.

        This property will cause some USB traffic the first time it is accessed
        and cache the resulting value for future use.
        """
        if us._serial_number is None:
            us._serial_number = usb.util.get_string(us, us.iSerialNumber)
        return us._serial_number
def video_ID(us):
        """ Return the usb video number
        """

for d in dev:
    name= str(serial_number(d))
    if("M8aS2" in name):
        vid = cv2.VideoCapture(d)
        
