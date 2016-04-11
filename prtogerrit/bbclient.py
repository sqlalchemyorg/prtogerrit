from .clientbase import ClientBase


class BitBucket(ClientBase):

    def __init__(self, repo, username, password):
        self.base_url = "https://api.bitbucket.org/"
        super(BitBucket, self).__init__(repo, username, password)

    def get_pullrequest(self, pr_number):
        pr = self._get(
            "/2.0/repositories%s/pullrequests/%s" % (
                self.repo,
                pr_number
            )
        )
        repo = pr["source"]["repository"]["full_name"]
        # commit = pr["source"]["commit"]["hash"]
        branch = pr["source"]["branch"]["name"]

        return {
            "repo": "https://bitbucket.org/%s" % repo,
            "branch": branch,
            "title": pr["title"],
            "description": pr["description"],
            "html_url": pr["links"]["html"]["href"]
        }

    def close_pullrequest(self, pr_number, comment):
        self._post(
            "/1.0/repositories%s/pullrequests/%s/comments" % (
                self.repo,
                pr_number
            ),
            data={
                "content": comment
            }
        )
        self._post(
            "/2.0/repositories%s/pullrequests/%s/decline" % (
                self.repo,
                pr_number
            ),
            data={
                "message": comment
            }
        )
