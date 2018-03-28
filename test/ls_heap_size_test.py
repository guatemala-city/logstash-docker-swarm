from .helpers import environment
import docker
import pytest
import os

ls_heap_container=None
# load the LS_HEAP_SIZE and image that passed as environment variables
LS_HEAP_SIZE = os.environ['LS_HEAP_SIZE']
image = os.environ['IMAGE_NAME']

def test_env_variable_is_set_correctly():
    # check if the environment variable set correctly in the container
    assert environment('LS_JAVA_OPTS') == "-Xmx"+LS_HEAP_SIZE


@pytest.mark.timeout(30)
def test_LS_HEAP_SIZE_in_ps(size=LS_HEAP_SIZE):
    client = docker.from_env()
    # run container in detached mode
    ls_heap_container = client.containers.run(image,detach=True)
    # check for "-Xmx" substring
    text=str(ls_heap_container.top(ps_args="auxww"))
    while "-Xmx" not in text:
        # wait till "-Xmx" substring in the processes list
        text=str(ls_heap_container.top(ps_args="auxww"))
    # if the container exist, we delete it (in healthy situation it should exist)
    if ls_heap_container is not None:
        # stop the container
        ls_heap_container.stop()
        # remove the container
        ls_heap_container.remove()
    # compare the strings..
    assert "-Xmx"+size in str(text)


