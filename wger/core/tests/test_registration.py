# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging
import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text

from wger.core.forms import RegistrationForm
from wger.core.forms import RegistrationFormNoCaptcha
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.core.models import UserProfile

logger = logging.getLogger(__name__)


class RegistrationTestCase(WorkoutManagerTestCase):
    """
    Tests registering a new user
    """

    def test_registration_captcha(self):
        """
        Tests that the correct form is used depending on global
        configuration settings
        """
        with self.settings(
                WGER_SETTINGS={
                    'USE_RECAPTCHA': True,
                    'REMOVE_WHITESPACE': False,
                    'ALLOW_REGISTRATION': True,
                    'ALLOW_GUEST_USERS': True,
                    'TWITTER': False
                }):
            response = self.client.get(reverse('core:user:registration'))
            self.assertIsInstance(response.context['form'], RegistrationForm)

        with self.settings(
                WGER_SETTINGS={
                    'USE_RECAPTCHA': False,
                    'REMOVE_WHITESPACE': False,
                    'ALLOW_REGISTRATION': True,
                    'ALLOW_GUEST_USERS': True,
                    'TWITTER': False
                }):
            response = self.client.get(reverse('core:user:registration'))
            self.assertIsInstance(response.context['form'],
                                  RegistrationFormNoCaptcha)

    def test_register(self):

        # Fetch the registration page
        response = self.client.get(reverse('core:user:registration'))
        self.assertEqual(response.status_code, 200)

        # Fill in the registration form
        registration_data = {
            'username': 'myusername',
            'password1': 'secret',
            'password2': 'secret',
            'email': 'not an email',
            'g-recaptcha-response': 'PASSED',
        }
        count_before = User.objects.count()

        # Wrong email
        response = self.client.post(
            reverse('core:user:registration'), registration_data)
        self.assertFalse(response.context['form'].is_valid())
        self.user_logout()

        # Correct email
        registration_data['email'] = 'my.email@example.com'
        response = self.client.post(
            reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count_before + 1, count_after)
        self.user_logout()

        # Username already exists
        response = self.client.post(
            reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before + 1, count_after)

        # Email already exists
        registration_data['username'] = 'my.other.username'
        response = self.client.post(
            reverse('core:user:registration'), registration_data)
        count_after = User.objects.count()
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before + 1, count_after)

    def test_registration_deactivated(self):
        """
        Test that with deactivated registration no users can register
        """

        with self.settings(
                WGER_SETTINGS={
                    'USE_RECAPTCHA': False,
                    'REMOVE_WHITESPACE': False,
                    'ALLOW_GUEST_USERS': True,
                    'ALLOW_REGISTRATION': False
                }):

            # Fetch the registration page
            response = self.client.get(reverse('core:user:registration'))
            self.assertEqual(response.status_code, 302)

            # Fill in the registration form
            registration_data = {
                'username': 'myusername',
                'password1': 'secret',
                'password2': 'secret',
                'email': 'my.email@example.com',
                'g-recaptcha-response': 'PASSED',
            }
            count_before = User.objects.count()

            response = self.client.post(
                reverse('core:user:registration'), registration_data)
            count_after = User.objects.count()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before, count_after)


class RegistrationTestCaseRest(WorkoutManagerTestCase):
    # Registration data
    reg_data = dict(username='test_user',
                    password='test_password', email='test@mail.com')

    # Registration url
    url = '/api/v2/register/'

    def new_user_login(self):
        '''
        Login the user, by default as 'admin'
        '''
        self.client.login(username='test1', password='test_pass')

    def create_user_profile(self):
        '''
        Create the user's profile here
        '''
        # Fill in the registration form
        registration_data = {'username': 'test1',
                             'password1': 'test_pass',
                             'password2': 'test_pass',
                             'email': 'my.email1@example.com',
                             'g-recaptcha-response': 'PASSED', }
        self.client.post(
            reverse('core:user:registration'), registration_data)

        user = User.objects.get(username="test1")
        user_profile = UserProfile.objects.get(user=user)
        user_profile.can_add_user = True
        user_profile.save()

    def test_unauthorized_user_cannot_access_resources(self):
        '''
        Test that non registered users cannot access the api
        '''

        # Test for the unauthorized user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_registered_user_cannot_access_without_permission(self):
        '''
        Test that users without permission cannot add users via the api
        '''

        self.create_user_profile()
        # Test for the unauthorized user
        self.user_login()  # this user's flag can_add_user is set to False
        response = self.client.post(self.url, data=self.reg_data)
        self.assertEqual(response.status_code, 403)

    def test_user_successfully_added_via_api(self):
        '''
        Test that a user is added successfully via the api by an authorized user
        '''
        reg_data = dict(username='test_user',
                        password='test_password', email='test@mail.com')

        self.create_user_profile()
        # Test register via Rest API
        self.new_user_login()  # this user's flag can_add_user is set to True
        response = self.client.post(
            self.url, data=reg_data)
        reply = json.loads(response.content.decode('utf-8'))

        self.assertEqual(reply['Message'],
                         "Profile created", msg="Profile not created")

    def test_duplicate_users_not_allowed(self):
        '''
        Test that duplicate usernames are not allowed
        '''

        self.create_user_profile()
        self.new_user_login()  # this user's flag can_add_user is set to True

        # Test username exists
        self.client.post(self.url, data=self.reg_data)
        duplicate_response_post = self.client.post(self.url, data=self.reg_data)
        self.assertEqual(duplicate_response_post.status_code, 400)

    def test_missing_credetial_not_allowed(self):
        '''
        Test that empty field in the api request data are not allowed
        '''

        self.create_user_profile()
        # Test incomplete data
        self.reg_data.pop('password')
        response_post = self.client.post(self.url, data=self.reg_data)
        self.assertEqual(response_post.status_code, 400)

    def test_deformed_credential_data_not_allowed(self):
        '''
        Test that json request data with some fields not specified is
        deformed json and is not allowed
        '''

        self.create_user_profile()
        # Invalid data missing username
        reg_data_new = {}
        reg_data_new['email'] = 'test_email'
        reg_data_new['password'] = 'password'
        response_post = self.client.post(self.url, data=reg_data_new)
        self.assertEqual(response_post.status_code, 400)
