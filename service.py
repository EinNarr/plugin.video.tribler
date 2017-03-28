import time
# import xbmc
import sys
import signal
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname('__file__')), 'tribler'))

from twisted.internet import reactor

from Tribler.Core.Session import Session
from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig

def start_tribler_core():
    """
    This method is invoked by multiprocessing when the Tribler core is started and will start a Tribler session.
    Note that there is no direct communication between the GUI process and the core: all communication is performed
    through the HTTP API.
    """
    from twisted.internet import reactor

    def on_tribler_shutdown(_):
        reactor.stop()

    def shutdown(session, *_):
        logging.info("Stopping Tribler core")
        session.shutdown().addCallback(on_tribler_shutdown)

    def start_tribler():
        config = SessionStartupConfig().load()
        config.set_http_api_port(8085)
        config.set_http_api_enabled(True)

        # Check if we are already running a Tribler instance
        process_checker = ProcessChecker()
        if process_checker.already_running:
            return

        session = Session(config)

        signal.signal(signal.SIGTERM, lambda signum, stack: shutdown(session, signum, stack))
        session.start()
    reactor.callWhenRunning(start_tribler)
    reactor.run()

if __name__ == '__main__':
	# from multiprocessing import Process
	# process=Process(target=start_tribler_core)
	# process.start()
	# if reactor.running:

	start_tribler_core()
	# while not monitor.abortRequested():
	# 	pass
	# import requests
	# r = requests.put("http://localhost:8085/shutdown")
	