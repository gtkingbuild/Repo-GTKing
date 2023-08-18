import os
import signal
import subprocess
import xbmcgui

from threading import Thread
from lib.acestream.object import Observable


class Engine(Observable):
  def __init__(self, bin, **options):
    Observable.__init__(self)

    self.process = None
    self.bin     = bin
    self.options = options

  def start(self, daemon=True, **kwargs):
    if not self.running:
      thread = Thread(target=self._start_process, kwargs=kwargs)
      thread.setDaemon(daemon)
      thread.start()

  def stop(self):
    if self.process:
      try:
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
      except:
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])

      self.process = None
      self.emit('terminated')

  @property
  def running(self):
    return bool(self.process)

  @property
  def process_args(self):
    options = self.bin.split()

    for (key, value) in self.options.items():
      options.append('--{0}'.format(key.replace('_', '-')))

      if not isinstance(value, bool):
        options.append(str(value))

    return options

  def _start_process(self, **kwargs):
    try:
      kwargs['preexec_fn'] = os.setsid
    except:
      kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE

    input = None
    if 'stdin' in kwargs:
      input = kwargs['stdin']
      kwargs['stdin'] = subprocess.PIPE

    try:
      try:
        self.process = subprocess.Popen(self.process_args, **kwargs)
      except RuntimeError:
        kwargs.pop('preexec_fn', None)
        kwargs.pop('creationflags', None)
        self.process = subprocess.Popen(self.process_args, **kwargs)

      self.emit('started')

      stdout, stderr = self.process.communicate(input)

      if stderr:
        self.emit('error::subprocess', str(stderr))

      self.process = None
      self.emit('terminated')
    except OSError as error:
      self.process = None
      self.emit('error', str(error))
