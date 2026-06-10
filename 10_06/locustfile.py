from locust import HttpUser, task, between

class ShopUser(HttpUser):
    wait_time = between(1, 3)  # Пауза между запросами пользователя (от 1 до 3 секунд)
    host = 'https://www.demoblaze.com'

    @task(3)  # Вес 3 — этот сценарий выполняется чаще всего
    def view_homepage(self):
        with self.client.get('/', catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f'Главная: ожидался 200, получен {r.status_code}')

    @task(2)  # Вес 2 — средний приоритет
    def view_category(self):
        self.client.post('/bycat', json={'cat': 'phone'})

    @task(1)  # Вес 1 — низкий приоритет
    def view_product(self):
        self.client.post('/view', json={'id': '1'})

    @task(1)  # Вес 1 — низкий приоритет
    def check_cart(self):
        self.client.post('/viewcart', json={'cookie': 'guest', 'flag': True})