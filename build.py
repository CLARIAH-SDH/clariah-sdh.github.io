import markdown
import glob
from yaml import load
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('build', 'templates'))

extensions = ['markdown.extensions.tables','markdown.extensions.codehilite','markdown.extensions.headerid', 'markdown.extensions.attr_list']

with open('config.yaml','r') as config_file:
    config = load(config_file.read())

content = {}
for c in config['content'] :
    content_filename = 'content/{}.md'.format(c)
    with open(content_filename,'r') as content_file :
        content[c] = markdown.markdown(content_file.read().decode('utf-8'), extensions=extensions)

blogs = {}
for b in config['blogs']:
    blog = blogs[b] = []
    for post_filename in glob.glob('{}/*.md'.format(b)):
        with open(post_filename,'r') as post_file:
            post = markdown.markdown(post_file.read().decode('utf-8'), extensions=extensions)
            blog.append(post)

index = env.get_template('index.html')
index_rendered = index.render(content=content, blogs=blogs)

with open('index.html','w') as index_file:
    index_file.write(index_rendered.encode('utf-8'))
