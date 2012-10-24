#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from pages.page import Page
from pages.base_page import MozTrapBasePage

class MozTrapEditRunPage(MozTrapBasePage):
    _known_kwargs = ['name', 'desc', 'start_date', 'end_date', 'suite_list']
    _product_version_readonly_locator = (By.CSS_SELECTOR, 'div.formfield.product-version-field.readonly > span')
    _name_locator = (By.ID, 'id_name')
    _description_locator = (By.ID, 'id_description')
    _start_date_locator = (By.ID, 'id_start')
    _end_date_locator = (By.ID, 'id_end')
    _available_suites_locator = (By.CSS_SELECTOR, '.multiunselected .itemlist article.selectitem')
    _included_suites_locator = (By.CSS_SELECTOR, '.multiselected .itemlist article.selectitem')
    _include_selected_suites_locator = (By.CSS_SELECTOR, '.multiselect .include-exclude .action-include')
    _remove_selected_suites_locator = (By.CSS_SELECTOR, '.multiselect .include-exclude .action-exclude')
    _submit_locator = (By.CSS_SELECTOR, '#run-add-form .form-actions > button')

    # Note on __init__: it fails with 'ReferenceError: jQuery is not defined' 
    # if you try to wait_for_ajax

    def fill_fields(self, **kwargs):
        '''
        ::keyword args::
        name
        desc
        start_date
        end_date
        suite_list
        '''
        
        for key in kwargs.keys():
            if not key in self._known_kwargs:
                raise Exception("%s unrecognized, use only recognized kwargs:\n%s" %
                    (key, "\n".join(self._known_kwargs)))

        if kwargs.has_key('name'):
            name_field = self.selenium.find_element(*self._name_locator)
            name_field.send_keys(kwargs['name'])
        if kwargs.has_key('desc'):
            self.selenium.find_element(*self._description_locator).send_keys(kwargs['desc'])
        if kwargs.has_key('start_date'):
            self.type_in_element(self._start_date_locator, kwargs['start_date'])
        if kwargs.has_key('end_date'):
            self.selenium.find_element(*self._end_date_locator).send_keys(kwargs['end_date'])

        if kwargs.has_key('suite_list') and kwargs['suite_list']:
            # remove unwanted
            for suite in self.included_suites:
                print 'included has %s' % suite.name
                if not suite.name in kwargs['suite_list']:
                    print 'selecting for removal'
                    suite.select()
            self.remove_selected_suites()
            # add wanted
            for suite in self.available_suites:
                print 'available has %s' % suite.name
                if suite.name in kwargs['suite_list']:
                    print 'selecting for addition'
                    suite.select()
            self.add_selected_suites()
            # check for strays
            included_suite_names = self.included_suite_names
            for suite_name in kwargs['suite_list']:
                if not suite_name in included_suite_names:
                    raise Exception('suite %s not found' % suite_name)

        self.selenium.find_element(*self._submit_locator).click()

    @property
    def product_version(self):
        return self.selenium.find_element(*self._product_version_readonly_locator).text

    @property
    def included_suites(self):
        '''this method only works if run is in draft mode.'''
        suites = self.selenium.find_elements(*self._included_suites_locator)
        included_suites = [self.Suite(self.testsetup, loc) for loc in suites]
        print 'included_suites:\n%s' % included_suites
        return included_suites

    @property
    def included_suite_names(self):
        # XXX fix this so that it returns something when run is active
        included_suite_names = [suite.name for suite in self.included_suites]
        print 'included_suite_names:\n%s' % included_suite_names
        return included_suite_names

    def remove_selected_suites(self):
        '''this method only works if run is in draft mode.'''
        self.selenium.find_element(*self._remove_selected_suites_locator).click()

    @property
    def available_suites(self):
        '''this method only works if run is in draft mode.'''
        suites = self.selenium.find_elements(*self._available_suites_locator)
        return [self.Suite(self.testsetup, loc) for loc in suites]

    @property
    def available_suite_names(self):
        '''this method only works if run is in draft mode.'''
        return [suite.name for suite in self.available_suites]

    def add_selected_suites(self):
        '''this method only works if run is in draft mode.'''
        self.selenium.find_element(*self._include_selected_suites_locator).click()
        
    class Suite(Page):
        _name_locator = (By.CSS_SELECTOR, 'div.name > h5.title')
        _checkbox_locator = (By.CSS_SELECTOR, 'label.bulk-type')
        _drag_locator = (By.CSS_SELECTOR, )

        def __init__(self, testsetup, webelement):
            Page.__init__(self, testsetup)
            self.webelement = webelement

        @property
        def name(self):
            return self.webelement.find_element(*self._name_locator).text

        @property
        def position(self):
            pass

        def select(self):
            self.webelement.find_element(*self._checkbox_locator).click()

        def drag_to(self, position):
            pass


class MozTrapCreateRunPage(MozTrapEditRunPage):

    _page_title = 'MozTrap'

    _product_version_select_locator = (By.ID, 'id_productversion')
    _run_manage_locator = (By.CSS_SELECTOR, '#manageruns .itemlist .listitem .title[title="%(run_name)s"]')
    _run_homepage_locator = (By.CSS_SELECTOR, '.runsdrill .runsfinder .runs .colcontent .title[title="%(run_name)s"]')
    _run_tests_button_locator = (By.CSS_SELECTOR, 'div.form-actions > button')

    def __init__(self, testsetup):
        MozTrapEditRunPage.__init__(self, testsetup)
        self._known_kwargs.append('product_version')

    def go_to_create_run_page(self):
        self.selenium.get(self.base_url + '/manage/run/add/')
        self.is_the_current_page

    def fill_fields(self, **kwargs):
        '''
        ::keyword args::
        name
        product_version
        desc
        start_date
        end_date
        suite_list
        '''

        if kwargs.has_key('product_version'):
            product_version_select = Select(self.selenium.find_element(*self._product_version_select_locator))
            product_version_select.select_by_visible_text(kwargs['product_version'])

        MozTrapEditRunPage.fill_fields(self, **kwargs)


    def create_run(self, 
            name='Test Run', 
            product_version='Test Product Test Version', 
            desc='This is a test run', 
            start_date='2011-01-01', 
            end_date='2012-12-31', 
            suite_list=None):
        '''
        ::keyword args::
        name
        product_version
        desc
        start_date
        end_date
        suite_list
        '''
        dt_string = datetime.utcnow().isoformat()
        run = {}
        run['name'] = u'%(name)s %(dt_string)s' % {'name': name, 'dt_string': dt_string}
        run['desc'] = u'%(desc)s created on %(dt_string)s' % {'desc': desc, 'dt_string': dt_string}
        run['manage_locator'] = (self._run_manage_locator[0], self._run_manage_locator[1] % {'run_name': run['name']})
        run['homepage_locator'] = (self._run_homepage_locator[0], self._run_homepage_locator[1] % {'run_name': run['name']})
        run['run_tests_locator'] = self._run_tests_button_locator

        self.fill_fields(
            name=run['name'],
            product_version=product_version,
            desc=run['desc'],
            start_date=start_date,
            end_date=end_date,
            suite_list=suite_list)

        return run
