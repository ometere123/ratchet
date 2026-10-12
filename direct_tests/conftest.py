"""Direct Mode compatibility for the pinned runner on Windows.

genlayer-test 0.29.0 replaces fd 0 with an open temporary file while loading a
contract, then unlinks that file in the same call. Windows correctly rejects
unlinking an open file. The runner has already installed the message stream by
that point, so retaining the file until fd 0 is replaced is safe for these
tests. This shim is test-only and does not alter contract/runtime behavior.
"""

import os

from gltest.direct import loader


_original_inject = loader._inject_message_to_fd0


def _windows_safe_inject(vm):
    try:
        return _original_inject(vm)
    except PermissionError:
        if os.name != "nt":
            raise
        # The original helper completed os.dup2 before failing at os.unlink.
        # fd 0 now contains the encoded GenLayer message and is consumed by
        # the SDK during module import; keep the temporary file until then.
        return None


loader._inject_message_to_fd0 = _windows_safe_inject
