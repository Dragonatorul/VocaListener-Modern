"""Compatibility for the pinned MFA 3.3.8 Windows executable probe."""
import sys


def configure_mfa():
    if sys.platform != "win32":
        return
    import montreal_forced_aligner.utils as utils
    original = utils.thirdparty_binary

    def executable_path(name):
        # MFA adds shell quotes, then passes this value in a subprocess argv list.
        # CreateProcess must receive the unquoted filename; Python quotes argv.
        path = original(name)
        if path.startswith('"') and path.endswith('"'):
            return path[1:-1]
        return path

    utils.thirdparty_binary = executable_path
