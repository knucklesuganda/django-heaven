""" That file contains examples for responses.http response classes """
from django.http import HttpResponse

from responses.http import LoggedHttpResponseMixin
from responses.examples.base import HeavenTestView


class HeavenTestHttpView(LoggedHttpResponseMixin, HeavenTestView):
    """
    That view will teach you how to use LoggedHttpResponseProxyMixin.
    We will not return render() function, but you can totally do it.
    As long as you return an HttpResponse or HttpStreamingResponse - you are fine.
    Make some requests and look in the console while you are making them.
    """
    success_data = HttpResponse("<i>Success</i>")
    error_data = HttpResponse("<b>Error</b>")



