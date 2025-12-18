"""
CLI CONTRACT — DO NOT CHANGE WITHOUT BREAKING TESTS

This file defines the immutable surface of the XKID command-line interface.
Any change here MUST be accompanied by:
  - explicit version bump, OR
  - golden test updates

Null+1 policy (current hardening):
  - id.generate is the only public ID command
  - only the mount lens is permitted for id.generate
  - capability validation MUST happen before mount validation
"""

# Envelope schema
COMMAND_RESULT_SCHEMA = "xkid.CommandResult.v1"

# Canonical command names
CMD_LENS_LIST = "lens.list"
CMD_LENS_DESCRIBE = "lens.describe"
CMD_ID_GENERATE = "id.generate"

# Output schemas
SCHEMA_LENS_LIST = "xkid.LensList.v1"
SCHEMA_LENS_DESCRIBE = "xkid.LensDescribe.v1"
SCHEMA_LENS_OUTPUT = "xkid.LensOutput.v1"

# Option B: id.generate emits IdOutput (CLI promotes LensOutput -> IdOutput)
SCHEMA_ID_OUTPUT = "xkid.IdOutput.v1"

# Null+1 hardening
NULL_PLUS_ONE = True
NULL_PLUS_ONE_MOUNT_LENS = "oscillation"

# Output formats (CLI flags)
OUTPUT_FORMATS = {"json", "pretty", "raw"}
DEFAULT_OUTPUT_FORMAT = "json"
