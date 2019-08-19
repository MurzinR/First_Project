import json
import os
import time
import requests

link = os.environ.get('HOST_URL', 'http://127.0.0.1:5000')


class TestClass:
    def test_add_task_correct_input(self) -> None:
        """Проверяет json_add() с корректными входными данными"""
        global link
        r = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "1"})).text)
        assert r["status"] == "ok"
        requests.delete(link + '/tasks/' + r['id'])

    def test_add_task_incorrect_input_2(self) -> None:
        """Проверяет json_add() с некорректными входными данными"""
        global link
        assert json.loads(requests.post(link + '/tasks', json=json.dumps({"id": "1"})).text) == {
            "status": "error",
            "description": "incorrect json"}

    def test_search_task(self) -> None:
        """Проверяет json_search() (необходимо запустить rq worker asynctasks-tasks)"""
        global link
        time.sleep(10)
        task_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "2"})).text)['id']
        time.sleep(3)
        assert json.loads(requests.get(link + '/tasks/' + task_id).text) == {"status": "ok",
                                                                             'data': {'id': task_id,
                                                                                      'name': '2',
                                                                                      'status': 'in_progress'}}
        time.sleep(10)
        assert json.loads(requests.get(link + '/tasks/' + task_id).text) == {"status": "ok",
                                                                             'data': {'id': task_id,
                                                                                      'name': '2',
                                                                                      'status': 'done'}}
        assert requests.get(link + '/tasks/1').status_code == 404
        requests.delete(link + '/tasks/' + task_id)

    def test_remove_task(self) -> None:
        """Проверяет json_remove()"""
        global link
        task4_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "4"})).text)['id']
        assert json.loads(requests.delete(link + '/tasks/' + task4_id).text) == {"status": "ok"}
        assert requests.delete(link + '/tasks/1').status_code == 404
        requests.delete(link + '/tasks/' + task4_id)

    def test_async_tasks(self) -> None:
        """Проверяет асинхронность задач (требует запуска трех rq worker asynctasks-tasks)"""
        global link
        time.sleep(10)
        task5_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "5"})).text)['id']
        task6_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "6"})).text)['id']
        task7_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "7"})).text)['id']
        time.sleep(20)
        assert json.loads(requests.get(link + '/tasks/' + task5_id).text) == {"status": "ok",
                                                                              'data': {'id': task5_id,
                                                                                       'name': '5',
                                                                                       'status': 'done'}}
        assert json.loads(requests.get(link + '/tasks/' + task6_id).text) == {"status": "ok",
                                                                              'data': {'id': task6_id,
                                                                                       'name': '6',
                                                                                       'status': 'done'}}
        assert json.loads(requests.get(link + '/tasks/' + task7_id).text) == {"status": "ok",
                                                                              'data': {'id': task7_id,
                                                                                       'name': '7',
                                                                                       'status': 'done'}}
        requests.delete(link + '/tasks/' + task5_id)
        requests.delete(link + '/tasks/' + task6_id)
        requests.delete(link + '/tasks/' + task7_id)
