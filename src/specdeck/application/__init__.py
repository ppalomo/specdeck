"""The use cases: what Specdeck does, expressed as steps over the domain.

Each one declares what it needs from the outside world as a `Protocol` and receives an
implementation of it. This layer imports the domain and nothing below it, so a use case can
be driven by a fake and never knows whether it is being called from HTTP or from the
executable.
"""
