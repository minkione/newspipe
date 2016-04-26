from flask import request
from flask.ext.login import current_user
from flask.ext.restless import ProcessingException
from werkzeug.exceptions import NotFound
from web.controllers import ArticleController, UserController
from web.views.common import login_user_bundle

url_prefix = '/api/v3'

def auth_func(*args, **kw):
    if request.authorization:
        ucontr = UserController()
        try:
            user = ucontr.get(nickname=request.authorization.username)
        except NotFound:
            raise ProcessingException("Couldn't authenticate your user",
                                        code=401)
        if not ucontr.check_password(user, request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user",
                                        code=401)
        if not user.is_active:
            raise ProcessingException("User is desactivated", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)

class AbstractProcessor():

    def is_authorized(self, user, obj):
        return user.id == obj.user_id

    def get_single_preprocessor(self, instance_id=None, **kw):
        # Check if the user is authorized to modify the specified
        # instance of the model.
        pass

    def get_many_preprocessor(self, search_params=None, **kw):
        """Accepts a single argument, `search_params`, which is a dictionary
        containing the search parameters for the request.
        """
        filt = dict(name="user_id",
                    op="eq",
                    val=current_user.id)

        # Check if there are any filters there already.
        if "filters" not in search_params:
          search_params["filters"] = []

        search_params["filters"].append(filt)

    def post_put_preprocessor(self, data=None, **kw):
        pass

    def delete_preprocessor(self, instance_id=None, **kw):
        pass