from zhmiscellanygsudo import rerun_as_admin
import winreg
import sys
import ctypes

def _is_windows():
    return sys.platform.startswith("win")

def _check_if_admin():
    """
    Check if zelepy is running as admin
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except:
        return False
    
def _ensure_admin():
    if _check_if_admin():
        return
    else:
        rerun_as_admin()    

def _find_app_starting_with(prefix: str) -> str | None:
    """
    Find the installation path of an application whose display name starts with 'prefix'.
    Returns None if not found, or if an issue was encountered.
    """
    prefix = prefix.lower()

    # uninstall registry keys for 32 and 64-bit apps
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]

    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for subkey in uninstall_keys:
            try:
                with winreg.OpenKey(root, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            sk_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sk_name) as sk:
                                try:
                                    display_name = winreg.QueryValueEx(sk, "DisplayName")[0]
                                except FileNotFoundError:
                                    continue

                                if display_name.lower().startswith(prefix):
                                    install_dir = ""
                                    try:
                                        install_dir = winreg.QueryValueEx(sk, "InstallLocation")[0]
                                        return install_dir
                                    except FileNotFoundError:
                                        pass
                                
                        except OSError:
                            continue
            except OSError:
                continue

    return None