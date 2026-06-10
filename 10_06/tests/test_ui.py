import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = 'https://www.demoblaze.com'

def test_homepage_loads(driver):
    """TC-UI-01: Главная страница открывается корректно."""
    driver.get(BASE)
    time.sleep(1)
    assert 'STORE' in driver.title, f'Неверный заголовок: {driver.title}'
    
    logo = driver.find_element(By.CLASS_NAME, 'navbar-brand')
    assert logo.is_displayed(), 'Логотип не отображается'
    
    items = driver.find_elements(By.CLASS_NAME, 'card-title')
    assert len(items) > 0, 'Товары на главной странице не найдены'
    
    driver.save_screenshot('report/tc_ui_01.png')
    print(f'\n[OK] Заголовок: {driver.title}, товаров: {len(items)}')


def test_successful_login(driver):
    """TC-UI-02: Успешная авторизация пользователя."""
    driver.get(BASE)
    wait = WebDriverWait(driver, 10)
    

    unique_username = f"VladQA_{int(time.time())}"
    password = "MyPassword123!"
    
    driver.find_element(By.ID, 'signin2').click()
    wait.until(EC.visibility_of_element_located((By.ID, 'sign-username')))
    
    driver.find_element(By.ID, 'sign-username').send_keys(unique_username)
    driver.find_element(By.ID, 'sign-password').send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Sign up']").click()
    
    alert = wait.until(EC.alert_is_present())
    alert.accept()
    
    time.sleep(1)
    
    driver.find_element(By.ID, 'login2').click()
    wait.until(EC.visibility_of_element_located((By.ID, 'loginusername')))
    
    driver.find_element(By.ID, 'loginusername').send_keys(unique_username)
    driver.find_element(By.ID, 'loginpassword').send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()
    
    wait.until(EC.visibility_of_element_located((By.ID, 'logout2')))
    logout_btn = driver.find_element(By.ID, 'logout2')
    assert logout_btn.is_displayed(), 'Кнопка Log out не появилась после входа'
    
    driver.save_screenshot('report/tc_ui_02.png')


def test_login_wrong_password(driver):
    """TC-UI-03: Отказ при неверном пароле."""
    driver.get(BASE)
    driver.find_element(By.ID, 'login2').click()
    
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'loginusername'))
    )
    driver.find_element(By.ID, 'loginusername').send_keys('testuser1')
    driver.find_element(By.ID, 'loginpassword').send_keys('wrongpassword')
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()
    
    try:
        alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
        msg = alert.text
        alert.accept()
        driver.save_screenshot('report/tc_ui_03.png')
        print(f'\n[OK] Сообщение об ошибке получено: {msg}')
    except:
        driver.save_screenshot('report/tc_ui_03_fail.png')
        pytest.fail('Ожидался alert с сообщением об ошибке входа')


def test_add_to_cart(driver):
    """TC-UI-04: Добавление товара в корзину с предусловием авторизации."""
    driver.get(BASE)
    wait = WebDriverWait(driver, 10)
    
    unique_username = f"CartUser_{int(time.time())}"
    password = "CartPassword123!"
    
    driver.find_element(By.ID, 'signin2').click()
    wait.until(EC.visibility_of_element_located((By.ID, 'sign-username')))
    driver.find_element(By.ID, 'sign-username').send_keys(unique_username)
    driver.find_element(By.ID, 'sign-password').send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Sign up']").click()
    
    alert = wait.until(EC.alert_is_present())
    alert.accept()
    time.sleep(1) 
    
    driver.find_element(By.ID, 'login2').click()
    wait.until(EC.visibility_of_element_located((By.ID, 'loginusername')))
    driver.find_element(By.ID, 'loginusername').send_keys(unique_username)
    driver.find_element(By.ID, 'loginpassword').send_keys(password)
    driver.find_element(By.XPATH, "//button[text()='Log in']").click()
    wait.until(EC.visibility_of_element_located((By.ID, 'logout2'))) 
    
    first_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'card-title')))
    first_item.find_element(By.XPATH, './..').click()
    
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Add to cart']")))
    add_btn.click()
    
    product_alert = wait.until(EC.alert_is_present())
    assert 'added' in product_alert.text.lower(), f'Неожиданный alert: {product_alert.text}'
    product_alert.accept()
    
    driver.save_screenshot('report/tc_ui_04.png')


def test_category_filter(driver):
    """TC-UI-05: Фильтрация каталога по категории 'Phones'."""
    driver.get(BASE)
    time.sleep(2)  # Ждем первичной загрузки каталога
    
    all_items = driver.find_elements(By.CLASS_NAME, 'card-title')
    count_before = len(all_items)
    
    phones_link = driver.find_element(By.LINK_TEXT, 'Phones')
    phones_link.click()
    time.sleep(2)  # Ждем обновления элементов каталога
    
    filtered_items = driver.find_elements(By.CLASS_NAME, 'card-title')
    count_after = len(filtered_items)
    
    assert count_after > 0, 'После фильтрации не отображается ни одного товара'
    assert count_after <= count_before, 'Фильтр не уменьшил количество товаров'
    
    driver.save_screenshot('report/tc_ui_05.png')
    print(f'\nБыло: {count_before}, стало после фильтра: {count_after}')