from svy.errors.base_errors import SvyError as SvyError

class SinglePSUError(SvyError):
    """Only one PSU in the stratum"""

class ProbError(SvyError):
    """Not a valid probability"""

class MethodError(SvyError):
    """Method not applicable"""

class CertaintyError(SvyError):
    """Method not applicable"""

class DimensionError(SvyError):
    """Method not applicable"""
