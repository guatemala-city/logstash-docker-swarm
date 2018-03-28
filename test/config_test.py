from .helpers import run, stdout_of
from .constants import pipeline_config_path_workspace, pipeline_config_path_container
import pytest


path_list = [(pipeline_config_path_workspace,pipeline_config_path_container)]

@pytest.fixture(params=path_list,ids=["pipeline_config"])
def integrity(request):
    with open(request.param[0],"r") as file:
        text = file.read()
    hashed_text=hash(text.rstrip())
    text_in_container = hash(stdout_of("cat '{0}'".format(request.param[1])))
    yield hashed_text,text_in_container

def test_logstash_configtest():
    result = run("-t")
    assert (result.returncode == 0,result.stdout)

def test_configuration_file_integrity(integrity):
    # compares the hashes from "integrity" fixture
    assert integrity[0] == integrity[1]

