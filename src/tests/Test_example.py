import allure
import pytest

from page_objects.main_screen import main_screen
from tests.conftest import get_url


@pytest.mark.usefixtures("driver", "url_fixture")
class Test_example:

    @allure.feature('url testing')
    @allure.story('get title from selected url')
    @pytest.mark.regression
    @pytest.mark.run(order=1)
    def test_get_title_from_url(self, driver,url_fixture):

        # Object #1 - Cyrebro Main Page
        main_page = main_screen(driver, get_url(url_fixture).get("main"))
        main_page.go_to()