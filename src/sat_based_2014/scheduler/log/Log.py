# scheduler/log/log.py

import logging

# Import VariableFactory from your encoding package.
from ..encoding.VariableFactory import VariableFactory

class Log:
    # Class-level variables (mimicking Java static fields)
    logger = logging.getLogger("Log")
    debug = True
    log_path = None
    variable_factory = VariableFactory.get_variable_factory()

    @classmethod
    def d(cls, arg, log_msg=None):
        """
        Debug logging.
        
        Overloaded behavior:
         - If called as d(log_method, log_msg): if log_method.get_log_status() is True, then logs log_msg.
         - If called as d(log_msg): logs the message if debug is True.
        """
        if log_msg is not None:
            # Assume arg is a LogMethod instance (or similar) with a get_log_status() method.
            if arg.get_log_status():
                cls.d(log_msg)
        else:
            if cls.debug:
                cls.logger.debug(arg)

    @classmethod
    def i(cls, log_msg):
        """Logs an informational message."""
        cls.logger.info(log_msg)

    @classmethod
    def clause_to_string(cls, clause):
        """
        Converts a clause (an iterable of integers) into a string.
        Each integer is converted using the variable factory's get_string_from_id method.
        If the resulting string is "0", that variable is skipped.
        """
        result = ""
        for var in clause:
            var_str = cls.variable_factory.get_string_from_id(var)
            if var_str != "0":
                result += var_str + " "
        return result.strip()

    @classmethod
    def write_log(cls, log_msg):
        """
        Appends the given log message to the file specified by log_path.
        """
        if cls.log_path is None:
            return
        try:
            with open(cls.log_path, "a") as f:
                f.write(log_msg + "\n")
        except IOError as e:
            print(e)

    @classmethod
    def set_log_path(cls, path):
        """Sets the log file path."""
        cls.log_path = path
