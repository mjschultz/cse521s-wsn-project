from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

red_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xffr\x9cRg\x00\x00\x00\x00IEND\xaeB`\x82'
yellow_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8\xff\x9f\xe1?\x00\x07\xfd\x02\xfe]\x91\xaa\xce\x00\x00\x00\x00IEND\xaeB`\x82'
green_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c`h`\xf8\x0f\x00\x02\x84\x01\x80\x01\x009g\x00\x00\x00\x00IEND\xaeB`\x82'

height = 15
total_width = 100

class Imager(webapp.RequestHandler) :
    def get(self, full_count, unknown_count, empty_count) :
        fc = int(full_count)
        uc = int(unknown_count)
        ec = int(empty_count)

        total = fc + uc + ec
        multiplier = 1.0 * total_width / total

        full_pos = int(round(fc * multiplier))
        unknown_pos = int(round(uc * multiplier))
        empty_pos = int(round(ec * multiplier))

        if full_pos < height :
            full_width = height
        else :
            full_width = full_pos

        if unknown_pos < height :
            unknown_width = height
        else :
            unknown_width = unknown_pos

        if empty_pos < height :
            empty_width = height
        else :
            empty_width = empty_pos

        full = images.resize(red_png, full_width, full_width, output_encoding=images.PNG)
        unknown = images.resize(yellow_png, unknown_width, unknown_width, output_encoding=images.PNG)
        empty = images.resize(green_png, empty_width, empty_width, output_encoding=images.PNG)

        full_in = (full, 0, 0, 1.0, images.TOP_LEFT)
        unknown_in = (unknown, full_pos, 0, 1.0, images.TOP_LEFT)
        empty_in = (empty, full_pos+unknown_pos, 0, 1.0, images.TOP_LEFT)
        inputs = (full_in, unknown_in, empty_in)

        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(images.composite(inputs, total_width, height))

class Test(webapp.RequestHandler) :
    def get(self, one) :
        self.response.out.write('one'+one)

pages = [
    ('/media/usage-(\d+)-(\d+)-(\d+).png', Imager),
]

application = webapp.WSGIApplication(pages, debug=True)

def main() :
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
