"""
That file shows you how to create your own service for your model.
I will not split everything into different files for the simplicity, but you should probably do that.
"""

from django.db import models
from django.http import HttpResponse
from django.views import View

from services.base import Service     # You will use 'import django_heaven.services'
from services.decorators import ServiceFunctionDecorator

# models.py


class HeavenTestModel(models.Model):
    """ That is a placeholder model that has no sense """
    name = models.CharField(max_length=30)
    creation_date = models.DateTimeField(auto_now=True)
    is_working = models.BooleanField(default=True)


#HeavenTestModel.objects.create(name='abc')
#HeavenTestModel.objects.create(name='def')
#HeavenTestModel.objects.create(name='ghi')
# models.py


# services.py

class HeavenTestModelService(Service):
    """
    That is the service that we will use in order to work with our HeavenTestModel.
    There are prebuilt service functions, but I want to add my own.
    """
    model = HeavenTestModel     # we set the model that we are working with

    @ServiceFunctionDecorator()  # I can write my functions without that decorator
    # but if I want the logging and other cool things by default, then I should use it.
    def set_as_working(self, **kwargs):
        """
        Here I want to set the 'is_working' argument of my HeavenTestModel as True.
        I get my instance from the kwargs and use update() function of my service to set it
        as is_working.
        """
        kwargs, instance = self.pop_argument_from_kwargs(kwargs, argument='instance')   # we get the
        # instance from kwargs and delete it.

        self.update(instance=instance, is_working=True)
        return instance

    def set_as_not_working(self):
        """
        I use no decorator in that function, however, I can still use it.
        Note that we don't want to get an instance from the kwargs, we want to get our
        current service objects. With that behavior, we can use chaining without any problems.
        I will rethink service chaining in the future, but for now that's how to do it.
        """
        self.objects.is_working = False     # I can use normal model expressions, not only service functions
        self.objects.save()
        return False    # I can also return what I want


# services.py


# views.py

class HeavenOwnServiceTestView(View):
    def post(self, request, **kwargs):
        service = HeavenTestModelService()  # we create our service in order to work with the ORM

        next_service = service.get(pk=kwargs.get('pk'))     # we get the user by pk
        if next_service is None:    # the default behavior is to return None in case of an error
            return HttpResponse("Not found")

        next_service.set_as_working()
        # if the service was found, then we set it as the working one
        return HttpResponse("<b>Set as working worked fine</b>")

    def get(self, request):
        """
        That will set the first instance of our model as not working.
        Since we are using the self.objects in the set_as_not_working() function, we can chain
        our services.
        """

        service = HeavenTestModelService()
        service = service.first(info_message=f"User {request.user} retrieved the first test model")

        if service is not None:
            service.set_as_not_working()
        else:
            return HttpResponse("Not found")

        return HttpResponse(f"{service.objects} has is_working as False now")

# views.py
