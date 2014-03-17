import webapp2
import jinja2
import os
import re
import datetime
import security
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


form_params = {"username": "",
               "username_err": "",
               "password_1_err": "",
               "password_2_err": "",
               "email": "",
               "email_err": ""}


class User(db.Model):
    user_id = db.StringProperty()
    password = db.StringProperty()
    email = db.EmailProperty()


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class FormHandler(Handler):
    def get(self):
        self.render('form.html', **form_params)

    def post(self):
        username = self.request.get('username')
        password_1 = self.request.get('password')
        password_2 = self.request.get('verify')
        email = self.request.get('email')

        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        PASSWORD_RE = re.compile(r"^.{3,20}$")
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

        # error checking
        username_err = ""
        password_1_err = ""
        password_2_err = ""
        email_err = ""

        if USER_RE.match(username) is None:
            username_err = "That is not a valid username"
        if PASSWORD_RE.match(password_1) is None:
            password_1_err = "That is not a valid password"
        if password_1 != password_2:
            password_2_err = "The two passwords do not match"
        if email:
            if EMAIL_RE.match(email) is None:
                email_err = "That is not a valid email address"
            else:
                email_err = ""

        # check if any items are invalid
        if email:
            valid = (USER_RE.match(username) and
                     PASSWORD_RE.match(password_1) and
                     (password_1 == password_2) and
                     EMAIL_RE.match(email))
        else:
            valid = (USER_RE.match(username) and
                     PASSWORD_RE.match(password_1) and
                     (password_1 == password_2))
        if valid:
            user_id_hash = security.make_secure_val(username)
            self.response.set_cookie('user_id',
                                     value=user_id_hash,
                                     expires=(datetime.datetime.today() +
                                              datetime.timedelta(weeks=520)),
                                     path='/',
                                     # domain='ghufran-syed.appspot.com',
                                     # secure=True,
                                     # httponly=False
                                     )

            user_obj = User()
            user_obj.user_id = user_id_hash
            user_obj.password = security.make_pw_hash(username,
                                                      password_1)
            if email:
                user_obj.email = email

            user_obj.put()

            # changed below when autograder would not work
            # turned out to not be relevant (both the code above
            #and the code below work fine, probably best to use function
            # above)
#             self.response.headers.add_header('Set-Cookie',
#                                              'user_id=%s;Path=/'
#                                              % str(user_id_hash))

            self.redirect("/success")
            # self.write("That all looks good!")
            # success page redirect goes here
            # old redirect below
            #self.redirect("/success?username={username}".format(**locals()))
        else:
            form_params["username"] = username
            form_params["email"] = email
            form_params["username_err"] = username_err
            form_params["password_1_err"] = password_1_err
            form_params["password_2_err"] = password_2_err
            form_params["email_err"] = email_err

            self.render("form.html", **form_params)
            #return page


class SuccessHandler(Handler):
    def get(self):
        user_id_check = (security.check_secure_val
                         (self.request.cookies.get('user_id')))
        if user_id_check:
            form_params["username"] = user_id_check
            self.render('success.html', **form_params)
        else:
            self.redirect("/signup")
