import json
import os
import time
import requests

link = os.environ.get('HOST_URL', 'http://127.0.0.1:5000')


class TestClass:
    def test_add_task_correct_input(self) -> None:
        """Проверяет json_add() с корректными входными данными"""
        global link
        r = requests.post(link + '/tasks', json=json.dumps({"name": "1"}))
        assert r.status_code == 200
        answer = json.loads(r.text)
        assert answer["ok"]
        requests.delete(link + '/tasks/' + answer['data']['id'])

    def test_add_task_incorrect_input_2(self) -> None:
        """Проверяет json_add() с некорректными входными данными"""
        global link
        assert json.loads(requests.post(link + '/tasks', json=json.dumps({"id": "1"})).text) == {"ok": False,
                                                                                                 "issues": "incorrect json",
                                                                                                 "message": None}

    def test_search_task(self) -> None:
        """Проверяет json_search() (необходимо запустить rq worker asynctasks-tasks)"""
        global link
        time.sleep(10)
        task_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "2"})).text)['data']['id']
        time.sleep(3)
        r = requests.get(link + '/tasks/' + task_id)
        assert r.status_code == 200
        assert json.loads(r.text) == {"ok": True,
                                      'data': {'id': task_id,
                                               'name': '2',
                                               'status': 'in_progress'},
                                      'message': None}
        time.sleep(10)
        r = requests.get(link + '/tasks/' + task_id)
        assert r.status_code == 200
        assert json.loads(r.text) == {"ok": True,
                                      'data': {'id': task_id,
                                               'name': '2',
                                               'status': 'done'},
                                      'message': None}
        assert requests.get(link + '/tasks/1').status_code == 404
        requests.delete(link + '/tasks/' + task_id)

    def test_remove_task(self) -> None:
        """Проверяет json_remove()"""
        global link
        task4_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "4"})).text)['data']['id']
        r = requests.delete(link + '/tasks/' + task4_id)
        assert r.status_code == 200
        assert json.loads(r.text) == {'ok': True,
                                      'data': 'ok',
                                      'message': None}
        assert requests.delete(link + '/tasks/1').status_code == 404
        requests.delete(link + '/tasks/' + task4_id)

    def test_async_tasks(self) -> None:
        """Проверяет асинхронность задач (требует запуска трех rq worker asynctasks-tasks)"""
        global link
        time.sleep(10)
        task5_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "5"})).text)['data']['id']
        task6_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "6"})).text)['data']['id']
        task7_id = json.loads(requests.post(link + '/tasks', json=json.dumps({"name": "7"})).text)['data']['id']
        time.sleep(20)
        assert json.loads(requests.get(link + '/tasks/' + task5_id).text) == {"ok": True,
                                                                              'data': {'id': task5_id,
                                                                                       'name': '5',
                                                                                       'status': 'done'},
                                                                              'message': None}
        assert json.loads(requests.get(link + '/tasks/' + task6_id).text) == {"ok": True,
                                                                              'data': {'id': task6_id,
                                                                                       'name': '6',
                                                                                       'status': 'done'},
                                                                              'message': None}
        assert json.loads(requests.get(link + '/tasks/' + task7_id).text) == {"ok": True,
                                                                              'data': {'id': task7_id,
                                                                                       'name': '7',
                                                                                       'status': 'done'},
                                                                              'message': None}
        requests.delete(link + '/tasks/' + task5_id)
        requests.delete(link + '/tasks/' + task6_id)
        requests.delete(link + '/tasks/' + task7_id)
