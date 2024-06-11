class ExceptionMiddleware(object):
    def process_exception(self, request, exception):
        print(f"ERROR: {exception}")
