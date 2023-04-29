import argparse
import sys
import os
import platform

from robot.api import TestSuite
from robot.conf import RobotSettings
from robot.output import LOGGER, pyloggingconf
from robot.api import ResultWriter
from pathlib import Path
from termcolor import *
from .version import VERSION

ACTIONS = ['init', 'clean', 'run']
CONFIG_FILE_NAME = 'config.yaml'
CSV_DATA_FILE_NAME = 'TestCases.csv'
INTRO = '=' * 78


def print_qat_cli_intro(args):
    """Prints QAT Execution Intro."""
    os.system('cls' if os.name == 'nt' else 'clear')
    cprint(INTRO, 'green')
    cprint('Executing QATLibrary Tests', 'green')
    cprint(INTRO, 'green')
    print("Test Source      : %s" % args.file)
    print("Context Config   : %s" % args.config)
    print("Platform         : %s" % platform.system())
    print("Log Level        : %s" % args.loglevel)
    print("Output           : %s" % args.output)
    print("Report           : %s" % args.report)
    print("Log              : %s" % args.log)
    cprint(INTRO, 'green')


def colored_msg(msg, color=None):
    if os.name == 'nt':
        print(msg)
    else:
        cprint(msg, color)


def is_file(arg_value):
    if not Path(arg_value).is_file():
        raise argparse.ArgumentTypeError('File does not exist: ' + arg_value)
    return arg_value


def is_dir(arg_value):
    if not Path(arg_value).is_dir():
        raise argparse.ArgumentTypeError('Directory does not exist: ' + arg_value)
    return arg_value


def input_csv(arg_value):
    is_file(arg_value)
    if '.csv' not in arg_value:
        raise argparse.ArgumentTypeError('-f or --file value must be a .csv file')
    return arg_value


def _clean(target_dir):
    report_exts = ('.html', '.xml')
    target_files = os.listdir(target_dir)

    for file_name in target_files:
        if file_name.endswith(report_exts):
            print('Removing file: ', os.path.join(target_dir, file_name))
            os.remove(os.path.join(target_dir, file_name))
    colored_msg('Cleanup complete!', 'green')


def _init():
    _create_template_files()


def _create_template_files():
    import shutil
    import pkg_resources
    for f in os.listdir(pkg_resources.resource_filename('QATLibrary', 'templates')):
        if not Path(f).is_file():
            shutil.copy(pkg_resources.resource_filename('QATLibrary', f'templates/{f}'), f)
            colored_msg('==> QAT sample file created: ' + f, 'green')
        else:
            colored_msg('==> Skipping... File exists: ' + f, 'yellow')
    print(f"""
    You may run: 
        qat run -c {CONFIG_FILE_NAME} -f {CSV_DATA_FILE_NAME} """)


def _create_test_suite(args):
    print_qat_cli_intro(args)
    suite = TestSuite(name=args.file.split('/')[-1] + ' | ' + 'QAT ',
                      doc='Runs (Quick) API Tests from Input CSV Data')
    suite.resource.imports.library('QATLibrary')

    suite.setup.config(name='QAT Dynamic Tests Setup', args=[args.file, args.encoding])
    settings = RobotSettings(output=args.output,
                             report=args.report,
                             loglevel=args.loglevel,
                             log=args.log,
                             variablefile=args.config)

    with pyloggingconf.robot_handler_enabled(settings.log_level):
        result = suite.run(settings=settings)
        LOGGER.info("Tests execution ended. Statistics:\n%s"
                    % result.suite.stat_message)
        if settings.log or settings.report or settings.xunit:
            writer = ResultWriter(settings.output if settings.log
                                  else result)
            writer.write_results(settings.get_rebot_settings())

    if args.return_rc:
        sys.exit(result.return_code)


def main():
    parser = argparse.ArgumentParser(description='QAT (Quick API Test) Library CLI Interface')
    parser.add_argument('--version', action="version",
                        version=VERSION,
                        help='QAT library version')

    parser.add_argument('action', metavar='action', type=str,
                        choices=ACTIONS,
                        help='Action for QAT CLI. Valid choices: ' + str(ACTIONS))

    parser.add_argument('-c', '--config',
                        help='Config yaml file with required settings or variables. ',
                        required='run' in sys.argv, type=is_file)

    parser.add_argument('-f', '--file',
                        help='CSV File Input. Relative/absolute path accepted.',
                        required='run' in sys.argv, type=input_csv)

    parser.add_argument('-e', '--encoding',
                        help='Encoding for CSV Input File',
                        required=False, default='UTF-8', type=str)

    parser.add_argument('-L', '--loglevel',
                        help='Robot framework Log level',
                        default='INFO',
                        choices=['NONE', 'WARN', 'INFO', 'DEBUG', 'TRACE'],
                        required=False, type=str)

    parser.add_argument('-r', '--report',
                        default='report.html',
                        help='Output report file name',
                        required=False, type=str)

    parser.add_argument('-l', '--log',
                        default='log.html',
                        help='Output log file name',
                        required=False, type=str)

    parser.add_argument('-o', '--output',
                        default='output.xml',
                        help='Output xml file name',
                        required=False, type=str)

    parser.add_argument('-d', '--directory',
                        help='Target Directory for "init" or "clean". Default current directory.',
                        default=os.getcwd(),
                        required=False, type=is_dir)

    parser.add_argument('-rc', '--return_rc',
                        action='store_true',
                        help='Return error status code on test failures. Default False',
                        required=False)

    args = parser.parse_args()
    if args.action == 'clean':
        _clean(args.directory)

    if args.action == 'init':
        _init()

    if args.action == 'run':
        _create_test_suite(args)


if __name__ == '__main__':
    main()
