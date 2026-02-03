import wmi


class InfoHardWareScan:
    conn_hardware = wmi.WMI()
    def __init__(self):
        pass


    def scan_hardware(self):
        return  self.conn_hardware.classes

if __name__ == '__main__':
    inicit_obj_scan = InfoHardWareScan()
    result_scan = inicit_obj_scan.scan_hardware()

    print(result_scan)