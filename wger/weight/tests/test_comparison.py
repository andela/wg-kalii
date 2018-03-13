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

from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase

logger = logging.getLogger(__name__)


class WeightComparisonTestCase(WorkoutManagerTestCase):
    """
    Test case for the weight comparison page
    """

    def test_weight_comparison(self):
        """
        Test the weight comparison page
        """
        self.user_login('test')
        response = self.client.get(
            reverse('weight:comparison', kwargs={'username': self.current_user}))
        self.assertEqual(response.status_code, 200)

    def test_get_weight_data(self):
        """
        Test that user's weight can be gotten from the server
        """
        self.user_login('test')
        response = self.client.get(
            reverse('weight:weight-data', kwargs={'username': self.current_user}))
        self.assertEqual(response.status_code, 200)

    def test_get_comparison_weight_data(self):
        """
        Test that user's comparison weight can be gotten from the server
        """
        self.user_login('test')
        response = self.client.get(
            reverse('weight:comparison-weight-data', kwargs={'username': self.current_user}))
        self.assertEqual(response.status_code, 200)
