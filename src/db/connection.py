import logging
import streamlit as st
import pymysql
from pymysql.cursors import DictCursor
from config.settings import get_db_settings
import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

def get_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'ItsAllGoodMan'),
        cursorclass=pymysql.cursors.DictCursor
    )