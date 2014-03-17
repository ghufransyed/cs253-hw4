import webapp2
from form import FormHandler
from form import SuccessHandler
from login import LoginHandler


app = webapp2.WSGIApplication([
    ('/signup', FormHandler),
    ('/success', SuccessHandler),
    ('/login', LoginHandler),
], debug=True)
