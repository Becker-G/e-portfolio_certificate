# coding=utf-8
HOSTNAME = 'localhost'
DATABASE = 'eportfolio'
USERNAME = 'admin'
PASSWORD = 'admin'
DB_URI = 'mysql://{}:{}@{}/{}'.format(
    USERNAME, PASSWORD, HOSTNAME, DATABASE)
