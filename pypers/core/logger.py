import logging
import json
import time


class PipeFormatter(logging.Formatter):
    """
    Custom formatter for more flexibility
    """
    max_width = 15
    def format(self, record):
        """
        Customized formatting (mainly to fix length of module name)
        """
        # Strip module name
        module_name = record.module[:self.max_width]
        mod_format = "[%%-%ds:%%03d]" % len(module_name)
        module_string = mod_format % (record.module[:self.max_width], record.lineno)
        return "%s %-20s %-8s %s" % (self.formatTime(record), module_string, record.levelname, record.msg)


class Logger(object):

    # Expose logging levels
    from logging import DEBUG,INFO,WARNING,ERROR,CRITICAL

    def __init__(self):
        """
        Standard configuration for the logging service
        """
        self.log = logging.getLogger(str(int(time.time())))
        self.log.setLevel(logging.DEBUG)

        self.formatter = PipeFormatter() 

        # Log to stdout too
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(logging.ERROR)
        streamhandler.setFormatter(self.formatter)
        self.log.addHandler(streamhandler)


    def add_file(self, logfile):
        """
        Add a alog file
        """
        # Log to file
        filehandler = logging.FileHandler(logfile, "w")
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(self.formatter)
        self.log.addHandler(filehandler)


    def get_log(self):
        """
        Return a log instance
        """
        return self.log

    def set_stdout_level(self, level):
        """
        Set the logging level
        """
        self.log.handlers[0].setLevel(level)

    def __del__(self):
        """
        Close all the file handlers
        """
        for handler in self.log.handlers:
            if str(type(handler)).find('StreamHandler'):
                handler.flush()
            else:
                handler.close()


logger = Logger()
