import xbmc
import xbmcaddon
from app import server_run
import threading

# inicia servidor
threading.Thread(target=server_run, daemon=True).start()

# mantém o addon vivo
monitor = xbmc.Monitor()
while not monitor.abortRequested():
    if monitor.waitForAbort(1):
        break

# encerra o servidor antes de sair
print("Servidor Flask encerrado.")