""" This module defines Log method for the project"""

import logging
import traceback


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def exception(self, e: Exception, *args, **kwargs):
        # extract and log exception info
        LOG.error(e.__cause__)
        # Get the current traceback stack
        tb = traceback.extract_tb(e.__traceback__)
        # Get the last traceback object (the one where the exception occurred)
        last_tb = tb[-1]
        # Extract the filename, line number, and line content
        filename, line_number, function_name, text = last_tb
        # Print the cause of the exception and the line where it occurred
        self.debug("An exception occurred: %s", e)
        self.debug(f"Cause: {e.__cause__}")
        self.debug(f"File: {filename}, line {line_number}, in {function_name}")
        self.debug(f"Code: {text}")

    def enableDebug(self):
        self.setLevel(logging.DEBUG)

    def disableDebug(self):
        self.setLevel(logging.INFO)


def setup_logger():
    logger_name = "backend"
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # because a new handler was created and added to the logger,
    # propagate needs to be set to false to log the message only once
    logger.propagate = False

    return logger


LOG = setup_logger()
