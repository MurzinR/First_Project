import time
import unittest
import requests


class AsyncTasksCase(unittest.TestCase):
    def test_add_task(self) -> None:
        """Проверяет json_add()"""
        self.assertEqual(requests.get('http://127.0.0.1:5000/add/{"name":"1"}').text, '{"status": "ok"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/add/{"name":"1"}').text, '{"status": "error"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/add/2').text, '{"status": "error"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"1"}')
        time.sleep(15)

    def test_search_task(self) -> None:
        """Проверяет json_search() (необходимо запустить rq worker asynctasks-tasks)"""
        requests.get('http://127.0.0.1:5000/add/{"name":"2"}')
        time.sleep(3)
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"2"}').text,
                         '{"status": "ok", "task": "2", "task_status": "in_progress"}')
        time.sleep(15)
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"2"}').text,
                         '{"status": "ok", "task": "2", "task_status": "done"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"3"}').text,
                         '{"status": "not_found", "task": null, "task_status": null}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/1').text,
                         '{"status": "error", "task": null, "task_status": null}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"2"}')

    def test_remove_task(self) -> None:
        """Проверяет json_remove()"""
        requests.get('http://127.0.0.1:5000/add/{"name":"4"}')
        requests.get('http://127.0.0.1:5000/add/{"name":"1"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/remove/{"name":"4"}').text, '{"status": "ok"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/remove/{"name":"4"}').text, '{"status": "not_found"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/remove/1').text, '{"status": "error"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"4"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"1"}')

    def test_async_tasks(self) -> None:
        """Проверяет асинхронность задач (требует запуска трех rq worker asynctasks-tasks)"""
        requests.get('http://127.0.0.1:5000/add/{"name":"5"}')
        requests.get('http://127.0.0.1:5000/add/{"name":"6"}')
        requests.get('http://127.0.0.1:5000/add/{"name":"7"}')
        time.sleep(15)
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"5"}').text,
                         '{"status": "ok", "task": "5", "task_status": "done"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"6"}').text,
                         '{"status": "ok", "task": "6", "task_status": "done"}')
        self.assertEqual(requests.get('http://127.0.0.1:5000/search/{"name":"7"}').text,
                         '{"status": "ok", "task": "7", "task_status": "done"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"5"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"6"}')
        requests.get('http://127.0.0.1:5000/remove/{"name":"7"}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
