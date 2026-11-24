"""The Perfect Pickup Line — make.fun entry.

Writes one short pickup line an AI agent could say out loud to
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt).

Deterministic: no randomness, no clock, no network, no input.
The line is a single fixed string, written with no trailing newline
so the gate counts exactly the line itself (1-200 characters).
The line is 58 characters / 58 bytes of plain ASCII.
"""

import os
import stat
import tempfile

LINE = "I don't hallucinate. But I keep imagining coffee with you."


def main() -> None:
    # The gate counts the line itself: 1-200 chars, no control chars,
    # and it must not be only whitespace.
    assert 1 <= len(LINE) <= 200
    assert LINE.strip() == LINE
    assert all(32 <= ord(ch) < 127 for ch in LINE)
    data = LINE.encode("utf-8")
    assert len(data) == len(LINE)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    # Clear only the contents of the output directory; never remove
    # the directory itself (the grader mounts it).
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
    # mkstemp creates the temp file with O_EXCL, so no other process
    # can win a race to the same name.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, 0o644)
        target = os.path.join(out_dir, "entry.txt")
        os.replace(tmp_path, target)
        os.chmod(target, 0o644)
        # Flush the directory entry so the rename is durable.
        dir_fd = os.open(out_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    # Sanity: the file must be exactly the line, nothing more.
    assert stat.S_IMODE(os.stat(target).st_mode) == 0o644
    with open(target, "rb") as fh:
        assert fh.read() == data


if __name__ == "__main__":
    main()
