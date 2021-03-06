from controller import Controller
from controller import Playlist
from controller import Layout
from server.server import run_server
import argparse
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)-15s | %(name)-12s (%(levelname)s): %(message)s'
logger = logging.getLogger('run_show')

def main():
	parser = argparse.ArgumentParser(description='Run the disco dance floor')
	parser.add_argument(
		'--network',
		dest='networkdriver',
		default=False,
		action='store_true',
		help='Starts the network driver (default = false)'
	)
	parser.add_argument(
		'--processor',
		dest='processor_name',
		default=None,
		help='Sets the LED processor to generate each frame of light data'
	)
	parser.add_argument(
		'--devserver',
		dest='devserver',
		default=False,
		action='store_true',
		help='Run a dev server'
	)
	parser.add_argument(
		'--no-opc-input',
		dest='opc_input',
		action='store_false',
		help='Turn off keyboard input handling'
	)
	parser.add_argument(
		'--opc-input',
		dest='opc_input',
		action='store_true',
		help='Turn on keyboard input handling'
	)
	parser.add_argument(
		'--verbose',
		dest='verbose',
		action='store_true',
		help='Enable verbose logging'
	)
	parser.add_argument(
		'--server_port',
		dest='server_port',
		type=int,
		help='Web server port; -1 to disable.'
	)
	parser.add_argument(
		'--network_port',
		dest='network_port',
		type=int,
		help='Network server port;',
		default=50999
	)
	parser.add_argument(
		'--noconsole',
		dest='noconsole',
		action='store_true',
		help='Disable logging to console',
		default=False,
	)
	parser.set_defaults(opc_input=True, server_port=1977)
	args = parser.parse_args()

	log_level = logging.DEBUG if args.verbose else logging.INFO
	logging.getLogger('').setLevel(log_level)
	#define a Handler which writes INFO messages or higher to the sys.stderr
	formatter = logging.Formatter(LOG_FORMAT)

	if (not args.noconsole):
		console = logging.StreamHandler(stream=sys.stdout)
		console.setLevel(log_level)
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)

	handler = RotatingFileHandler('floor.log',maxBytes = 100000000,backupCount = 5)
	handler.setFormatter(formatter)
	handler.setLevel(log_level)
	logging.getLogger('').addHandler(handler)

	logging.getLogger('').info("Start")
	logger.info("Start")
	
	config_dir = get_config_dir()
	playlist = Playlist(config_dir, args.processor_name)
	layout = Layout(config_dir)

	show = Controller(playlist)
	if (args.devserver):
		show.add_driver('devserver', {
			"opc_input": args.opc_input,
			"layout": layout
		})
	
	if (args.networkdriver):
		show.add_driver('network', {
			"opc_input": args.opc_input,
			"layout": layout,
			"network_port" : args.network_port
		})

	if args.server_port >= 0:
		run_server(show, port=args.server_port)

	try:
		show.run()
	except KeyboardInterrupt:
		sys.exit(0)


def get_config_dir():
	script_dir = os.path.dirname(os.path.realpath(__file__))
	return script_dir + "/config"

main()
