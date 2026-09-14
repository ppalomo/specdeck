"""Reading one markdown artifact into structure, and nothing else.

Pure functions from text to domain models. They take the text and the name of the file it
came from — never a path to open — which is what keeps the domain free of the disk and lets
every awkward document be tested without one existing anywhere.

They exist to render fast. What is valid, and what state an artifact is in, is decided by
the OpenSpec CLI and never here.
"""
