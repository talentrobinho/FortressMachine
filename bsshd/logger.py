import logging
from conf import ReadConf
from logging.handlers import TimedRotatingFileHandler


config = ReadConf.config_dict()

class CreateLogger(object):
    ''' Setting root logger
    '''

    log_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'FATAL': logging.FATAL,
            'CRITICAL': logging.CRITICAL,
        }

    @classmethod
    def create_logger(cls):
        conf_log_level = config['SERVER_LOGLEVEL']
        set_log_level = cls.log_level[conf_log_level.upper()]
        set_log_path = config['SERVER_LOGFILE']

        ''' Does not specify a log name to increase the log output of paramiko '''
        logger = logging.getLogger()

        root_formatter = logging.Formatter(
                                            fmt='%(asctime)s [%(name)s] [%(module)s %(levelname)s] %(message)s',
                                            datefmt='%Y%m%d %H:%M:%S'
        )
        #console_handler = logging.StreamHandler()
        file_handler = TimedRotatingFileHandler(
                                                        filename=set_log_path,
                                                        when='D',
                                                        backupCount=10
                                                      )

        #for handler in [console_handler, file_handler]:
        for handler in [file_handler]:
            handler.setFormatter(root_formatter)
            logger.addHandler(handler)

        logger.setLevel(set_log_level)


#CreateLogger.create_logger()
