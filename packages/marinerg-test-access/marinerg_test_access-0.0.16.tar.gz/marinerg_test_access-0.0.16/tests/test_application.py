import tempfile

from ichec_django_core.utils.test_utils.test_client import (
    AuthAPITestCase,
    setup_default_users_and_groups,
)

from marinerg_test_access.utils.test_utils.test_client import (
    setup_access_call,
    setup_application,
)


class AccessApplicationViewTests(AuthAPITestCase):

    template = {
        "call": "http://testserver/api/access_calls/1/",
        "form": {"values": []},
        "facilities": [],
        "dates_flexible": True,
    }

    def setUp(self):
        self.url = "/api/access_applications/"
        setup_default_users_and_groups()
        call = setup_access_call()
        setup_application(call, "test_applicant")

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_regular_user(self):
        self.assert_403(self.authenticated_detail("regular_user", 1))

    def test_detail_test_applicant(self):
        self.assert_200(self.authenticated_detail("test_applicant", 1))

    def xtest_detail_consortium_admin(self):
        self.assert_200(self.authenticated_detail("admin_user", 1))

    def test_create_not_authenticated(self):
        self.assert_401(self.create(self.template))

    def test_create_regular_user(self):
        self.assert_201(self.authenticated_create("regular_user", self.template))

    def test_update_regular_user(self):
        response = self.authenticated_create("regular_user", self.template)
        self.assert_201(response)

        created = response.json()

        created["dates_flexible"] = False
        updated = self.authenticated_update("regular_user", created["id"], created)
        self.assert_200(updated)

    def test_submit(self):
        response = self.authenticated_create("regular_user", self.template)
        self.assert_201(response)

        created = response.json()

        created["status"] = "SUBMITTED"
        updated = self.authenticated_update("regular_user", created["id"], created)
        self.assert_200(updated)
