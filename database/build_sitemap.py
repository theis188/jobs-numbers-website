from flask import Flask,render_template,send_from_directory,redirect,request
from database import route_build_page
import os

##
dirpath = os.path.dirname(os.path.abspath(__file__))
templates_folder = os.path.join( dirpath, '../templates' )

_sitemap_path = os.path.join( dirpath, '../static/sitemap.xml' )
##

app = Flask(__name__, template_folder=templates_folder)

def build_sitemap():
    page = route_build_page('sitemap')
    with app.app_context():
        file_text = render_template('sitemap.template', **page)
    with open(_sitemap_path,'w') as f:
        f.write(file_text)

if __name__ == '__main__':
    build_sitemap()