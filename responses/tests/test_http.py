from django.http import HttpResponse

from responses.http import LoggedHttpResponseMixin
from responses.tests.base import BaseLoggedResponseMixinTest


class LoggedHttpResponseMixinTest(BaseLoggedResponseMixinTest):
    testing_class = LoggedHttpResponseMixin
    info_data = HttpResponse("info")
    error_data = HttpResponse("error")
