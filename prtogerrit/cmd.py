from __future__ import print_function
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


def assert_branch(servicename, number):
    target = "pr_%s_%s" % (servicename, number)
    output = run_command_status(
        "git", "rev-parse", "--abbrev-ref", "HEAD"
    )
    if output != target:
        raise Exception("For --continue, we should be on branch %s" % target)


def fetch_branch(repo, branch):
    run_command_status("git", "pull", "--squash", repo, branch)


def commit_branch(comment, author):
    run_command_status("git", "commit", "--author", author, "-m", comment)


def push_to_gerrit(gerrit):
    output = run_command_status("git", "review", "-R")
    pr_link = re.search(r'%s\S+' % gerrit, output, re.S)
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
    print(" ".join(argv))
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


def prtogerrit(
        gerrit, service, repo, number, username, password, continue_, dryrun):
    if service == "github":
        client = ghclient.GitHub(repo, username, password)
    elif service == "bitbucket":
        client = bbclient.BitBucket(repo, username, password)
    else:
        assert False

    pr_info = client.get_pullrequest(number)

    if not continue_:
        # TODO: from non-master?
        create_branch(service, number)

        # this step will fail if the merge fails.  user will
        # correct and run w/ --continue
        fetch_branch(pr_info['repo'], pr_info["branch"])
    else:
        assert_branch(service, number)

    commit_msg = "%s\n\n%s\n\nPull-request: %s" % (
        pr_info["title"],
        pr_info["description"],
        pr_info["html_url"]
    )
    author = None
    with open(".git/SQUASH_MSG") as f:
        for line in f:
            if line.startswith("Author:"):
                author = line[8:].decode('utf-8')
                break
        else:
            raise Exception("could not determine author for PR.")

    commit_branch(commit_msg, author)

    if dryrun:
        sys.exit("exiting for dry run")

    review_num = push_to_gerrit(gerrit)

    comment = (
        "Dear contributor -\n\n"
        "This pull request is being moved to Gerrit, at %s, where it "
        "may be tested and reviewed more closely.  As such, the pull "
        "request itself is being marked \"closed\" or \"declined\", "
        "however your "
        "contribution is merely being moved to our central review system. "
        "Please register at "
        "%s#/register/"
        " to send and receive comments regarding this item." % (
            review_num,
            gerrit,
        )
    )
    print(comment)
    client.close_pullrequest(number, comment)
    run_command_status("git", "checkout", "master")


def main(argv=None):
    parser = ArgumentParser(prog="prtogerrit")
    parser.add_argument(
        "name", help="config name")
    parser.add_argument("number", type=int, help="pr number")
    parser.add_argument("--config", help="path to config file")
    parser.add_argument(
        "--continue", action="store_true",
        dest="continue_",
        help="continue pushing to gerrit after a merge failure")
    parser.add_argument(
        "--dryrun", action="store_true",
        help="Merge the branch from the PR locally but don't push "
        "to gerrit or close the PR."
    )
    options = parser.parse_args(argv)

    from os.path import expanduser
    import ConfigParser
    configfile = options.config or expanduser("~/.prtogerrit.config")

    config = ConfigParser.ConfigParser()
    print("Using config: ", configfile)
    config.read([configfile])

    gerrit = config.get(options.name, "gerrit")
    service = config.get(options.name, "service")
    repo = config.get(options.name, "repo")
    username = config.get(options.name, "username")
    password = config.get(options.name, "password")

    prtogerrit(
        gerrit, service, repo, options.number,
        username, password, options.continue_, options.dryrun)


if __name__ == '__main__':
    main()
