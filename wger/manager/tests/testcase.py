# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import os

from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test import LiveServerTestCase
from django.db import models

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class WorkoutManagerTestCase(TestCase):
    fixtures = ('tests-user-data',
                'test-weight-data',
                'test-exercises',
                'tests-ingredients',
                'test-nutrition-data',
                'days_of_week',
                'tests-workout-data')

    def setUp(self):
        '''
        Overwrite some of Django's settings here
        '''
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        '''
        Reset settings
        '''
        del os.environ['RECAPTCHA_TESTING']

    def user_login(self, user='admin'):
        '''
        Login the user, by default as 'admin'
        '''
        self.client.login(username=user, password='%(user)s%(user)s' % {'user': user})

    def user_logout(self):
        '''
        Visit the logout page
        '''
        self.client.logout()


class WorkoutManagerDeleteTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting an object an authorized user, a different one and a logged out
    one. This assumes the delete action is only triggered with a POST request and
    GET will only show a confirmation dialog.
    '''

    delete_class = ''
    delete_url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'

    def delete_object(self, fail=False):
        '''
        Helper function to test deleting a workout
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerDeleteTestCase':
            return

        # Fetch the delete page
        count_before = self.delete_class.objects.count()
        response = self.client.get(reverse(self.delete_url, kwargs={'pk': self.pk}))
        count_after = self.delete_class.objects.count()
        self.assertEqual(count_before, count_after)
        
        if fail:
            self.assertIn(response.status_code, (403, 302))
        else:
            self.assertEqual(response.status_code, 200)

        # Try deleting the object
        response = self.client.post(reverse(self.delete_url, kwargs={'pk': self.pk}))
        count_after = self.delete_class.objects.count()

        if fail:
            self.assertIn(response.status_code, (403, 302))
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)
            self.assertRaises(self.delete_class.DoesNotExist,
                              self.delete_class.objects.get,
                              pk=self.pk)

    def test_delete_object_anonymous(self):
        '''
        Tests deleting the object as an anonymous user
        '''

        self.delete_object(fail=True)

    def test_delete_object_authorized(self):
        '''
        Tests deleting the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.delete_object(fail=False)

    def test_delete_object_other(self):
        '''
        Tests deleting the object as an unauthorized, logged in user
        '''

        self.user_login(self.user_fail)
        self.delete_object(fail=True)


class WorkoutManagerEditTestCase(WorkoutManagerTestCase):
    '''
    Tests editing an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    edit_url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'
    data_update = {}

    def edit_object(self, fail=False):
        '''
        Helper function to test editing an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerEditTestCase':
            return

        # Fetch the edit page
        response = self.client.get(reverse(self.edit_url, kwargs={'pk': self.pk}))
        entry_before = self.object_class.objects.get(pk=self.pk)

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Try to edit the object
        response = self.client.post(reverse(self.edit_url, kwargs={'pk': self.pk}),
                                    self.data_update)

        entry_after = self.object_class.objects.get(pk=1)

        # Check the results
        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')
            self.assertEqual(entry_before, entry_after)

        else:
            self.assertEqual(response.status_code, 302)
            for i in self.data_update:
                self.assertEqual(getattr(entry_after, i), self.data_update[i])

    def test_edit_object_anonymous(self):
        '''
        Tests editing the object as an anonymous user
        '''

        self.edit_object(fail=True)

    def test_edit_object_authorized(self):
        '''
        Tests editing the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.edit_object(fail=False)

    def test_edit_object_other(self):
        '''
        Tests editing the object as an unauthorized, logged in user
        '''

        self.user_login(self.user_fail)
        self.edit_object(fail=True)


class WorkoutManagerAddTestCase(WorkoutManagerTestCase):
    '''
    Tests adding an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'
    data = {}

    def add_object(self, fail=False):
        '''
        Helper function to test adding an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerAddTestCase':
            return

        # Fetch the add page
        response = self.client.get(reverse(self.url))

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Enter the data
        count_before = self.object_class.objects.count()
        response = self.client.post(reverse(self.url), self.data)
        count_after = self.object_class.objects.count()
        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

            self.assertRaises(self.object_class.DoesNotExist,
                              self.object_class.objects.get,
                              pk=self.pk)
            self.assertEqual(count_before, count_after)
            
        else:
            self.assertEqual(response.status_code, 302)
            entry = self.object_class.objects.get(pk=self.pk)
            for i in self.data:
                self.assertEqual(getattr(entry, i), self.data[i])

            self.assertEqual(count_before + 1, count_after)
            

    def test_add_object_anonymous(self):
        '''
        Tests adding the object as an anonymous user
        '''

        self.add_object(fail=True)

    def test_add_object_authorized(self):
        '''
        Tests adding the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.add_object(fail=False)

    def test_add_object_other(self):
        '''
        Tests adding the object as an unauthorized, logged in user
        '''

        self.user_login(self.user_fail)
        self.add_object(fail=True)
