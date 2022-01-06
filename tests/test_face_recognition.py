import os
import sys

workspace = os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)
sys.path.append(workspace)

from app import 