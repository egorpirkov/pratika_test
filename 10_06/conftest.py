import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope='function')
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1280,800')
    # options.add_argument('--headless') # Раскомментируй для запуска без открытия окна браузера
    
    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    drv.implicitly_wait(10)
    yield drv
    drv.quit()