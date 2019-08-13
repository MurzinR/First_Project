import time
import requests


class TestClass:
    def test_add_task_correct_input(self) -> None:
        """Проверяет json_add() с корректными входными данными"""
        assert requests.post('http://127.0.0.1:5000/tasks/{"name":"1"}').text == '{"status": "ok"}'

    def test_add_task_incorrect_input_1(self) -> None:
        """Проверяет json_add() с некорректными входными данными"""
        assert requests.post('http://127.0.0.1:5000/tasks/{"name":"1"}').text == '{"status": "error", "description": ' \
                                                                                 '"task_already_exists"}'
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"1"}')

    def test_add_task_incorrect_input_2(self) -> None:
        """Проверяет json_add() с некорректными входными данными"""
        assert requests.post('http://127.0.0.1:5000/tasks/2').text == '{"status": "error", "description": ' \
                                                                      '"incorrect json"}'

    def test_search_task(self) -> None:
        """Проверяет json_search() (необходимо запустить rq worker asynctasks-tasks)"""
        time.sleep(10)
        requests.post('http://127.0.0.1:5000/tasks/{"name":"2"}')
        time.sleep(3)
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"2"}').text == '{"status": "ok", "task": "2", ' \
                                                                                '"task_status": "in_progress"}'
        time.sleep(10)
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"2"}').text == '{"status": "ok", "task": "2", ' \
                                                                                '"task_status": "done"}'
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"3"}').text == '{"status": "not_found", "task": ' \
                                                                                'null, "task_status": null}'
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"2"}')
        assert requests.get('http://127.0.0.1:5000/tasks/1').text == '{"status": "error", "description": ' \
                                                                     '"incorrect json"}'

    def test_remove_task(self) -> None:
        """Проверяет json_remove()"""
        requests.post('http://127.0.0.1:5000/tasks/{"name":"4"}')
        requests.post('http://127.0.0.1:5000/tasks/{"name":"1"}')
        assert requests.delete('http://127.0.0.1:5000/tasks/{"name":"4"}').text == '{"status": "ok"}'
        assert requests.delete('http://127.0.0.1:5000/tasks/{"name":"4"}').text == '{"status": "not_found"}'
        assert requests.delete('http://127.0.0.1:5000/tasks/1').text == '{"status": "error", "description": ' \
                                                                        '"incorrect json"}'
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"4"}')
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"1"}')

    def test_async_tasks(self) -> None:
        """Проверяет асинхронность задач (требует запуска трех rq worker asynctasks-tasks)"""
        time.sleep(10)
        requests.post('http://127.0.0.1:5000/tasks/{"name":"5"}')
        requests.post('http://127.0.0.1:5000/tasks/{"name":"6"}')
        requests.post('http://127.0.0.1:5000/tasks/{"name":"7"}')
        time.sleep(20)
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"5"}').text == '{"status": "ok", "task": "5", ' \
                                                                                '"task_status": "done"}'
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"6"}').text == '{"status": "ok", "task": "6", ' \
                                                                                '"task_status": "done"}'
        assert requests.get('http://127.0.0.1:5000/tasks/{"name":"7"}').text == '{"status": "ok", "task": "7", ' \
                                                                                '"task_status": "done"}'
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"5"}')
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"6"}')
        requests.delete('http://127.0.0.1:5000/tasks/{"name":"7"}')
