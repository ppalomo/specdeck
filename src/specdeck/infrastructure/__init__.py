"""The outside world: the disk, subprocesses and the one file Specdeck writes.

Implements the ports the use cases declare. Everything that can fail because the machine is
what it is — a path that vanished, a binary that is not installed, a command that hangs —
is dealt with here and turned into something the domain can describe.
"""
