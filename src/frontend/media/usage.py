from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

red_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xffr\x9cRg\x00\x00\x00\x00IEND\xaeB`\x82'
yellow_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c\xf8\xff\x9f\xe1?\x00\x07\xfd\x02\xfe]\x91\xaa\xce\x00\x00\x00\x00IEND\xaeB`\x82'
green_png = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDAT\x08\xd7c`h`\xf8\x0f\x00\x02\x84\x01\x80\x01\x009g\x00\x00\x00\x00IEND\xaeB`\x82'

height = 15
total_width = 100

class Imager(webapp.RequestHandler) :
    def get(self, green_count, yellow_count, red_count) :
        gc = int(green_count)
        yc = int(yellow_count)
        rc = int(red_count)

        total = gc + yc + rc
        multiplier = 1.0 * total_width / total

        green_pos = int(round(gc * multiplier))
        yellow_pos = int(round(yc * multiplier))
        red_pos = int(round(rc * multiplier))

        if green_pos < height :
            green_width = height
        else :
            green_width = green_pos

        if yellow_pos < height :
            yellow_width = height
        else :
            yellow_width = yellow_pos

        if red_pos < height :
            red_width = height
        else :
            red_width = red_pos

        red = images.resize(red_png, red_width, red_width, output_encoding=images.PNG)
        yellow = images.resize(yellow_png, yellow_width, yellow_width, output_encoding=images.PNG)
        green = images.resize(green_png, green_width, green_width, output_encoding=images.PNG)

        red_in = (red, green_pos+yellow_pos, 0, 1.0, images.TOP_LEFT)
        yellow_in = (yellow, green_pos, 0, 1.0, images.TOP_LEFT)
        green_in = (green, 0, 0, 1.0, images.TOP_LEFT)
        inputs = (green_in, yellow_in, red_in)

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
