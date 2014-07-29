import lettuce
from flask import url_for
from selenium import webdriver
from rheTOracle import app


@lettuce.before.all
def setup_app():
    print "This happens before all the lettuce tests begin"
    site_url = 'localhost:5000'
    driver = webdriver.Chrome()
    driver.get(site_url)
    lettuce.world.driver = driver

@lettuce.after.each.scenario
def close_modals(scenario):
    driver = lettuce.world.driver
    driver.execute_script(
        """
        $("#about-modal").modal("hide");
        $("#reTOracle-modal").modal("hide");
        """
        )
    time.sleep(3)

@lettuce.after.each_step
def wait(step):
    time.sleep(1)

@lettuce.after.each_feature
def close_driver(feature):
    driver = lettuce.world.driver
    driver.close()

@lettuce.step('I click the About button')
def about_button(step):
    driver = lettuce.world.driver
    driver.find_element_by_id('about').click()

@lettuce.step('Then I see the About page')
def about_page(step):
    driver = lettuce.world.driver
    assert driver.find_element_by_id('about').is_displayed()


@lettuce.step('I click the reTOracle button')
def retoracle_button(step):
    driver = lettuce.world.driver
    driver.find_element_by_id('rhetoracle').click()

@lettuce.step('Then I see the page refreshes')
def retoracle_refresh(step):
    driver = lettuce.world.driver
    assert driver.find_element_by_id('home').is_displayed()

# need to add selenium to requirements







