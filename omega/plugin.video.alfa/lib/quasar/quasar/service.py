import xbmc
import threading
from quasar.logger import log
from quasar.rpc import server_thread
from quasar.monitor import QuasarMonitor
from quasar.daemon import quasard_thread


def run():
    # Make sure the XBMC jsonrpc server is started.
    xbmc.startServer(xbmc.SERVER_JSONRPCSERVER, True)

    # Make the monitor
    monitor = QuasarMonitor()

    threads = [
        threading.Thread(target=server_thread),  # JSONRPC thread
        threading.Thread(target=quasard_thread, args=[monitor]),  # Quasard thread
    ]
    for t in threads:
        t.daemon = True
        t.start()

    # XBMC loop
    while not monitor.abortRequested():
        xbmc.sleep(1000)

    try:
        monitor.onAbortRequested()
    except:
        pass
    
    log.info("quasar: exiting quasard")
