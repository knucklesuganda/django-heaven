from django.http import HttpResponse
from django.shortcuts import reverse
from django.views import View


class HeavenTestAPIView(View):
    def get(self, request):
        link_format = "<a href='{reversed_link}'>{link}</a>"

        example_urls = [link_format.format(reversed_link=reverse(link), link=link) for link in (
            'example_http',
            'example_json',
            'example_json_proxy',
            'example_redirect',
        )]

        try:
            example_urls += [
                link_format.format(reversed_link=reverse(link), link=link)
                for link in ['example_rest', 'example_rest_proxy']
            ]
        except Exception:
            pass

        return HttpResponse("<br>".join(example_urls))
