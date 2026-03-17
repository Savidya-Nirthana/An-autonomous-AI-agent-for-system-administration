import ctypes
import sys
import os
import platform

def is_admin() -> bool:
    """
    Check if the current process has administrative privileges.
    """
    if platform.system().lower() != "windows":
        # For non-Windows, we assume for now or check for root if needed
        try:
            return os.getuid() == 0
        except AttributeError:
            return False
            
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def request_admin():
    """
    Attempt to restart the current script with administrative privileges.
    This will trigger a Windows UAC prompt.
    """
    if platform.system().lower() != "windows":
        print("Administrative elevation is only supported on Windows in this implementation.")
        return

    # Prepare arguments for elevation
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    
    # Use ShellExecuteEx to run as 'runas' (admin)
    # 0 = hidden, 1 = normal, 3 = maximized
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    
    if int(ret) > 32:
        # Success (at least the request was sent and UAC accepted)
        sys.exit(0)
    else:
        # User likely clicked 'No' or another error occurred
        return False
