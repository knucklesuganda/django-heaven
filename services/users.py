from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from services.services import Service
from services.decorators import ServiceFunctionDecorator, service_function_for_write


class UserService(Service):
    """ That is the service for the User model of your project """
    model = get_user_model()

    def model_create_method(self) -> callable:
        return self.model.create_user

    @service_function_for_write
    @ServiceFunctionDecorator()
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

    @service_function_for_write
    @ServiceFunctionDecorator()
    def set_password(self, **kwargs):
        """ Use that function to set new user password """
        return self.update(
            instance=self.get_argument_from_kwargs(kwargs=kwargs, argument='instance'),
            password=make_password(kwargs.get('password') or kwargs.get('raw_password'))
        )
