# Django heaven

**Transfer your projects from hell to django-heaven**

# Overview

Django heaven is a module for the Django projects. It helps you
to structure and log your responses, use services instead of raw ORM queries,
log everything in JSON, and much more.

# Requirements

* Python (3.7, 3.8, 3.9)
* Django (3.0, 3.1, 3.2)
* django-rest-framework(optional)

# Installation

Install using `pip`:

    pip install django-heaven

Add `'django-heaven'` to your `INSTALLED_APPS` setting.

    INSTALLED_APPS = ['django_heaven',]

# Services
Service is a class that helps you work with your models without
raw ORM queries in your views. It supports custom error handling and logging by default.
All the ORM queries must be done in services. All the services inherit from BaseService class.
What you should do is add a custom service for your model. There are a lot of possibilities for your
services since we are using ****kwargs**. The only requirements are the log messages that we will use.
We provide some built-in services for you, so let's use them here.

#### Example

```python
from django.views import View
from django.http import HttpResponse

from django_heaven.services.users import UserService

class UserView(View):
    def get(self, request):
        user_service = UserService()
        all_users = user_service.all(info_message="Listed all the users")
        return HttpResponse(f"{all_users}")
```
In that example we use UserService. That service allows you to work with the 
User model of your project. In our case, we get all the users and write "Listed all the users"
message to logs with INFO level.

# Responses 
* Responses - responses in django-heaven aren't created directly inside of views.
Instead, we use a class that helps us to call similar functions and provide the arguments 
for the response data, response log message, response validation and a lot of other things.
If you will use the same mixins, then you will have the similar structure of your API's with the logging 
and validation. If you want to add our example views, then include
examples in your `urls.py`:

```python
urlpatterns += [
    path('django_heaven/', include('django_heaven.responses.examples.urls')),
]
```

### There are two concepts of responses:
1) Response creation - you provide the data and we create the response object for you
2) Response proxy - you provide the response object, we validate it and log the messages

#### Response Creation Example
    return self.log_response_as_error(
        data=[1, 2, 3],
        log_message="User retrieved 1, 2, 3",
    )

In that case, we log an error and provide raw data that will
be converted to a normal response in return. If you work in your own views, and create your own responses, 
then you will use Response Creation technique.


#### Response Proxy Example
    return self.log_response_as_info(
        data=JsonResponse({"message": "ok"}),
        log_message="User retrieved 1, 2, 3",
    )

In that case, we log an info and provide already created response. Our response mixin
will not change it, and we will just receive the same response at the end.

However, there are some things that you should know about proxy responses:
1) We run validation checks on proxy responses. You can write your own checks reassigning proxy_response_validation()
function and raising an Exception() where needed
2) We do not recommend using that, since these responses will not follow the same structure. It is better to recreate your 
response in the response mixin. But, if you can't do that, then proxy is a way to go.


# TODO
1) All the tests for the responses and services
2) Support for the django-graphene
