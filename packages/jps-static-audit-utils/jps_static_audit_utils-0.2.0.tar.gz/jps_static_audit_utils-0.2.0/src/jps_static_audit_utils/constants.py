import re

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

PROGRAM_NAME = "perl-hardcoded-path-report"
PROGRAM_VERSION = "1.0.0"

TIMESTAMP_FMT = "%Y-%m-%d-%H%M%S"


# --------------------------------------------------------------------------- #
# Regexes
# --------------------------------------------------------------------------- #

ABS_PATH_RE = re.compile(r"""(['"])(\/(?:[^'"\s]+\/?)+)\1""")
REL_PATH_RE = re.compile(r"""(['"])(\.\.?\/[^'"\s]+)\1""")

URL_RE = re.compile(r"(https?|s3|gs|ftp)://")
ENV_RE = re.compile(r"\$ENV\{[^}]+\}")


