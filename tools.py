
import os
import time
import subprocess
import serial

class config:
    def __init__(self, board_name, un, pw, ip, dev, dev_us, boot_bin_filename):
        self.board_name = board_name
        self.username = un
        self.password = pw
        self.board_ip = ip
        self.boot_bin_filename = boot_bin_filename
        self.com = []
        self.arch = ""
        self.__devices = dev
        self.__devices_us = dev_us
        self.check_architecture()

    def check_architecture(self):
        cmd = "uname -a"
        output = self.do_remote(cmd)
        print(output)
        if "aarch64" in str(output):
            self.arch = "arm64"
            self.devices = self.__devices_us
        else:
            self.arch = "arm"
            self.devices = self.__devices

    def copy_file(self, filename,target):
        cmd = "scp "+filename+" "+self.username+"@"+self.board_ip+":"+target
        output = subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT)

    def do_remote(self, cmd):
        cmd = "ssh "+self.username+"@"+self.board_ip+" "+cmd
        output = subprocess.check_output(cmd,shell=True,stderr=subprocess.STDOUT)
        return output

    def reboot_board(self):
        self.do_remote("reboot")
        time.sleep(4)
        # Wait
        for k in range(30):
            cmd = ["ping","-c","1","-w","1",self.board_ip]
            with open(os.devnull, "w") as f:
                out = subprocess.call(cmd,stdout=f,shell=False)
            if out==0:
                return True
        return False

    def serial_start(self):
        self.com = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        self.com.reset_input_buffer()
        # com.open()

    def serial_done(self):
        f = open('uart_'+self.board_name+'.log','w')
        while self.com.in_waiting > 10:
            data = self.com.readline()
            try:
                data = str(data.decode('ASCII'))
                f.write(data)
            except:
                continue
        self.com.close()
        f.close()

    def update_boot_bin(self):
        if not os.path.exists(self.boot_bin_filename):
            raise(self.boot_bin_filename+" not found")
        self.do_remote("mkdir -p /media/mount")
        try:
            self.do_remote("mount /dev/mmcblk0p1 /media/mount")
        except:
            self.do_remote("umount /media/mount")
            self.do_remote("mount /dev/mmcblk0p1 /media/mount")
        self.copy_file(self.boot_bin_filename,"/media/mount/")
        self.do_remote("umount /media/mount")
