# Import modules from parent folder
import os
import sys
parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_folder)

from bot import Bot

bot_icnstance = Bot ()
bot_icnstance.unfollow ()