from .clientbase import ClientBase


class BitBucket(ClientBase):

    def __init__(self, repo, username, password):
        self.base_url = "https://api.bitbucket.org/2.0/"
        super(BitBucket, self).__init__(repo, username, password)

    def get_pullrequest(self, pr_number):
        pr = self._get(
            "/repositories%s/pullrequests/%s" % (
                self.repo,
                pr_number
            )
        )
        repo = pr["source"]["repository"]["full_name"]
        # commit = pr["source"]["commit"]["hash"]
        branch = pr["source"]["branch"]["name"]

        return {
            "repo": "https://bitbucket.org/%s" % repo,
            "branch": branch
        }

    def close_pullrequest(self, pr_number, comment):
        self._post(
            "/repositories%s/pullrequests/%s/decline" % (
                self.repo,
                pr_number
            ),
            data={
                "message": comment
            }
        )
