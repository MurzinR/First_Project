import json
import time
import requests


class TestClass:
    def test_add_task_correct_input(self) -> None:
        """Проверяет json_add() с корректными входными данными"""
        r = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "1"})).text)
        assert r["status"] == "ok"
        requests.delete('http://127.0.0.1:5000/tasks/' + r['id'])

    def test_add_task_incorrect_input_2(self) -> None:
        """Проверяет json_add() с некорректными входными данными"""
        assert json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"id": "1"})).text) == {
            "status": "error",
            "description": "incorrect json"}

    def test_search_task(self) -> None:
        """Проверяет json_search() (необходимо запустить rq worker asynctasks-tasks)"""
        time.sleep(10)
        task_id = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "2"})).text)['id']
        time.sleep(3)
        assert json.loads(requests.get('http://127.0.0.1:5000/tasks/' + task_id).text) == {"status": "ok",
                                                                                           "task": "2",
                                                                                           "task_status":  {'__enum__': 'Status.in_progress'}}
        time.sleep(10)
        assert json.loads(requests.get('http://127.0.0.1:5000/tasks/' + task_id).text) == {"status": "ok",
                                                                                           "task": "2",
                                                                                           "task_status":  {'__enum__': 'Status.done'}}
        assert requests.get('http://127.0.0.1:5000/tasks/1').status_code == 404

    def test_remove_task(self) -> None:
        """Проверяет json_remove()"""
        task4_id = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "4"})).text)['id']
        assert json.loads(requests.delete('http://127.0.0.1:5000/tasks/' + task4_id).text) == {"status": "ok"}
        assert requests.delete('http://127.0.0.1:5000/tasks/1').status_code == 404
        requests.delete('http://127.0.0.1:5000/tasks/' + task4_id)

    def test_async_tasks(self) -> None:
        """Проверяет асинхронность задач (требует запуска трех rq worker asynctasks-tasks)"""
        time.sleep(10)
        task5_id = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "5"})).text)['id']
        task6_id = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "6"})).text)['id']
        task7_id = json.loads(requests.post('http://127.0.0.1:5000/tasks', json=json.dumps({"name": "7"})).text)['id']
        time.sleep(20)
        assert json.loads(requests.get('http://127.0.0.1:5000/tasks/' + task5_id).text) == {"status": "ok",
                                                                                            "task": "5",
                                                                                            "task_status":  {'__enum__': 'Status.done'}}
        assert json.loads(requests.get('http://127.0.0.1:5000/tasks/' + task6_id).text) == {"status": "ok",
                                                                                            "task": "6",
                                                                                            "task_status":  {'__enum__': 'Status.done'}}
        assert json.loads(requests.get('http://127.0.0.1:5000/tasks/' + task7_id).text) == {"status": "ok",
                                                                                            "task": "7",
                                                                                            "task_status":  {'__enum__': 'Status.done'}}
        requests.delete('http://127.0.0.1:5000/tasks/' + task5_id)
        requests.delete('http://127.0.0.1:5000/tasks/' + task6_id)
        requests.delete('http://127.0.0.1:5000/tasks/' + task7_id)
