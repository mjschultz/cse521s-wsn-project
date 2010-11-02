import model
import views
import controller

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

pages = [
    ('/', views.MainPage),
    ('/lot/?', views.LotPage),
    ('/lot/([A-Za-z0-9-_]+)(/.*)?', views.LotHandler),
]

application = webapp.WSGIApplication(pages, debug=True)

def main() :
    run_wsgi_app(application)

if __name__ == '__main__' :
    main()