import xbmc
import paths

import sys
import os
import threading

from twisted.internet import reactor

from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig


class server(threading.Thread):

    def shutdown(self, *_):
        xbmc.log("Stopping Tribler core")
        self.session.shutdown()
        reactor.stop()

    def _start_tribler(self):
        config = SessionStartupConfig().load()
        config.set_http_api_port(8085)
        config.set_http_api_enabled(True)

        # Check if we are already running a Tribler instance
        process_checker = ProcessChecker()
        if process_checker.already_running:
            return

        session = Session(config)
        self.session = session

        #signal.signal(signal.SIGTERM, lambda signum, stack: self.shutdown(session, signum, stack))
        session.start()
        xbmc.log("Started Tribler core")

    def run(self):
        xbmc.log("Starting Tribler core")
        reactor.callWhenRunning(self._start_tribler)
        reactor.run(installSignalHandlers=0)
        xbmc.log("Stopped Tribler core")


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    core = server()
    core.start()

    while not monitor.abortRequested():
        if monitor.waitForAbort(5):
            core.shutdown()
            break
core.join()
