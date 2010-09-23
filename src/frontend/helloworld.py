import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

class Greeting(db.Model) :
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler) :
    def get(self) :
        greetings = db.GqlQuery('SELECT * FROM Greeting '\
                                'ORDER BY date '\
                                'DESC LIMIT 10')

        self.response.out.write('<!doctype html>\n<html>\n\t<body>')
        for greeting in greetings :
            if greeting.author :
                name = '<strong>%s</strong>' % greeting.author.nickname()
            else :
                name = '<em>Anonymous</em>'
            self.response.out.write('<div>%s wrote:' % name)
            content = cgi.escape(greeting.content)
            self.response.out.write('<blockquote>%s</blockquote></div>' % content)

        self.response.out.write("""<form method="post" action="/sign">
    <div><textarea name="content" rows="3" cols="60"></textarea></div>
    <div><input type="submit" value="Sign Guestbook"></div>
</form>
</body>""")

class Guestbook(webapp.RequestHandler) :
    def post(self) :
        greeting = Greeting()

        if users.get_current_user() :
            greeting.author = users.get_current_user()
        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

pages = [
    ('/', MainPage),
    ('/sign', Guestbook),
]

application = webapp.WSGIApplication(pages, debug=True)

def main() :
    run_wsgi_app(application)

if __name__ == '__main__' :
    main()
