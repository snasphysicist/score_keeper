
from io import StringIO
import os

from django.http import FileResponse, Http404

from score_keeper.settings import BASE_DIR


# Will pre-load static
# files on first call
# Store here
# Like a manual cache
STATIC_LOADED = False
STATIC = None


def try_static(request):
    # Set up cache on first call
    if STATIC is None:
        load_static()
    path = request.get_full_path()
    # Path should be of format
    # /<module>/folders/filename
    # Ditch module bit
    path = "/".join(
        path.split("/")[1:]
    )
    # Try to get page content from 'cache'
    if path in list(STATIC):
        return FileResponse(
            STATIC[path]["content"].getvalue(),
            content_type=STATIC[path]["type"]
        )
    else:
        raise Http404


def load_static():
    global STATIC
    STATIC = {}
    static_paths = []
    # Find all files in static folders
    for root_directory, directories, files in os.walk(BASE_DIR):
        for file in files:
            if "/static/" in os.path.join(
                root_directory,
                file
            ):
                static_paths.append(
                    os.path.join(
                        root_directory,
                        file
                    )
                )
    # Load file content for each
    for path in static_paths:
        # Path is everything 'south' of /static/
        uri_path = path.split("/static/")[-1]
        with open(path, 'r') as file:
            content = file.read()
        file_like_content = StringIO()
        file_like_content.write(
            content
        )
        STATIC[uri_path] = {
            "content": file_like_content,
            "type": guess_type(path)
        }


def guess_type(path):
    if ".css" in path:
        return "text/css"
    if ".js" in path:
        return "text/javascript"
    if ".html" in path:
        return "text/html"
    if ".svg" in path:
        return "image/svg+xml"
    return "text/plain"
