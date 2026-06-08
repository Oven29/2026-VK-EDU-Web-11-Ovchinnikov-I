import urllib.parse


def application(environ, start_response):
    """
    Independent WSGI application that parses GET and POST parameters.
    """
    # Parse GET parameters from QUERY_STRING
    query_string = environ.get('QUERY_STRING', '')
    get_params = urllib.parse.parse_qs(query_string)

    # Parse POST parameters from wsgi.input
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    post_params = urllib.parse.parse_qs(request_body.decode('utf-8'))

    # Format the output text
    response_body = f"GET parameters: {get_params}\nPOST parameters: {post_params}\n"

    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]

    start_response(status, headers)
    return [response_body.encode('utf-8')]

# To run: gunicorn -b 0.0.0.0:8081 simple_wsgi:application
