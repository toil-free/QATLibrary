from robot.api import TestSuite
from robot.conf import RobotSettings
from robot.output import LOGGER, pyloggingconf
from robot.api import ResultWriter
from pathlib import Path
import argparse
from .version import VERSION


def input_csv(arg_value):
    if '.csv' not in arg_value:
        print('in csv validation')
        raise argparse.ArgumentTypeError('-f or --file value must be a .csv file')
    if not Path(arg_value).is_file():
        print('in file validation')
        raise argparse.ArgumentTypeError('csv input file does not exist: ' + arg_value)
    return arg_value


def main():
    parser = argparse.ArgumentParser(description='QAT (Quick API Test) Library CLI Interface')
    parser.add_argument('--version', action="version",
                        version=VERSION,
                        help='QAT library version')
    parser.add_argument('-f', '--file',
                        help='CSV File Input. Relative/absolute path accepted',
                        required=True, type=input_csv)

    parser.add_argument('-c', '--config',
                        help='Config yaml file with required settings',
                        required=True, type=str)

    parser.add_argument('-e', '--encoding',
                        help='Encoding for CSV Input File',
                        required=False,
                        default='UTF-8',
                        type=str)

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

    args = parser.parse_args()
    create_test_suite(args)


# figure out test suite name
def create_test_suite(args):
    suite = TestSuite(name=args.file.split('/')[-1] + ' | ' + 'QAT ',
                      doc='Runs (Quick) API Tests from Input CSV Data')
    suite.resource.imports.library('QATLibrary')

    suite.keywords.create('QAT Dynamic Tests Setup', args=[args.file, args.encoding], type='setup')
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


if __name__ == '__main__':
    main()
