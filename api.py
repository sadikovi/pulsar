import setpath
from google.appengine.api import users
import analytics.analyticsws as ws
import webapp2


class Message(object):
    pass
Message.NotAuthenticated = "Snap, you are not authenticated!"
Message.UnexpectedError = "Bugger, unexpected error..."


# pulsar api
class API_Datasets(webapp2.RequestHandler):
    def get(self):
        res = ""
        try:
            user = users.get_current_user()
            if user and ws.isUserInEmaillist(user.email()):
                res = ws.getAllDatasets()
            else:
                res = ws.generateErrorMessage(Message.NotAuthenticated)
                self.response.set_status(401)
            self.response.write(res)
        except:
            error = ws._generateErrorMessage(Message.UnexpectedError)
            self.response.set_status(400)
            self.response.write(error)

class API_Query(webapp2.RequestHandler):
    def get(self):
        res = ""
        try:
            user = users.get_current_user()
            if user and ws.isUserInEmaillist(user.email()):
                query = self.request.get('q') or ""
                datasetId = str(self.request.get('d') or "")
                res = ws.requestData(datasetId, query)
            else:
                res = ws.generateErrorMessage(Message.NotAuthenticated)
                self.response.set_status(401)
            self.response.write(res)
        except:
            error = ws.generateErrorMessage(Message.UnexpectedError)
            self.response.set_status(400)
            self.response.write(error)

class API_Login(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/'))

class API_Logout(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

application = webapp2.WSGIApplication([
    ('/datasets', API_Datasets),
    ('/logout', API_Logout),
    ('/login', API_Login),
    ('/query', API_Query)
], debug=True)
