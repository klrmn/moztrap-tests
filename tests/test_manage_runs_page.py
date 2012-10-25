#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from unittestzero import Assert

from pages.base_test import BaseTest
from pages.manage_runs_page import MozTrapManageRunsPage


class TestManageRunsPage(BaseTest):

    @pytest.mark.xfail(reason="Bug 795283 - [dev] https://moztrap-dev.allizom.org/manage/suite/add/ returns 503[Service Unavailable]")
    def test_that_user_can_create_and_delete_run(self, mozwebqa_logged_in):
        manage_runs_pg = MozTrapManageRunsPage(mozwebqa_logged_in)

        run = self.create_run(mozwebqa_logged_in)

        manage_runs_pg.filter_runs_by_name(name=run['name'])

        runs = manage_runs_pg.get_runs
        Assert.equal(len(runs), 1)

        runs[0].delete()

        runs = manage_runs_pg.get_runs
        Assert.equal(len(runs), 0)

        self.delete_version(mozwebqa_logged_in, version=run['version'], delete_product=True)

    @pytest.mark.moztrap(2929)
    @pytest.mark.native
    def test_edit_existing_run_that_includes_suites(self, mozwebqa_logged_in):
        # setup
        product = self.create_product(mozwebqa_logged_in)
        suite1 = self.create_suite(mozwebqa_logged_in, product=product)
        suite2 = self.create_suite(mozwebqa_logged_in, product=product)
        case1 = self.create_case(mozwebqa_logged_in,
            product=product, version=product['version'], suite_name=suite1['name'])
        case2 = self.create_case(mozwebqa_logged_in,
            product=product, version=product['version'], suite_name=suite1['name'])
        case3 = self.create_case(mozwebqa_logged_in,
            product=product, version=product['version'], suite_name=suite2['name'])
        case4 = self.create_case(mozwebqa_logged_in,
            product=product, version=product['version'], suite_name=suite2['name'])
        run = self.create_run(mozwebqa_logged_in,
            product=product, version=product['version'],
            suite_name_list=[suite1['name']])

        # go to manage runs page
        manage_runs_pg = MozTrapManageRunsPage(mozwebqa_logged_in)
        # find the run
        manage_runs_pg.filter_runs_by_name(name=run['name'])
        runs = manage_runs_pg.get_runs
        # click edit
        edit_run_pg = runs[0].edit()

        # not yet deployed to stage
        # assert edit_run_pg.product_version == run['product_version']
        assert suite1['name'] in edit_run_pg.included_suite_names
        assert suite2['name'] in edit_run_pg.available_suite_names

        # add suite2 to the run
        edit_run_pg.add_suite(suite2['name'])
        # re-order suites to run suite2 first
        edit_run_pg.drag_and_drop_suite(suite2['name'], suite1['name'])
        # save
        manage_runs_pg = edit_run_pg.click_save()
        # click edit
        manage_runs_pg.filter_runs_by_name(name=run['name'])
        runs = manage_runs_pg.get_runs
        edit_run_pg = runs[0].edit()
        expected = [suite2['name'], suite1['name']]
        actual = edit_run_pg.included_suite_names
        assert actual == expected

        # teardown
        self.delete_run(mozwebqa_logged_in, run)
        for case in [case1, case2, case3, case4]:
            self.delete_case(mozwebqa_logged_in, case)
        for suite in [suite1, suite2]:
            self.delete_suite(mozwebqa_logged_in, suite)
        self.delete_product(mozwebqa_logged_in, product)
