import re
import MySQLdb.cursors
from flask_mysqldb import MySQL
from passlib.context import CryptContext
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import os

static_dir = os.path.abspath('static')
template_dir = os.path.abspath('templates')

app = Flask(__name__ , static_folder = static_dir, template_folder = template_dir)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'vcby3qlzlT'
app.config['MYSQL_PASSWORD'] = 'fNYUUHSa0M'
app.config['MYSQL_DB'] = 'vcby3qlzlT'

mysql = MySQL(app)

context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=50000
)
