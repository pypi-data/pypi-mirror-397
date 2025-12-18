from davidkhala.ai.agent.dify.ops.console import API


class ConsoleUser(API):
    def login(self, email, password,
              *,
              remember_me=True,
              language="en-US"
              ):
        url = f"{self.base_url}/login"

        r = self.request(url, "POST", json={
            'email': email,
            'password': password,
            'remember_me': remember_me,
            'language': language,
        })
        assert r == {"result": "success"}
        self.options['headers']['x-csrf-token'] = self.session.cookies.get("csrf_token")
        return self.session.cookies

    @property
    def me(self) -> dict:
        url = f"{self.base_url}/account/profile"
        return self.request(url, "GET")

    @property
    def workspace(self) -> dict:
        url = f"{self.base_url}/features"
        return self.request(url, "GET")
