import subprocess
import os
image = os.environ['IMAGE_NAME']


def run(command):
    # running a command in a container, removing the container, and return the result
    cli = 'docker run --rm --interactive %s %s ' % (image, command)
    result = subprocess.run(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result.stdout = result.stdout.rstrip()
    return result

def stdout_of(command):
    # warp run, and parse the result
    return(run(command).stdout.decode())


def stderr_of(command):
    return(run(command).stderr.decode())


def environment(varname):
    # parse the container environment as python dictionary, and return the value of "varname"
    environ = {}
    for line in run('env').stdout.decode().split("\n"):
        var, value = line.split('=')
        environ[var] = value
    return environ[varname]


