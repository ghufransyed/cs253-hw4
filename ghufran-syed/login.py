import webapp2
import jinja2
import os
import datetime
import security
from form import User


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


login_params = {"username": "",
                "username_err": "",
                "password_err": "",
                }


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class LoginHandler(Handler):
    def get(self):
        self.render('login.html', **login_params)

    def post(self):
        username_test = self.request.get('username')
        password_test = self.request.get('password')

        user_query = User.all()
        user_query_f = user_query.filter('user_id =',
                                         security.make_secure_val
                                         (username_test))
        user_query_r = user_query_f.fetch(1)
        if user_query_r:
            user_query_r = user_query_f.fetch(1)[0]
            #self.write("user_query_r is: %r" % user_query_r.password)
            password_ref = user_query_r.password
            if security.valid_pw(username_test,
                                 password_test,
                                 password_ref):
                self.write("user_query_r is: %r" % user_query_r.password)
                self.success(username_test)
            else:
                login_params["username"] = username_test
                login_params["username_err"] = ""
                login_params["password_err"] = "That password is not correct"
                self.redirect('/login')

        else:
            login_params["username"] = username_test
            login_params["username_err"] = "That username is not correct"
            login_params["password_err"] = ""
            self.redirect('/login')

    def success(self, username_p):
            user_id_hash = security.make_secure_val(username_p)
            self.response.set_cookie('user_id',
                                     value=user_id_hash,
                                     expires=(datetime.datetime.today() +
                                              datetime.timedelta(weeks=520)),
                                     path='/',
                                     # domain='ghufran-syed.appspot.com',
                                     # secure=True,
                                     # httponly=False
                                     )
            # changed below when autograder would not work
            # turned out to not be relevant (both the code above
            #and the code below work fine, probably best to use function
            # above)
#             self.response.headers.add_header('Set-Cookie',
#                                              'user_id=%s;Path=/'
#                                              % str(user_id_hash))
            self.redirect("/success")


class SuccessHandler(Handler):
    def get(self):
        user_id_check = (security.check_secure_val
                         (self.request.cookies.get('user_id')))
        if user_id_check:
            login_params["username"] = user_id_check
            self.render('success.html', **login_params)
        else:
            self.redirect("/signup")
