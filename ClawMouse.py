import argparse
import sys

from loguru import logger

from KeymouseGo import main, single_run
from mcp_server import main as mcp_main


if __name__ == '__main__':
    logger.debug(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('scripts', help='Path for the scripts', type=str, nargs='*')
    parser.add_argument('-rt', '--runtimes', help='Run times for the script', type=int, default=1)
    parser.add_argument('--mcp-server', action='store_true')
    parser.add_argument('--transport', default='stdio', choices=['stdio', 'http'])
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    if args.mcp_server:
        mcp_args = ['--transport', args.transport]
        if args.transport == 'http':
            mcp_args.extend(['--host', args.host, '--port', str(args.port)])
        mcp_main(mcp_args)
    elif len(args.scripts) > 0:
        single_run(args.scripts, args.runtimes)
    else:
        main()
