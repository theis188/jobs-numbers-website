
from flask import Flask,render_template,send_from_directory,redirect,request
from database.database import route_build_page
import json
import os
import re

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

REDIRECTS = {
    'national-all-occupations':'national.html'
    }

STATIC_PAGES = {
    'about':'about.template',
    'contact':'contact.template',
}

def comma_format(num):
    try:
        num_int = int(num)
        ret = '{:,}'.format(num_int)
        return ret
    except ValueError:
        return num

def slugify(s):
    lower = s.lower()
    chunks = re.findall(r'[a-z]+',lower)
    return '-'.join(chunks)

@app.context_processor
def add_functions():
    return dict(
                    zip=zip,
                    comma_format=comma_format,
                    slugify=slugify,
                )

def redirecter(redirects):
    def decorator(fun):
        def wrapper(*args,**kwargs):
            try:
                if 'slug' in kwargs:
                    slug = kwargs['slug']
                else:
                    slug = args[0]
            except KeyError:
                return fun(*args,**kwargs)
            if slug in redirects:
                new_destination = redirects[slug]
                print(slug,'redirecting to',new_destination)
                return redirect(request.host_url + new_destination, code=301)
            else:
                return fun(*args,**kwargs)
        return wrapper
    return decorator


def static_pages(static_pages_dict):
    def decorator(fun):
        def wrapper(*args,**kwargs):
            try:
                if 'slug' in kwargs:
                    slug = kwargs['slug']
                else:
                    slug = args[0]
            except KeyError:
                return fun(*args,**kwargs)
            if slug in static_pages_dict:
                destination_template = static_pages_dict[slug]
                return render_template(destination_template)
            else:
                return fun(*args,**kwargs)
        return wrapper
    return decorator


@app.route('/js/<js_file>')
def js(js_file):
    return send_from_directory(os.path.join(app.root_path, 'static/js'),
                              js_file , mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/<slug>.html')
@redirecter(REDIRECTS)
@static_pages(STATIC_PAGES)
def route_url(slug):
    print('slug',slug)
    full_slug = slug+'.html'
    page = route_build_page(full_slug)
    type_str = page['type']
    print(type_str)
    route_map = {
        'home':'home.template',
        'state':'state.template',
        'location':'location.template',
        'location_occ_group':'location_occ_group.template',
        #'occupation':
    }
    template = route_map[type_str]
    return render_template(template, **page)

@app.route('/')
def home():
    page = route_build_page('')
    return render_template('home.template',**page)


@app.route('/sitemaps/sitemap.xml')
def route_sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')

@app.route('/robots.txt')
def route_robots():
    return send_from_directory(app.static_folder, 'robots.txt')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
