from .clientbase import ClientBase


class GitHub(ClientBase):

    def __init__(self, repo, username, password):
        self.base_url = "https://api.github.com/"
        super(GitHub, self).__init__(repo, username, password)

    def get_pullrequest(self, pr_number):

        pr = self._get(
            "/repos%s/pulls/%s" % (
                self.repo,
                pr_number
            )
        )
        repo = pr["head"]["repo"]["clone_url"]
        branch = pr["head"]["ref"]

        return {
            "repo": repo,
            "branch": branch,
            "title": pr["title"],
            "description": pr["body"],
            "html_url": pr["html_url"]
        }

    def close_pullrequest(self, pr_number, comment):
        self._post(
            "/repos%s/issues/%s/comments" % (
                self.repo,
                pr_number
            ),
            data={
                "body": comment,
            },
            as_json=True
        )
        self._patch(
            "/repos%s/pulls/%s" % (
                self.repo,
                pr_number
            ),
            data={
                "state": "closed"
            },
            as_json=True
        )


