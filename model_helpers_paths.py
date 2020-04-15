
import os
import sys

try:
  from sys import _MEIPASS
  MODEL_HELPERS_SCRIPTS_ROOT_PATH = _MEIPASS
  MODEL_HELPERS_APP_ROOT_PATH = os.path.dirname(os.path.realpath(sys.executable))
  IS_RUNNING_FROM_SOURCE = False
except ImportError:
  MODEL_HELPERS_SCRIPTS_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
  MODEL_HELPERS_APP_ROOT_PATH = MODEL_HELPERS_SCRIPTS_ROOT_PATH
  IS_RUNNING_FROM_SOURCE = True

WWRANDO_PATH = os.path.join(MODEL_HELPERS_SCRIPTS_ROOT_PATH, "wwrando")
SUPERBMD_PATH = os.path.join(MODEL_HELPERS_APP_ROOT_PATH, "SuperBMD", "SuperBMD.exe")
