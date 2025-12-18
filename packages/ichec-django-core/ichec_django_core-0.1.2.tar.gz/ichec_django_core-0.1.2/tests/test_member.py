from ichec_django_core.models import Member

from ichec_django_core.utils.test_utils.test_client import (
    AuthAPITestCase,
    setup_default_users_and_groups,
    add_group_permissions,
)


class MemberViewTests(AuthAPITestCase):

    template = {
        "username": "test_user",
        "identifiers": [{"id_type": "ORCID", "value": "1234-5678-1234-5678"}],
    }

    def setUp(self):
        self.url = "/api/members/"
        setup_default_users_and_groups()

        add_group_permissions(
            "admins",
            Member,
            ["change_member", "add_member"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_authenticated(self):
        self.assert_200(self.authenticated_detail("regular_user", 1))

    def test_create_not_authenticated(self):
        data = {"username": "test_user"}
        self.assert_401(self.create(self.template))

    def test_create_authenticated_no_permission(self):
        self.assert_403(self.authenticated_create("regular_user", self.template))

    def test_create_authenticated(self):
        self.assert_201(self.authenticated_create("admin_user", self.template))

    def test_update_authenticated(self):
        response = self.authenticated_create("admin_user", self.template)
        self.assert_201(response)

        user = response.json()
        user["identifiers"][0]["value"] = "4321-5678-1234-5678"

        response = self.authenticated_update("admin_user", user["id"], user)
        self.assert_200(response)

        user_updates = response.json()
        self.assertTrue(
            user_updates["identifiers"][0]["value"] == "4321-5678-1234-5678"
        )

        user_updates["identifiers"].append({"id_type": "FREEFORM", "value": "1234"})
        response = self.authenticated_update("admin_user", user["id"], user_updates)
        self.assert_200(response)
        user_updates = response.json()
        self.assertTrue(len(user_updates["identifiers"]) == 2)

        user_updates["identifiers"] = []
        response = self.authenticated_update("admin_user", user["id"], user_updates)
        self.assert_200(response)

        user_updates = response.json()
        self.assertTrue(len(user_updates["identifiers"]) == 0)
