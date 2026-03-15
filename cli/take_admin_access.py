
import ctypes
import sys
import os
from cli.checkOS import checkOS

def is_admin():
    try:
        if checkOS() == 'windows':
            return ctypes.windll.shell32.IsUserAnAdmin()
        elif checkOS() == 'linux' or checkOS() == 'darwin':
            return os.geteuid() == 0
        else:
            return True
    except:
        return False

def req_Admin_Access():
    current_os = checkOS()
    if not is_admin():
        if current_os == 'windows':
            # Trigger UAC popup and re-launch as admin
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        elif current_os == 'linux' or current_os == 'darwin':
            # Re-launch the script with sudo
            print("🔐 Root access required. Re-launching with sudo...")
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            # os.execvp replaces the current process — sys.exit() not needed