#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.page import Page
from pages.base_page import MozTrapBasePage
from pages.create_run_page import MozTrapEditRunPage


class MozTrapManageRunsPage(MozTrapBasePage):

    _page_title = 'MozTrap'

    _filter_input_locator = (By.ID, 'text-filter')
    _filter_suggestion_locator = (By.CSS_SELECTOR, '#filter .textual .suggest .suggestion[data-type="name"][data-name="%(filter_name)s"]')
    _filter_locator = (By.CSS_SELECTOR, '#filterform .filter-group input[data-name="name"][value="%(filter_name)s"]:checked')
    _run_item_locator = (By.CSS_SELECTOR, '#manageruns .itemlist .listitem')
    _new_run_button_locator = (By.LINK_TEXT, 'create a test run')

    def go_to_manage_runs_page(self):
        self.selenium.get(self.base_url + '/manage/runs/')
        self.is_the_current_page

    def click_add_run(self):
        self.selenium.find_element(*self._new_run_button_locator).click()
        from pages.create_run_page import MozTrapCreateRunPage
        return MozTrapCreateRunPage(self.testsetup)

    def filter_runs_by_name(self, name):
        _filter_suggestion_locator = (self._filter_suggestion_locator[0], self._filter_suggestion_locator[1] % {'filter_name': name})

        self.selenium.find_element(*self._filter_input_locator).send_keys(name)
        self.selenium.find_element(*_filter_suggestion_locator).click()
        self.wait_for_ajax()

    def remove_name_filter(self, name):
        _filter_locator = (self._filter_locator[0], self._filter_locator[1] % {'filter_name': name.lower()})

        self.selenium.find_element(*self._filter_locator).click()
        self.wait_for_ajax()

    @property
    def get_runs(self):
        runs = self.selenium.find_elements(*self._run_item_locator)
        return [self.Run(self.testsetup, run) for run in runs]

    class Run(Page):
        _delete_run_locator = (By.CSS_SELECTOR, '.action-delete')
        _run_activate_locator = (By.CSS_SELECTOR, '.status-action.active')
        _run_status_locator = (By.CSS_SELECTOR, '.status-title')
        _edit_run_locator = (By.CSS_SELECTOR, 'a.edit-link')

        def __init__(self, testsetup, webelement):
            Page.__init__(self, testsetup)
            self.webelement = webelement

        def delete(self):
            self.webelement.find_element(*self._delete_run_locator).click()
            self.wait_for_ajax()

        def edit(self):
            self.webelement.find_element(*self._edit_run_locator).click()
            return MozTrapEditRunPage(self.testsetup)

        def activate(self):
            self.webelement.find_element(*self._run_status_locator).click()
            self.webelement.find_element(*self._run_activate_locator).click()
            self.wait_for_ajax()
