default_app_config = 'core.apps.CoreAppConfig'

class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()