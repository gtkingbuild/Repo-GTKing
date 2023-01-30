import hashlib
import logging
import os
import pipes
import re
import select
import shutil
import stat
import subprocess
import sys
import threading
from io import FileIO

from lib.os_platform import PLATFORM, System
from lib.utils import bytes_to_str, PY3


def compute_hex_digest(file_path, hash_type, buff_size=4096):
    h = hash_type()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(buff_size), b""):
            h.update(chunk)
    return h.hexdigest()


def get_current_app_id():
    with open("/proc/{:d}/cmdline".format(os.getpid())) as fp:
        return fp.read().rstrip("\0")


def join_cmd(cmd):
    return " ".join(pipes.quote(arg) for arg in cmd)


def read_select(fd, timeout):
    r, _, _ = select.select([fd], [], [], timeout)
    if fd not in r:
        raise SelectTimeoutError("Timed out waiting for pipe read")


# https://docs.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-sethandleinformation
HANDLE_FLAG_INHERIT = 0x00000001
# https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletype
FILE_TYPE_DISK = 0x0001


def windows_suppress_file_handles_inheritance(r=0xFFFF):
    from ctypes import windll, wintypes, byref

    handles = []
    for handle in range(r):
        if windll.kernel32.GetFileType(handle) == FILE_TYPE_DISK:
            flags = wintypes.DWORD()
            if windll.kernel32.GetHandleInformation(handle, byref(flags)) and flags.value & HANDLE_FLAG_INHERIT:
                if windll.kernel32.SetHandleInformation(handle, HANDLE_FLAG_INHERIT, 0):
                    handles.append(handle)
                else:
                    logging.error("Error clearing inherit flag, disk file handle %x", handle)

    return handles


def windows_restore_file_handles_inheritance(handles):
    from ctypes import windll

    for handle in handles:
        if not windll.kernel32.SetHandleInformation(handle, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT):
            logging.debug("Failed restoring handle %x inherit flag", handle)


class SelectTimeoutError(Exception):
    pass


class Pipe(object):
    def __init__(self):
        self._r, self._w = os.pipe()

    @property
    def r(self):
        return self._r

    @property
    def w(self):
        return self._w

    def read(self, buf, timeout=0):
        if self._r < 0:
            raise ValueError("read file descriptor is closed")
        if timeout > 0:
            read_select(self._r, timeout)
        return os.read(self._r, buf)

    def write(self, data):
        if self._w < 0:
            raise ValueError("write file descriptor is closed")
        return os.write(self._w, data)

    def close(self, read=False, write=False):
        both = not (read or write)
        if (both or read) and self._r >= 0:
            os.close(self._r)
            self._r = -1
        if (both or write) and self._w >= 0:
            os.close(self._w)
            self._w = -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class DefaultDaemonLogger(threading.Thread):
    def __init__(self, fd, default_level=logging.INFO, path=None):
        super(DefaultDaemonLogger, self).__init__()
        self.daemon = True
        self._fd = fd
        self._default_level = default_level
        self._file = open(path, "wb") if path else None
        self._stopped = False

    def _get_level_and_message(self, line):
        return self._default_level, line.rstrip("\r\n")

    def run(self):
        for line in iter(self._fd.readline, self._fd.read(0)):
            logging.log(*self._get_level_and_message(bytes_to_str(line)))
            if self._file:
                self._file.write(line)
                self._file.flush()
            if self._stopped:
                break

    def stop(self, timeout=None):
        self._stopped = True
        self.join(timeout)
        if self._file:
            self._file.close()


class DaemonLogger(DefaultDaemonLogger):
    levels_mapping = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "notice": logging.INFO,
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "trace": logging.DEBUG,
    }

    tag_regex = re.compile("\x1b\\[[\\d;]+m")
    level_regex = re.compile(r"^(?:{})*\d+-\d+-\d+ \d+:\d+:\d+\.\d+ ({})".format(
        tag_regex.pattern, "|".join(levels_mapping)), re.IGNORECASE)

    def _get_level_and_message(self, line):
        m = self.level_regex.search(line)
        if m:
            line = line[len(m.group(0)):].lstrip(" ")
            level = self.levels_mapping[m.group(1).lower()]
        else:
            level = self._default_level

        return level, self.tag_regex.sub("", line).rstrip("\r\n")


class DaemonNotFoundError(Exception):
    pass


class Daemon(object):
    def __init__(self, name, daemon_dir, work_dir=None, android_find_dest_dir=True,
                 android_extra_dirs=(), dest_dir=None, pid_file=None, root=False, contains_sha1=False):
        self._name = name
        self._work_dir = work_dir
        self._pid_file = pid_file
        self._root = root
        self._root_pid = -1
        self._contains_sha1 = contains_sha1
        if PLATFORM.system == System.windows:
            self._name += ".exe"

        src_path = os.path.join(daemon_dir, self._name)
        if not os.path.exists(src_path):
            raise DaemonNotFoundError("Daemon source path does not exist: " + src_path)

        if PLATFORM.system == System.android and android_find_dest_dir:
            app_dir = os.path.join(os.sep, "data", "data", get_current_app_id())
            if not os.path.exists(app_dir):
                logging.debug("Default android app dir '%s' does not exist", app_dir)
                for directory in android_extra_dirs:
                    if os.path.exists(directory):
                        app_dir = directory
                        break

            logging.debug("Using android app dir '%s'", app_dir)
            self._dir = os.path.join(app_dir, "files", name)
        else:
            self._dir = dest_dir or daemon_dir
        self._path = os.path.join(self._dir, self._name)

        if self._dir is not daemon_dir:
            if not os.path.exists(self._path) or self._compute_sha1(src_path) != self._compute_sha1(self._path):
                logging.info("Updating %s daemon '%s'", PLATFORM.system, self._path)
                try:
                    if os.path.exists(self._dir):
                        logging.debug("Removing old daemon dir %s", self._dir)
                        shutil.rmtree(self._dir)
                    shutil.copytree(daemon_dir, self._dir)
                except:
                    logging.info("Error udating %s daemon '%s'", PLATFORM.system, self._path)

        self._p = None  # type: subprocess.Popen or None
        self._logger = None  # type: DaemonLogger or None

    def _compute_sha1(self, path):
        if self._contains_sha1:
            # Legacy code
            # Using FileIO instead of open as fseeko with OFF_T=64 is broken in android NDK
            # See https://trac.kodi.tv/ticket/17827
            with FileIO(path) as f:
                f.seek(-40, os.SEEK_END)
                digest = f.read()
        else:
            digest = compute_hex_digest(path, hashlib.sha1)

        return digest

    def kill_leftover_process(self):
        if self._pid_file and os.path.exists(self._pid_file):
            try:
                with open(self._pid_file) as f:
                    pid = int(f.read().rstrip("\r\n\0"))
                logging.warning("Killing process with pid %d", pid)
                self._kill(pid, 9)
            except Exception as e:
                logging.error("Failed killing process: %s", e)
            finally:
                os.remove(self._pid_file)

    def _kill(self, pid, signal):
        if self._root:
            if PLATFORM.system == System.android:
                subprocess.check_call(["su", "-c", "kill -{} {}".format(signal, pid)])
            else:
                logging.debug("Not possible to use root on this platform. Falling back to os.kill.")
                os.kill(pid, signal)
        else:
            os.kill(pid, signal)

    def ensure_exec_permissions(self):
        try:
            st = os.stat(self._path)
            if st.st_mode & stat.S_IEXEC != stat.S_IEXEC:
                logging.info("Setting exec permissions")
                os.chmod(self._path, st.st_mode | stat.S_IEXEC)
        except:
            logging.info("Error on setting exec permissions")

    def start_daemon(self, *args):
        if self._p is not None:
            raise ValueError("daemon already running")
        logging.info("Starting daemon with args: %s", args)
        cmd = [self._path] + list(args)
        work_dir = self._work_dir or self._dir
        kwargs = {}

        if PLATFORM.system == System.windows:
            if not PY3:
                # Attempt to solve https://bugs.python.org/issue1759845
                encoding = sys.getfilesystemencoding()
                for i, arg in enumerate(cmd):
                    cmd[i] = arg.encode(encoding)
                work_dir = work_dir.encode(encoding)
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = si
            # Attempt to solve https://bugs.python.org/issue19575
            handles = windows_suppress_file_handles_inheritance()
        else:
            kwargs["close_fds"] = True
            # Make sure we update LD_LIBRARY_PATH, so libs are loaded
            env = os.environ.copy()
            ld_path = env.get("LD_LIBRARY_PATH", "")
            if ld_path:
                ld_path += os.pathsep
            ld_path += self._dir
            env["LD_LIBRARY_PATH"] = ld_path
            kwargs["env"] = env
            handles = []

        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
        kwargs["cwd"] = work_dir

        if self._root:
            if PLATFORM.system == System.android:
                cmd = ["su", "-c", "echo $$ && exec " + join_cmd(cmd)]
            else:
                logging.warning("Not possible to use root on this platform")

        logging.debug("Creating process with command %s and params %s", cmd, kwargs)
        try:
            self._p = call_binary('openBinary', cmd, p=self._p, **kwargs)
            if self._p.returncode == 888:
                self._p.returncode = None
                self._root = False
                logging.info("Process cannot be run as root")

            if self._root and PLATFORM.system == System.android:
                read_select(self._p.stdout.fileno(), 10)
                self._root_pid = int(self._p.stdout.readline().rstrip())

            if self._pid_file:
                logging.debug("Saving pid file %s", self._pid_file)
                with open(self._pid_file, "w") as f:
                    f.write(str(self._root_pid if self._root_pid >= 0 else self._p.pid))
        finally:
            if PLATFORM.system == System.windows:
                windows_restore_file_handles_inheritance(handles)

    def stop_daemon(self):
        if self._p is not None:
            logging.info("Terminating daemon")
            try:
                self._terminate()
            except (OSError, subprocess.CalledProcessError):
                logging.info("Daemon already terminated")
            if self._pid_file and os.path.exists(self._pid_file):
                os.remove(self._pid_file)
            self._root_pid = -1
            self._p = None

    def _terminate(self):
        if self._root and self._root_pid >= 0:
            if PLATFORM.system == System.android:
                subprocess.check_call(["su", "-c", "kill {}".format(self._root_pid)])
            else:
                logging.debug("Not possible to use root on this platform. Falling back to terminate.")
                self._p.terminate()
        else:
            self._p.terminate()

    def daemon_poll(self):
        return self._p and self._p.poll()

    @property
    def daemon_running(self):
        return self._p is not None and self._p.poll() is None

    def start_logger(self, level=logging.INFO, path=None):
        if self._logger is not None:
            raise ValueError("logger was already started")
        if self._p is None:
            raise ValueError("no process to log")
        logging.info("Starting daemon logger")
        self._logger = DaemonLogger(self._p.stdout, default_level=level, path=path)
        self._logger.start()

    def stop_logger(self):
        if self._logger is not None:
            logging.info("Stopping daemon logger")
            self._logger.stop()
            self._logger = None

    @property
    def logger_running(self):
        return self._logger is not None and self._logger.is_alive()

    def start(self, *args, **kwargs):
        self.start_daemon(*args)
        self.start_logger(**kwargs)

    def stop(self):
        self.stop_daemon()
        self.stop_logger()

# Launching Torrest through an external APP for Android >= 10 and Kodi >= 19
def call_binary(function, cmd, retry=False, p=None, **kwargs):
    import xbmc
    import xbmcaddon
    import traceback
    import base64
    import requests
    import time
    import json
    import xbmcvfs
    
    def translatePath(path):
        """
        Kodi 19: xbmc.translatePath is deprecated and might be removed in future kodi versions. Please use xbmcvfs.translatePath instead.
        @param path: cadena con path special://
        @type path: str
        @rtype: str
        @return: devuelve la cadena con el path real
        """
        if PY3:
            if isinstance(path, bytes):
                path = path.decode('utf-8')
            path = xbmcvfs.translatePath(path)
            if isinstance(path, bytes):
                path = path.decode('utf-8')
        else:
            path = xbmc.translatePath(path)
        return path
    
    # Lets try first the traditional way
    if not p:
        try:
            p = subprocess.Popen(cmd, **kwargs)
            logging.info('## Executing Popen.CMD: %s - PID: %s', cmd, p.pid)
            return p
        except Exception as e:
            if not PY3:
                e = unicode(str(e), "utf8", errors="replace").encode("utf8")
            elif PY3 and isinstance(e, bytes):
                e = e.decode("utf8")
            logging.info('Exception Popen ERROR: %s, %s', str(cmd), str(e))
            
            if PLATFORM.system == System.android and ('Errno 13' in str(e) or 'Errno 2' in str(e)):
                p = None
            else:
                return p

    # The traditional way did not work, so most probably we hit the SDK 29 problem
    APP_PARAMS = {
                  'Torrest':  {
                               'ACTIVE': 0, 
                               'USER_ADDON': 'plugin.video.torrest', 
                               'USER_ADDON_STATUS': xbmc.getCondVisibility('System.HasAddon("plugin.video.torrest")'), 
                               'USER_ADDON_USERDATA': os.path.join(translatePath('special://masterprofile/'), 
                                            'addon_data', 'plugin.video.torrest'), 
                               'USER_APK': [os.path.join(translatePath('special://xbmcbinaddons/'), 
                                            'plugin.video.torrest', 'resources', 'apk', 
                                            'torrest-mobile-assistant.apk')], 
                               'USER_APP': 'com.torrest.torrestmobileassistant', 
                               'USER_APP_CONTROL': 'torrest-mobile-assistant.version',
                               'USER_APP_URL': 'http://127.0.0.1', 
                               'USER_APP_PORT': '66666',
                               'USER_APP_PORT_ALT': '66667'
                              }, 
                  'Alfa':     {
                               'ACTIVE': 1, 
                               'USER_ADDON': 'plugin.video.alfa', 
                               'USER_ADDON_STATUS': xbmc.getCondVisibility('System.HasAddon("plugin.video.alfa")'), 
                               'USER_ADDON_USERDATA': os.path.join(translatePath('special://masterprofile/'), 
                                            'addon_data', 'plugin.video.alfa'), 
                               'USER_APK': 
                                    ['https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/alfa-mobile-assistant.apk',
                                    'https://raw.githubusercontent.com/alfa-addon/alfa-repo/master/downloads/assistant/alfa-mobile-assistant.version'], 
                               'USER_APP': 'com.alfa.alfamobileassistant', 
                               'USER_APP_CONTROL': 'alfa-mobile-assistant.version',
                               'USER_APP_URL': 'http://127.0.0.1', 
                               'USER_APP_PORT': '48885',
                               'USER_APP_PORT_ALT': '48886'
                              }
                  }
    
    TORREST_ADDON_SETTING = xbmcaddon.Addon()
    run_as_root = False
    if TORREST_ADDON_SETTING.getSetting('run_as_root') == 'true':
        TORREST_ADDON_SETTING.setSetting('run_as_root', 'false')
        run_as_root = True
        logging.info('## Assistant checking "run_as_root": SET to False')
    TORREST_ADDON_USERDATA = translatePath(TORREST_ADDON_SETTING.getAddonInfo("profile"))
    USER_APP_URL = ''
    USER_APP_URL_ALT = ''
    USER_ADDON = ''
    USER_ADDON_STATUS = False
    ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
    if not ANDROID_STORAGE: ANDROID_STORAGE = '/storage'
    USER_APP = ''
    USER_APP_PATH = os.path.join(ANDROID_STORAGE, 'emulated', '0', 'Android', 'data')
    USER_APP_STATUS = False

    for user_addon, user_params in list(APP_PARAMS.items()):
        if not user_params['ACTIVE'] or not user_params['USER_ADDON_STATUS']: continue
        
        if user_addon == 'Torrest':
            try:
                # Torrest add-on and Torrest Assistant installed
                USER_ADDON = user_params['USER_ADDON']
                USER_ADDON_STATUS = True
                if os.path.exists(os.path.join(USER_APP_PATH, user_params['USER_APP'])):
                    USER_APP = user_params['USER_APP']
                    USER_APP_STATUS = True
                    USER_APP_URL = "%s:%s" % (user_params['USER_APP_URL'], user_params['USER_APP_PORT'])
                    USER_APP_URL_ALT = "%s:%s" % (user_params['USER_APP_URL'], user_params['USER_APP_PORT_ALT'])
                if USER_APP_STATUS: break
            except:
                logging.info(traceback.format_exc())
        
        if user_addon == 'Alfa':
            try:
                try:
                    # Alfa add-on and Alfa Assistant installed
                    USER_ADDON_SETTING = xbmcaddon.Addon(id="%s" % user_params['USER_ADDON'])
                    USER_ADDON = user_params['USER_ADDON']
                    USER_ADDON_STATUS = True
                    #if USER_ADDON_SETTING.getSetting('is_rooted_device') == 'rooted':
                    #    USER_ADDON_SETTING.setSetting('is_rooted_device', 'check')
                    #    logging.info('## Assistant checking "is_rooted_device": SET to "check"')
                    if os.path.exists(os.path.join(USER_APP_PATH, user_params['USER_APP'])):
                        USER_APP = user_params['USER_APP']
                        USER_APP_STATUS = True
                        USER_APP_URL_base = user_params['USER_APP_URL']
                        USER_APP_URL = "%s:%s" % (USER_APP_URL_base, user_params['USER_APP_PORT'])
                        USER_APP_URL_ALT = "%s:%s" % (USER_APP_URL_base, user_params['USER_APP_PORT_ALT'])
                except:
                    # Only Alfa Assistant installed and not Alfa
                    if os.path.exists(os.path.join(USER_APP_PATH, user_params['USER_APP'])):
                        USER_APP_STATUS = True
                if USER_APP_STATUS: break
            except:
                logging.info(traceback.format_exc())

    if not USER_APP_STATUS:
        user_params = install_app(APP_PARAMS)
        if not user_params.get('USER_APP', '') or not user_params.get('USER_APP_URL', '') \
                        or not user_params.get('USER_APP_PORT', '') or not user_params.get('USER_APP_PORT_ALT', ''):
            raise ValueError("No app: One MUST be installed")
        else:
            USER_APP_STATUS = True
            USER_APP = user_params['USER_APP']
            USER_APP_URL = "%s:%s" % (user_params['USER_APP_URL'], user_params['USER_APP_PORT'])
            USER_APP_URL_ALT = "%s:%s" % (user_params['USER_APP_URL'], user_params['USER_APP_PORT_ALT'])

    if USER_APP_STATUS:
        try:
            try:
                # Special process for Android 11+: setting download paths in a "free zone"
                os_release = 0
                if PY3:
                    FF = b'\n'
                else:
                    FF = '\n'
                try:
                    for label_a in subprocess.check_output('getprop').split(FF):
                        if PY3 and isinstance(label_a, bytes):
                            label_a = label_a.decode()
                        if 'build.version.release' in label_a:
                            os_release = int(re.findall(':\s*\[(.*?)\]$', label_a, flags=re.DOTALL)[0])
                            break
                except:
                    try:
                        with open(os.environ['ANDROID_ROOT'] + '/build.prop', "r") as f:
                            labels = read(f)
                        for label_a in labels.split():
                            if PY3 and isinstance(label_a, bytes):
                                label_a = label_a.decode()
                            if 'build.version.release' in label_a:
                                os_release = int(re.findall('=(.*?)$', label_a, flags=re.DOTALL)[0])
                                break
                    except:
                        os_release = 10
                
                # If Android 11+, reset the download & torrents paths to /storage/emulated/0/Download/Kodi/Torrest/...
                if os.path.exists(cmd[-1]):
                    os.remove(cmd[-1])
                if os_release >= 11:
                    cmd[-1] = cmd[-1].replace('Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.torrest', \
                                            'Download/Kodi/Torrest')
                    if 'userdata/addon_data/plugin.video.' in TORREST_ADDON_SETTING.getSetting('s:download_path'):
                        download_path = '/storage/emulated/0/Download/Kodi/Torrest/downloads/'
                        TORREST_ADDON_SETTING.setSetting('s:download_path', download_path)
                        if not os.path.exists(download_path):
                            res = xbmcvfs.mkdirs(download_path)
                    if 'userdata/addon_data/plugin.video.' in TORREST_ADDON_SETTING.getSetting('s:torrents_path'):
                        torrents_path = '/storage/emulated/0/Download/Kodi/Torrest/torrents/'
                        TORREST_ADDON_SETTING.setSetting('s:torrents_path', torrents_path)
                        if not os.path.exists(torrents_path):
                            res = xbmcvfs.mkdirs(torrents_path)
                    if os.path.exists(cmd[-1]):
                        os.remove(cmd[-1])
                
                # As settings.json does not exists, it creates an initial one to avoid Torrest mkdir "downloads" in bin read-only folder
                cmd_back = cmd[:]
                for arg in cmd:
                    s = {}
                    if 'settings.json' in arg:
                        from lib import kodi
                        from lib.utils import assure_unicode
                        argum = arg
                        # "run_as_root" is incompatible with this process, creating a wrong format for the call.  It has to be reseted
                        if run_as_root:
                            cmd_back = argum.replace('echo $$ && exec ', '').split(' ')
                            for argum in cmd_back:
                                if 'settings.json' in argum:
                                    break
                            else:
                                argum = ''

                        if not s:
                            _settings_prefix = "s"
                            _settings_separator = ":"
                            _settings_spec = [s for s in kodi.get_all_settings_spec() if s["id"].startswith(
                                            _settings_prefix + _settings_separator)]
                            s = kodi.generate_dict_settings(_settings_spec, separator=_settings_separator)[_settings_prefix]
                            s["download_path"] = assure_unicode(translatePath(s["download_path"]))
                            s["torrents_path"] = assure_unicode(translatePath(s["torrents_path"]))
                            try:
                                if not os.path.exists(os.path.dirname(argum)):
                                    res = xbmcvfs.mkdirs(os.path.dirname(argum))
                                if not os.path.exists(s["download_path"]):
                                    res = xbmcvfs.mkdirs(s["download_path"])
                                if not os.path.exists(s["torrents_path"]):
                                    res = xbmcvfs.mkdirs(s["torrents_path"])
                            except:
                                logging.info('## Assistant ERROR creating DIRS for "download_path" or "torrents_path"')
                            with open(argum, "w") as f:
                                json.dump(s, f, indent=3)
                            logging.info('## Assistant CREATING initial settings.json: %s - AT %s/ %s', \
                                            s, os.path.dirname(argum), os.listdir(os.path.dirname(argum)))
                            
                cmd = cmd_back[:]
            except:
                logging.info('## Assistant checking settings.json: ERROR on processing .json AT %s', arg)
                logging.info(traceback.format_exc())
            
            """
            Assistant APP acts as a CONSOLE for binaries management in Android 10+ and Kodi 19+
            
            Syntax StartAndroidActivity("USER_APP", "", "function", "cmd|arg| ... |arg|||dict{env} in format |key=value|... "):
                  
                  - cmd: binary name in format '$PWD/lib'binary_name'.so'
                  - 'open':                                                     START the Assitant
                  - 'terminate':                                                CLOSE Assistant
                  - "OpenBinary", "$PWD/libBINARY.so|-port|61235|-settings|/storage/emulated/.../settings.json|||
                                    (kwargs[env]): |key=value|etc=etc":         CALL binary
            
            Syntax Http requests: http://127.0.0.1:48884/command?option=value
                  
                  - /openBinary?cmd=base64OfFullCommand($PWD/libBINARY.so|-port|61235| 
                                    -settings|/storage/emulated/.../settings.json|||
                                    (kwargs[env]): |key=value|etc=etc):         CALL binary
                          - returns: {
                                      "pid": 999,
                                      "output": "Base64encoded",
                                      "error": "Base64encoded",
                                      "startDate": "Base64encoded(2021-12-13 14:00:12)",
                                      "endDate": "Base64encoded([2021-12-13 14:00:12])",    If ended
                                      "retCode": "0|1|number|None"                          None if not ended
                                      "cmd": "Base64encoded(command *args **kwargs)"        Full command as sent to the app
                                      "finalCmd": "Base64encoded($PWD/command *args)"       Actual command executed vy the app
                                      
                  - /openBinary?cmd=base64OfFullCommand([[ANY Android/Linux command: killall libtorrest.so (kills all Torrest binaries)]])
                          - returns: {As in /openBinary?cmd}
                  
                  - /getBinaryStatus?pid=999:                                   Request binary STATUS by PID
                          - returns: {As in /openBinary?cmd}
                  
                  - /killBinary?pid=999:                                        Request KILL binary PID
                          - returns: {As in /openBinary?cmd}

                  - /getBinaryList:                                             Return a /getBinaryStatus per binary launched during app session
                          - returns: {As in /openBinary?cmd}
                  - /terminate:                                                 Close Assistant
            """
            
            # Lets start the Assistant app
            separator = '|'
            separator_escaped = '\|'
            separator_kwargs = '|||'
            command = []
            status_code = 0
            cmd_app = ''
            
            url = ''
            url_open = USER_APP_URL + '/openBinary?cmd='
            url_killall = url_open + base64.b64encode(str('killall%slibtorrest.so' % separator).encode('utf8')).decode('utf8')
            if isinstance(p, int):
                url_killall = USER_APP_URL + '/killBinary?pid=%s' % p
            cmd_android = 'StartAndroidActivity("%s", "", "%s", "%s")' % (USER_APP, 'open', 'about:blank')
            cmd_android_close = 'StartAndroidActivity("%s", "", "%s", "%s")' % (USER_APP, 'terminate', 'about:blank')
            xbmc.executebuiltin(cmd_android)
            time.sleep(3)

            # Build the command & params
            if isinstance(cmd, list):
                command.append(cmd)
                command.append(kwargs)
                # Convert Args to APP format
                cmd_bis = cmd[:]
                cmd_bis[0] = '$PWD/libtorrest.so'
                for args in cmd_bis:
                    cmd_app += args.replace(separator, separator_escaped) + separator
                cmd_app = cmd_app.rstrip(separator)
                # Convert Kwargs to APP format
                if kwargs.get('env', {}):
                    cmd_app += separator_kwargs
                for key, value in list(kwargs.get('env', {}).items()):
                    if key == 'LD_LIBRARY_PATH':
                        # The app will replace $PWD by the binary/lib path
                        value = '$PWD'
                    if key == 'PATH':
                        # The app will replace $PWD by the binary/lib path
                        value = '$PWD:%s' % value
                    cmd_app += '%s=%s%s' % (key.replace(separator, separator_escaped), \
                                value.replace(separator, separator_escaped), separator)
                cmd_app = cmd_app.rstrip(separator)
                command_base64 = base64.b64encode(cmd_app.encode('utf8')).decode('utf8')
            else:
                command_base64 = cmd
                cmd = p.args_
                kwargs = p.kwargs_
                command.append(cmd)
                command.append(kwargs)

            # Launch the Binary
            launch_status = True
            try:
                session = requests.Session()
                # First, cancel existing Binary sessions
                url = url_killall
                logging.info('## Killing Torrest from Assistant App: %s', url)
                resp = session.get(url, timeout=5)
                status_code = resp.status_code
                if status_code != 200:
                    logging.info('## ERROR Killing Torrest from Assistant App: %s', resp.content)
                time.sleep(1)
                # Now lets launch the Binary
                logging.info('## Calling Torrest from Assistant App: %s - Retry = %s', cmd, retry)
                url = url_open + command_base64
                resp = session.get(url, timeout=5)
            except Exception as e:
                resp = requests.Response()
                resp.status_code = str(e)
            status_code = resp.status_code
            if status_code != 200 and not retry:
                logging.info("## Calling/Killing Torrest: Invalid app requests response: %s.  Closing Assistant (1)", status_code)
                xbmc.executebuiltin(cmd_android_close)
                time.sleep(4)
                return call_binary(function, cmd, retry=True, **kwargs)
            elif status_code != 200 and retry:
                logging.info("## Calling/Killing Torrest: Invalid app requests response: %s.  Closing Assistant (2)", status_code)
                launch_status = False
                xbmc.executebuiltin(cmd_android_close)
                time.sleep(4)
            try:
                app_response = resp.content
                if launch_status:
                    if PY3 and isinstance(app_response, bytes):
                        app_response = app_response.decode()
                    app_response = re.sub('\n|\r|\t', '', app_response)
                    app_response = json.loads(app_response)
            except:
                status_code = resp.content
                launch_status = False
                logging.info("## Calling Torrest: Invalid app response: %s", resp.content)

            # Simulate the response from subprocess.Popen
            pipeout, pipein = os.pipe()
            class Proc:
                pid = 999999
                stdout = os.fdopen(pipeout, 'rb')
                stdin = os.fdopen(pipein, 'wb')
                stderr = stdout
                returncode = None
                startDate = ''
                endDate = ''
                poll = ''
                terminate = ''
                communicate = ''
                app = USER_APP
                url_app = USER_APP_URL
                url_app_alt = USER_APP_URL_ALT
                cmd_app = command_base64
                finalCmd = ''
                args_ = cmd
                kwargs_ = kwargs
                sess = session
                monitor = xbmc.Monitor()
                binary_time = time.time()
                binary_awake = 0

            p = Proc()
            
            def redirect_terminate(p=p, action='killBinary'):
                return binary_stat(p, action)
            def redirect_poll(p=p, action='poll'):
                return binary_stat(p, action)
            def redirect_communicate(p=p, action='communicate'):
                return binary_stat(p, action)
            p.poll = redirect_poll
            p.terminate = redirect_terminate
            p.communicate = redirect_communicate
            
            # If something went wrong on the binary launch, lets return the error so it is recovered from the standard code
            if not launch_status:
                p.returncode = 999
                raise ValueError("No app response:  error code: %s" % status_code)

            try:
                p.pid = int(app_response['pid'])
            except:
                raise ValueError("No valid PID returned:  PID code: %s" % resp.content)

            # Handle initial messages
            time.sleep(2)
            if app_response.get('output') or app_response.get('error'):
                res = binary_stat(p, 'poll', app_response=app_response)
            else:
                for x in range(20):
                    res = binary_stat(p, 'poll', init=True)
                    if res: break
                    time.sleep(1)
                else:
                    # Is the binary hung?  Lets restart it
                    return call_binary(function, command_base64, retry=True, kwargs={})

            # Tell the caller that run_as_root is not possible
            if run_as_root:
                p.returncode = 888
            
            logging.info('## Assistant executing CMD: %s - PID: %s', command[0], p.pid)
            logging.debug('## Assistant executing CMD **kwargs: %s', command[1])
        except:
            logging.info('## Assistant ERROR %s in CMD: %s%s', status_code, url, command)
            logging.info(traceback.format_exc())
            
    return p

def binary_stat(p, action, retry=False, init=False, app_response={}):
    if init: logging.info('## Binary_stat: action: %s; PID: %s; retry: %s; init: %s; awake: %s; app_r: %s', \
                        action, p.pid, retry, init, p.binary_awake, app_response)
    import traceback
    import base64
    import requests
    import json
    import time
    import xbmc
    
    try:
        if action in ['poll', 'communicate']:
            url = p.url_app + '/getBinaryStatus?pid=%s&flushAfterRead=true' % str(p.pid)
            url_alt = p.url_app_alt + '/getBinaryStatus?pid=%s&flushAfterRead=true' % str(p.pid)

        if action == 'killBinary':
            url = p.url_app + '/killBinary?pid=%s' % str(p.pid)
            url_alt = p.url_app_alt + '/killBinary?pid=%s' % str(p.pid)

        url_close = p.url_app + '/terminate'
        cmd_android = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'open', 'about:blank')
        cmd_android_quit = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'quit', 'about:blank')
        cmd_android_close = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'terminate', 'about:blank')
        cmd_android_permissions = 'StartAndroidActivity("%s", "", "%s", "%s")' % (p.app, 'checkPermissions', 'about:blank')

        finished = False
        retry_req = False
        retry_app = False
        stdout_acum = ''
        stderr_acum = ''
        msg = ''
        binary_awake = 0
        binary_awake_safe = 300*1000
        while not finished:
            if not isinstance(app_response, dict):
                logging.info("## ERROR in app_response: %s - type: %s", str(app_response), str(type(app_response)))
                app_response = {}
            if not app_response.get('retCode', 0) >= 999:
                try:
                    resp = p.sess.get(url, timeout=5)
                except Exception as e:
                    resp = requests.Response()
                    resp.status_code = str(e)
                
                if resp.status_code != 200 and not retry_req:
                    if action == 'killBinary' or p.monitor.abortRequested():
                        app_response = {'pid': p.pid, 'retCode': 998}
                        retry_req = False
                    else:
                        logging.info("## Binary_stat: Invalid app requests response for PID: %s: %s - retry: %s - awake: %s", \
                                    p.pid, resp.status_code, retry_req, p.binary_awake)
                        retry_req = True
                        url = url_alt
                        msg += str(resp.status_code)
                        stdout_acum += str(resp.status_code)
                        xbmc.executebuiltin(cmd_android)
                        binary_awake = (int(time.time()) - int(p.binary_time)) * 1000 - binary_awake_safe
                        if binary_awake < binary_awake_safe:
                            binary_awake = 0
                        logging.info('## Time.awake: %s; binary_awake: %s; p.binary_awake: %s', \
                                    (int(time.time()) - int(p.binary_time))*1000, binary_awake, p.binary_awake)
                        time.sleep(4)
                        continue
                if resp.status_code != 200 and retry_req and app_response.get('retCode', 0) != 999 and not p.monitor.abortRequested():
                    logging.info("## Binary_stat: Invalid app requests response for PID: %s: %s - retry: %s - awake: %s.  Closing Assistant", \
                                    p.pid, resp.status_code, retry_req, p.binary_awake)
                    msg += str(resp.status_code)
                    stdout_acum += str(resp.status_code)
                    app_response = {'pid': p.pid, 'retCode': 999}
                    xbmc.executebuiltin(cmd_android_close)
                    time.sleep(4)
                    xbmc.executebuiltin(cmd_android)
                    binary_awake = (int(time.time()) - int(p.binary_time)) * 1000 - binary_awake_safe
                    if binary_awake > binary_awake_safe:
                        if p.binary_awake:
                            if binary_awake < p.binary_awake: p.binary_awake = binary_awake
                        else:
                            p.binary_awake = binary_awake
                        time.sleep(4)
                        logging.info('## Time.awake: %s; binary_awake: %s; p.binary_awake: %s; awakingInterval: True', \
                                    (int(time.time()) - int(p.binary_time))*1000, binary_awake, p.binary_awake)
                        try:
                            if not 'awakingInterval' in url: 
                                url += '&awakingInterval=%s' % p.binary_awake
                                resp = p.sess.get(url, timeout=5)
                        except:
                            pass
                        time.sleep(1)
                        continue
                    time.sleep(4)
                    continue

                if resp.status_code == 200:
                    try:
                        app_response = resp.content
                        if init: logging.debug(app_response)
                        if PY3 and isinstance(app_response, bytes):
                            app_response = app_response.decode()
                        app_response_save = app_response
                        app_response = re.sub('\n|\r|\t', '', app_response)
                        app_response = json.loads(app_response)
                        test_json = app_response["pid"]
                    except:
                        status_code = resp.content
                        logging.info("## Binary_stat: Invalid app response for PID: %s: %s - retry: %s - awake: %s", \
                                    p.pid, resp.content, retry_app, binary_awake)
                        if retry_app:
                            app_response = {'pid': p.pid}
                            app_response['retCode'] = 999
                            msg += app_response_save
                            stdout_acum += app_response_save
                        else:
                            retry_app = True
                            app_response = {}
                            if not 'awakingInterval' in url and (binary_awake > 0 or p.binary_awake > 0):
                                if p.binary_awake:
                                    if binary_awake and binary_awake < p.binary_awake: p.binary_awake = binary_awake
                                else:
                                    p.binary_awake = binary_awake
                                url += '&awakingInterval=%s' % p.binary_awake
                                logging.info('## Time.awake: %s; binary_awake: %s; p.binary_awake: %s; awakingInterval: True', \
                                            (int(time.time()) - int(p.binary_time))*1000, binary_awake, p.binary_awake)
                            time.sleep(1)
                            continue
                        
            if app_response.get("pid", 0):
                if app_response.get('output'):
                    stdout_acum += base64.b64decode(app_response['output']).decode('utf-8')
                    msg += base64.b64decode(app_response['output']).decode('utf-8')
                if app_response.get('error'): 
                    stderr_acum += base64.b64decode(app_response['error']).decode('utf-8')
                    msg += base64.b64decode(app_response['error']).decode('utf-8')
                if app_response.get('startDate'): 
                    p.startDate = base64.b64decode(app_response['startDate']).decode('utf-8')
                if app_response.get('endDate'): 
                    p.endDate = base64.b64decode(app_response['endDate']).decode('utf-8')
                if app_response.get('cmd'): 
                    p.cmd_app = base64.b64decode(app_response['cmd']).decode('utf-8')
                if app_response.get('finalCmd'): 
                    p.finalCmd = base64.b64decode(app_response['finalCmd']).decode('utf-8')

                # If still app permissions not allowed, give it a retry
                if 'permission denied' in msg:
                    from lib import kodi
                    kodi.notification('Accept Assitant permissions', time=15000)
                    if not p.monitor.abortRequested(): time.sleep(4)
                    xbmc.executebuiltin(cmd_android_permissions)
                    if not p.monitor.abortRequested(): time.sleep(4)
                    if not p.monitor.abortRequested(): time.sleep(4)
                    xbmc.executebuiltin(cmd_android_quit)
                    if not p.monitor.abortRequested(): time.sleep(3)
                
                if msg:
                    try:
                        for line in msg.split('\n'):
                            line += '\n'
                            if PY3 and not isinstance(line, (bytes, bytearray)):
                                line = line.encode('utf-8')
                            p.stdin.write(line)
                            p.stdin.flush()
                    except:
                        pass
            
            p.returncode = None
            if action == 'killBinary' and not app_response.get('retCode', ''):
                app_response['retCode'] = 137
            if app_response.get('retCode', '') or action == 'killBinary' or \
                            (action == 'communicate' and app_response.get('retCode', '') != ''):
                try:
                    p.stdin.flush()
                    p.stdin.close()
                except:
                    pass
                try:
                    p.returncode = int(app_response['retCode'])
                except:
                    p.returncode = app_response['retCode']
                
            if action == 'communicate' and p.returncode is not None:
                logging.info("## Binary_stat: communicate Torrest: %s - Returncode: %s", p.pid, p.returncode)
                return stdout_acum, stderr_acum
            
            elif action == 'poll':
                if init and msg:
                    logging.debug('## Binary_stat: Torrest initial response: %s', msg)
                    return True
                return p.returncode
            
            elif action == 'killBinary':
                logging.info("## Binary_stat: killBinary Torrest: %s - Returncode: %s", p.pid, p.returncode)
                try:
                    if p.monitor.abortRequested():
                        try:
                            resp_t = p.sess.get(url_close, timeout=1)
                        except:
                            pass
                    elif p.returncode == 998:
                        xbmc.executebuiltin(cmd_android_close)
                        time.sleep(4)
                except:
                    logging.info(traceback.format_exc())
                    time.sleep(1)
                    xbmc.executebuiltin(cmd_android_close)
                    time.sleep(2)
                return p
            
            if not p.monitor.abortRequested():
                time.sleep(4)
            else:
                return p
            msg = ''
            app_response = {}

    except:
        logging.info(traceback.format_exc())
    return None

def install_app(APP_PARAMS):
    import traceback
    import requests
    import xbmc
    import time
    from lib import kodi
    
    try:
        user_params = {}
        apk_OK = False
        ANDROID_STORAGE = os.getenv('ANDROID_STORAGE')
        if not ANDROID_STORAGE: ANDROID_STORAGE = '/storage'
        LOCAL_DOWNLOAD_PATH = os.path.join(ANDROID_STORAGE, 'emulated', '0', 'Download')
        USER_APP_PATH = os.path.join(ANDROID_STORAGE, 'emulated', '0', 'Android', 'data')

        for user_addon, user_params in list(APP_PARAMS.items()):
            if not user_params['ACTIVE']: continue
                
            for apk_path in user_params['USER_APK']:
                if apk_path.endswith('.apk'):
                    download_path = LOCAL_DOWNLOAD_PATH
                elif user_params['USER_ADDON_STATUS']:
                    download_path = user_params['USER_ADDON_USERDATA']
                else:
                    continue
                
                if apk_path.startswith('http'):
                    try:
                        apk_body = requests.get(apk_path, timeout=10)
                    except Exception as e:
                        apk_body = requests.Response()
                        apk_body.status_code = str(e)
                    if apk_body.status_code != 200:
                        logging.info("## Install_app: Invalid app requests response: %s", apk_body.status_code)
                        apk_OK = False
                        continue
                    with open(os.path.join(download_path, \
                            os.path.basename(apk_path)), "wb") as f:
                        f.write(apk_body.content)
                    apk_OK = True
                
                else:
                    if os.path.exists(apk_path):
                        shutil.copy(apk_path, download_path)
                        apk_OK = True
                    else:
                        continue
                if not apk_OK:
                    break
            
            if apk_OK:
                logging.info("## Install_app: Installing the APK from: %s", LOCAL_DOWNLOAD_PATH)
                kodi.notification('Install your Assistant %s from folder %s' % \
                            (os.path.basename(user_params['USER_APK'][0]), \
                            LOCAL_DOWNLOAD_PATH))
                cmd_android = 'StartAndroidActivity("%s", "", "%s", "%s")' % (user_params['USER_APP'], 'open', 'about:blank')
                cmd_android_permissions = 'StartAndroidActivity("%s", "", "%s", "%s")' % (user_params['USER_APP'], 'checkPermissions', 'about:blank')
                cmd_android_close = 'StartAndroidActivity("%s", "", "%s", "%s")' % (user_params['USER_APP'], 'terminate', 'about:blank')
                xbmc.executebuiltin(cmd_android)
                time.sleep(1)
                
                # Lets give the user 5 minutes to install the app an retry automatically
                for x in range(300):
                    if os.path.exists(os.path.join(USER_APP_PATH, user_params['USER_APP'])):
                        logging.info("## Install_app: APP installed: %s", user_params['USER_APP'])
                        kodi.notification('Accept Assistant permissions')
                        logging.info("## Install_app: Requesting permissions: %s", user_params['USER_APP'])
                        time.sleep(4)
                        xbmc.executebuiltin(cmd_android_permissions)
                        time.sleep(15)
                        logging.info("## Install_app: closing APP: %s", user_params['USER_APP'])
                        kodi.notification('Accept Assistant permissions')
                        xbmc.executebuiltin(cmd_android_close)
                        logging.info("## Install_app: APP closed: %s", user_params['USER_APP'])
                        time.sleep(10)
                        return user_params
                    
                    xbmc.executebuiltin(cmd_android)
                    time.sleep(1)
                break
    
    except:
        logging.info(traceback.format_exc())
        user_params = {}
    return user_params