prtogerrit
==========

This is a script Mike is working on to transfer pull requests from
github and bitbucket into gerrit.

Requirements
------------

You need a running instance of Gerrit available, and also you must have
the `git-review <http://docs.openstack.org/infra/git-review/>`_ tool installed locally.

Installation
------------

pip install prtogerrit

Configuration
-------------

Create a new file ${HOME}/.prtogerrit.config.  In it, place instructions
as to where your git repositories are, and into what part of your gerrit
server you'd like them to go::

	# place this file in $HOME/.prtogerrit.config

	[myproject_github]
	gerrit=https://gerrit.myproject.com/
	service=github
	repo=myusername/myproject
	username=myusername
	password=foobar

	[myproject_bitbucket]
	gerrit=https://gerrit.myproject.com/
	service=bitbucket
	repo=myusername/myproject
	username=myusername
	password=foobar

Running it
----------

To use the script, suppose you receive pull request number 14 on "myproject"
at Github.  Go to your git working directory, select the desired branch
(usually master), and type::

	prtogerrit myproject_github 14

If the pull request merges cleanly, that's it!  The script will contact
the Github API, get the branch information for pull request 14, squash-merge
it into a new local branch called "myproject_github_14", and will then
push it up with "git review".  It will also close the pull request and
add comments for the contributor how to find the review.

Conflicts
---------

If the squash-merge has conflicts, prtogerrit will stop and let you correct
the changes, by using "git add <filename>" just like any other merge
resolution.  Then run the command again with ``--continue``::

	prtogerrit myproject_github 14 --continue
