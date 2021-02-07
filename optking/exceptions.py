import logging


# We don't catch this one internallyclass OptFail(Exception):
class OptError(Exception):
    def __init__(self, mesg="None given", err_type="Not specified"):
        optimize_log = logging.getLogger(__name__)
        optimize_log.critical("OptError: Optimization has failed.")
        self.mesg = mesg
        self.err_type = err_type
        # Exception.__init__(self, mesg)


class AlgError(Exception):
    # maybe generalize later def __init__(self, *args, **kwargs):
    def __init__(self, mesg="None given", newLinearBends=None):
        optimize_log = logging.getLogger(__name__)
        optimize_log.error("AlgError: Exception created.\n")
        if newLinearBends:
            optimize_log.error("AlgError: New bends detected.\n")
        self.linearBends = newLinearBends
        self.mesg = mesg


class IRCendReached(Exception):
    """Quit when we have found a minimum or completed the requested steps."""

    def __init__(self, mesg="None given"):
        optimize_log = logging.getLogger(__name__)
