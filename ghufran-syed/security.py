import hmac
import random
import string
import hashlib


# Implement the hash_str function to use HMAC and our SECRET instead of md5
SECRET = 'imsosecret'


def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Implement the function valid_pw() that returns True if a user's password
# matches its hash. You will need to modify make_pw_hash.


def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)


def valid_pw(name, pw, h):
    test_hash = hashlib.sha256(name + pw + h.split('|')[-1]).hexdigest()
    # have to extract salt from h and combine with name and pw before sending
    # to hashlib.sha256...
    return test_hash == h.split('|')[0]  # comparing hash of test_data
    # with 'original' (given) hash
