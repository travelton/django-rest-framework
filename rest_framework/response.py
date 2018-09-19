"""
The Response class in REST framework is similar to HTTPResponse, except that
it is initialized with unrendered data, instead of a pre-rendered string.

The appropriate renderer is called during Django's template response rendering.
"""
from __future__ import unicode_literals
#from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.template.response import SimpleTemplateResponse
from rest_framework.compat import six

STATUS_CODE_TEXT = {
    100: u'CONTINUE',
    101: u'SWITCHING PROTOCOLS',
    102: u'PROCESSING',
    200: u'OK',
    201: u'CREATED',
    202: u'ACCEPTED',
    203: u'NON-AUTHORITATIVE INFORMATION',
    204: u'NO CONTENT',
    205: u'RESET CONTENT',
    206: u'PARTIAL CONTENT',
    207: u'MULTI-STATUS',
    208: u'ALREADY REPORTED',
    226: u'IM USED',
    300: u'MULTIPLE CHOICES',
    301: u'MOVED PERMANENTLY',
    302: u'FOUND',
    303: u'SEE OTHER',
    304: u'NOT MODIFIED',
    305: u'USE PROXY',
                           306: u'RESERVED',
                            307: u'TEMPORARY REDIRECT',
                             400: u'BAD REQUEST',
                              401: u'UNAUTHORIZED',
                               402: u'PAYMENT REQUIRED',
                                403: u'FORBIDDEN',
                                 404: u'NOT FOUND',
                                  405: u'METHOD NOT ALLOWED',
                                   406: u'NOT ACCEPTABLE',
                                    407: u'PROXY AUTHENTICATION REQUIRED',
                                     408: u'REQUEST TIMEOUT',
                                      409: u'CONFLICT',
                                       410: u'GONE',
                                        411: u'LENGTH REQUIRED',
                                         412: u'PRECONDITION FAILED',
                                          413: u'REQUEST ENTITY TOO LARGE',
                                           414: u'REQUEST-URI TOO LONG',
                                            415: u'UNSUPPORTED MEDIA TYPE',
    416: u'REQUESTED RANGE NOT SATISFIABLE',
                                              417: u'EXPECTATION FAILED',
                                               422: u'UNPROCESSABLE ENTITY',
                                                423: u'LOCKED',
                                                 424: u'FAILED DEPENDENCY',
                                                  426: u'UPGRADE REQUIRED',
    500: u'INTERNAL SERVER ERROR',
                                                    501: u'NOT IMPLEMENTED',
                                                     502: u'BAD GATEWAY',
    503: u'SERVICE UNAVAILABLE',
                                                       504: u'GATEWAY TIMEOUT',
    505: u'HTTP VERSION NOT SUPPORTED',
    506: u'VARIANT ALSO NEGOTIATES',
    507: u'INSUFFICIENT STORAGE',
    508: u'LOOP DETECTED',
    510: u'NOT EXTENDED'
}

class Response(SimpleTemplateResponse):
    """
    An HttpResponse that allows it's data to be rendered into
    arbitrary media types.
    """

    def __init__(self, data=None, status=200,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.

        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=status)
        self.data = data
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value

    @property
    def rendered_content(self):
        renderer = getattr(self, 'accepted_renderer', None)
        media_type = getattr(self, 'accepted_media_type', None)
        context = getattr(self, 'renderer_context', None)

        assert renderer, ".accepted_renderer not set on Response"
        assert media_type, ".accepted_media_type not set on Response"
        assert context, ".renderer_context not set on Response"
        context['response'] = self

        charset = renderer.charset
        content_type = self.content_type

        if content_type is None and charset is not None:
            content_type = "{0}; charset={1}".format(media_type, charset)
        elif content_type is None:
            content_type = media_type
        self['Content-Type'] = content_type

        ret = renderer.render(self.data, media_type, context)
        if isinstance(ret, six.text_type):
            assert charset, 'renderer returned unicode, and did not specify ' \
            'a charset value.'
            return bytes(ret.encode(charset))
        return ret

    @property
    def status_text(self):
        """
        Returns reason text corresponding to our HTTP response status code.
        Provided for convenience.
        """
        # TODO: Deprecate and use a template tag instead
        # TODO: Status code text for RFC 6585 status codes
        return STATUS_CODE_TEXT.get(self.status_code, '')

    def __getstate__(self):
        """
        Remove attributes from the response that shouldn't be cached
        """
        state = super(Response, self).__getstate__()
        for key in ('accepted_renderer', 'renderer_context', 'data'):
            if key in state:
                del state[key]
        return state
