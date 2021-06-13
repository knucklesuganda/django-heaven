from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from services.base import BaseService


class UserService(BaseService):
    """ That is the service for the User model of your project """
    model = get_user_model()

    def model_create_method(self) -> callable:
        return self.model.create_user

    def create_superuser(self, *args, **kwargs):
        """
        Use that to create superuser model. We use monkey-patching which is not a great idea,
        but you will not typically find yourself creating a lot of superusers with UserService() in the production.
        """
        old_model_create = self.model_create_method
        self.model_create_method = lambda: self.model.create_superuser

        result = self.create(*args, **kwargs)
        self.model_create_method = old_model_create
        return result

    def set_password(self, **kwargs):
        """ Use that function to set new user password """
        return self.update(
            instance=self._get_instance_from_kwargs(kwargs),
            password=make_password(kwargs.get('password') or kwargs.get('raw_password'))
        )
