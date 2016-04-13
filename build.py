import markdown
import glob
import time
import sys
import SimpleHTTPServer
import SocketServer
import threading

from yaml import load
from jinja2 import Environment, PackageLoader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


env = Environment(loader=PackageLoader('build', 'templates'))

extensions = ['markdown.extensions.tables', 'markdown.extensions.codehilite',
              'markdown.extensions.headerid', 'markdown.extensions.attr_list']


class BuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if (isinstance(event, FileModifiedEvent) and
                (event.src_path.endswith('.md') or
                 event.src_path.endswith('.html') or
                 event.src_path.endswith('.yaml') )):
            if event.src_path.endswith('./index.html'):
                print "Not rebuilding index.html"
                return

            print("File change detected, rebuilding...")
            build()
            print("Done")


def build():
    with open('config.yaml', 'r') as config_file:
        config = load(config_file.read())

    content = {}
    for c in config['content']:
        content_filename = 'content/{}.md'.format(c)
        with open(content_filename, 'r') as content_file:
            content[c] = markdown.markdown(content_file.read().decode('utf-8'), extensions=extensions)

    blogs = {}
    for b in config['blogs']:
        blog = blogs[b] = []
        for post_filename in glob.glob('{}/*.yaml'.format(b)):
            with open(post_filename, 'r') as post_file:
                post = load(post_file.read().decode('utf-8'))
                # Render the markdown of the text, if applicable
                if 'text' in post:
                    post['text'] = markdown.markdown(post['text'], extensions=extensions)
                blog.append(post)

    index = env.get_template('index.html')
    index_rendered = index.render(content=content, blogs=blogs)

    with open('index.html', 'w') as index_file:
        index_file.write(index_rendered.encode('utf-8'))


if __name__ == "__main__":
    # First build from sources
    build()

    # Start the HTTP Server
    PORT = 8000

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "Serving at port", PORT
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True

    try:
        thread.start()
    except KeyboardInterrupt:
        httpd.shutdown()
        sys.exit(0)

    # Initialize a watchdog eventhandler
    event_handler = BuildHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        httpd.shutdown()
        observer.stop()
    observer.join()
