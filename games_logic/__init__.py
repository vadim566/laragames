from flask import render_template, request, flash, redirect, url_for, send_from_directory

from SVN.trunk.Code.Python import lara_utils
from config.config import mypath, slash_clean
from db.db import tbl_game4
from functions.functions import dirinDir
import random

from lara_games_app import db


