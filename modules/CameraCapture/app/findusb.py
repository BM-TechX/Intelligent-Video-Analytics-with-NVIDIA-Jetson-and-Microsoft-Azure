import subprocess
# To make python 2 and python 3 compatible code
# bufferless VideoCapture
class findUsb:
    def __init__(self):
        output = self.run_v4l2_command("v4l2-ctl --list-devices")
        lines = output.split('\n')
        devices = {}
        for line in lines:
            parts = line.split()
            if "video" in line:
                device_path = line.strip()
                device_info = self.run_v4l2_command(f"v4l2-ctl --device={device_path} --info")
                for info_line in device_info.split('\n'):
                    if 'Serial' in info_line:
                        serial = info_line.split(':')[1].strip()
                        devices[device_path] = serial
                        break
        self.devices = devices
    def run_v4l2_command(self,command):
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    def getDevice(self,serial):
        selected_device = None
        for device_path, serial in self.devices.items():
            if serial == desired_serial:
                selected_device = device_path
                break
        if selected_device is not None:
            return selected_device
        else:
            return None





