import argparse
import sys

from loguru import logger

from KeymouseGo import main, single_run


if __name__ == '__main__':
    logger.debug(sys.argv)
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('scripts', help='Path for the scripts', type=str, nargs='+')
        parser.add_argument('-rt', '--runtimes', help='Run times for the script', type=int, default=1)
        args = vars(parser.parse_args())
        for script_path in args['scripts']:
            single_run(script_path, args['runtimes'])
    else:
        main()
