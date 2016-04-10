from argparse import ArgumentParser
from . import ghclient
from . import bbclient
import sys
import subprocess
import shlex
import os
import re


def create_branch(servicename, number):
    run_command_status("git", "checkout", "master")
    run_command_status(
        "git", "checkout", "-b", "pr_%s_%s" % (servicename, number))


def fetch_branch(repo, branch):
    run_command_status("git", "pull", repo, branch)


def push_to_gerrit():
    output = run_command_status("git", "review", "-R")
    pr_link = re.search(r'https://gerrit.sqlalchemy.org/\S+', output, re.S)
    if pr_link:
        return pr_link.group(0)
    else:
        raise Exception("Could not locate PR link: %s" % output)


def run_command_status(*argv, **kwargs):
    if len(argv) == 1:
        # for python2 compatibility with shlex
        if sys.version_info < (3,) and isinstance(argv[0], unicode):
            argv = shlex.split(argv[0].encode('utf-8'))
        else:
            argv = shlex.split(str(argv[0]))
    stdin = kwargs.pop('stdin', None)
    newenv = os.environ.copy()
    newenv['LANG'] = 'C'
    newenv['LANGUAGE'] = 'C'
    newenv.update(kwargs)
    p = subprocess.Popen(argv,
                         stdin=subprocess.PIPE if stdin else None,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         env=newenv)
    (out, nothing) = p.communicate(stdin)
    out = out.decode('utf-8', 'replace')
    if p.returncode != 0:
        raise Exception("Command failed: %s %s" % (argv, out.strip()))
    return out.strip()


def prtogerrit(service, repo, number, username, password):
    if service == "github":
        client = ghclient.GitHub(repo, username, password)
    elif service == "bitbucket":
        client = bbclient.BitBucket(repo, username, password)
    else:
        assert False

    pr_info = client.get_pullrequest(number)

    # TODO: from non-master?
    create_branch(service, number)

    fetch_branch(pr_info['repo'], pr_info["branch"])

    review_num = push_to_gerrit()

    comment = "This pull request has been transferred to Gerrit,"\
        " at %s.  Please register at "\
        "https://gerrit.sqlalchemy.org/#/register/"\
        " to send and receive comments regarding this item." % review_num

    client.close_pullrequest(number, comment)


def main(argv=None):
    parser = ArgumentParser(prog="prtogerrit")
    parser.add_argument(
        "service", choices=["github", "bitbucket"], help="service")
    parser.add_argument("repo")
    parser.add_argument("number", type=int, help="pr number")
    parser.add_argument("-u", "--username", help="username")
    parser.add_argument("-p", "--password", help="password")
    options = parser.parse_args(argv)

    prtogerrit(
        options.service, options.repo, options.number,
        options.username, options.password)


if __name__ == '__main__':
    main()
