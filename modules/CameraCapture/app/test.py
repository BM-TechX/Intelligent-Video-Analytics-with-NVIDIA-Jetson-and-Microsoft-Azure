import usb.core
import os
# specify the serial ID
serial_id = "M8aS1"

# find all connected devices
devices = usb.core.find(find_all=True)

# find the device with the matching serial ID
device = None
for dev in devices:
    try:
        if dev.serial_number == serial_id:
            device = dev
            break
    except Exception:
        pass

# check if the device was found
if device is None:
    raise ValueError("Device not found")

# get the bus number of the device
bus = device.bus
address = device.address


for i in range(10):
    video_device = "/dev/video%d" % i
    if os.path.exists(video_device):
        try:
            bus_number = int(open("/sys/class/video4linux/video%d/dev" % i).read().strip().split(":")[0], 16)
            if bus_number == bus:
                video_device = "/dev/video%d" % i
                print(video_device)
                break
        except Exception:
            pass

# check if the video device file was found
if not os.path.exists(video_device):
    raise ValueError("Video device not found")
