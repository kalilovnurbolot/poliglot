from django.test import TestCase

# Create your tests here.


from django.contrib.auth import get_user_model


class AdminEmailTests(TestCase):
    def test_admin_email_always_becomes_admin(self):
        user = get_user_model().objects.create_user(email='KalilovNurbolot3@gmail.com', password='pass12345')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        user.is_staff = False
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_staff)

    def test_other_users_are_not_admins(self):
        user = get_user_model().objects.create_user(email='someone@example.com', password='pass12345')
        self.assertFalse(user.is_staff)
