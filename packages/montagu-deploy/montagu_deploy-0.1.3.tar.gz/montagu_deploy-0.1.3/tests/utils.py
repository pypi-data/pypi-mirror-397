import ssl
import time
import urllib
from contextlib import contextmanager

import docker


# Because we wait for a go signal to come up, we might not be able to
# make the request right away:
def http_get(url, retries=10, poll=0.5):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for _i in range(retries):
        try:
            r = urllib.request.urlopen(url, context=ctx)  # noqa
            return r.read().decode("UTF-8")
        except (urllib.error.URLError, ConnectionResetError) as e:
            print("sleeping...")
            time.sleep(poll)
            error = e
    raise error


# Create a container, as a context manager.
# This container will be stopped and removed when the context manager exits.
@contextmanager
def create_container(image, **kwargs):
    container = docker.from_env().containers.create(image, detach=True, **kwargs)
    try:
        yield container
    finally:
        container.stop()
        container.remove()
