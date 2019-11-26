import datetime
from django.urls import reverse
from django.test import TestCase, Client
from django.utils import timezone

from .models import User, Project, Sprint, ProductBacklogItem, Task

def create_project(name, desc):
    return Project.objects.create(name=name, desc=desc)

def create_sprint(number, project):
    start_date = timezone.now()
    # project = Project.objects.create(name=project_name)
    return Sprint.objects.create(number=number, start_date=start_date, project=project)

def create_pbi(name, desc, priority, storypoints, status, project, sprint):
    return ProductBacklogItem.objects.create(name=name, desc=desc, priority=priority, storypoints=storypoints, status=status, project=project, sprint=sprint)

def create_pbi_not_in_sprint(name, desc, priority, storypoints, status, project):
    return ProductBacklogItem.objects.create(name=name, desc=desc, priority=priority, storypoints=storypoints, status=status, project=project)

def create_task(name, desc, burndown, est, status, pbi):
    return Task.objects.create(name=name, desc=desc, burndown=burndown, estimate=est, status=status, pbi=pbi)


class NewProjectViewTest(TestCase):
    def test_no_project(self):
        response = self.client.get(reverse('backtrack:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects currently")
        self.assertQuerysetEqual(response.context['projects'], [])

    def test_one_project(self):
        proj = create_project(name="Test project", desc="this is a project for testing.")
        response = self.client.get(reverse('backtrack:index'))
        self.assertQuerysetEqual(response.context['projects'], ['<Project: Test project>'])
        self.assertEqual(proj.name, "Test project")
        self.assertEqual(proj.desc, "this is a project for testing.")


class ProjectPBViewTest(TestCase):
    def test_no_pbi(self):
        project = create_project(name="Test project", desc="this is a project for testing.")
        sprint = create_sprint(number=1, project=project)
        url = reverse('backtrack:project_pb', args=(project.id,))
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['pbi_set'], [])

    def test_pbi_with_abnormal_priority(self):
        project = create_project(name="Test project", desc="this is a project for testing.")
        sprint = create_sprint(number=1, project=project)
        # The pbi view of one pbi with priority 3
        pbi = create_pbi(name='pbi1', desc="pbi for testing", priority=3, storypoints=20, status='NS', project=project, sprint=sprint)
        url = reverse('backtrack:project_pb', args=(project.id,))
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['pbi_set'], ProductBacklogItem.objects.all(), transform=lambda x: x)
        # priority out of bound l104

    def test_two_pbis(self):
        project = create_project(name="Test project", desc="this is a project for testing.")
        sprint = create_sprint(number=1, project=project)
        pbi1 = create_pbi(name='pbi1', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        pbi2 = create_pbi(name='pbi2', desc="pbi for testing", priority=2, storypoints=20, status='NS', project=project, sprint=sprint)
        url = reverse('backtrack:project_pb', args=(project.id,))
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['pbi_set'], ProductBacklogItem.objects.all(), transform=lambda x: x)
        self.assertEqual(pbi1.priority, 1)
        self.assertEqual(pbi2.priority, 2)

    def test_delete_pbi(self):
        project = create_project(name="Test project", desc="this is a project for testing.")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi1', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        pbi.delete()
        url = reverse('backtrack:project_pb', args=(project.id,))
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['pbi_set'], [])


class SprintBacklogViewTest(TestCase):
    def test_no_pbi_in_sb(self):
        project = create_project(name="Test project", desc="this is a project for testing.")
        sprint = create_sprint(number=1, project=project)
        pbi1 = create_pbi_not_in_sprint(name='pbi1', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project)
        url = reverse('backtrack:project_sb', args=(sprint.id,))
        response = self.client.get(url)
        # for pbi in productbacklogitem_set:
        #     self.assertEqual(response.status_code, 200)
        # self.assertQuerysetEqual(response.context['sprint.pbi_set'], [])
        self.assertContains(response, "No Product Backlog Items in Sprint yet")

    def test_one_pbi_in_sprint(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi1 = create_pbi(name='pbi1', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        url = reverse('backtrack:project_sb', args=(sprint.id,))
        response = self.client.get(url)
        self.assertContains(response, "pbi1")

    def test_two_pbis_in_sprint(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi1 = create_pbi(name='pbi1', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        pbi2 = create_pbi(name='pbi2', desc="pbi for testing", priority=2, storypoints=30, status='NS', project=project, sprint=sprint)
        url = reverse('backtrack:project_sb', args=(sprint.id,))
        response = self.client.get(url)
        # self.assertQuerysetEqual(response.context['sprint.productbacklogitem_set'], ['<ProductBacklogItem: pbi2>', '<ProductBacklogItem: pbi1>'])
        self.assertContains(response, "pbi1")
        self.assertContains(response, "pbi2")


class NewTaskViewTest(TestCase):
    def test_no_task(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        url = reverse('backtrack:new_task', args=(sprint.id,))
        response = self.client.get(url)
        # self.assertQuerysetEqual(response.context['pbi.task_set'], [])
        self.assertContains(response, "No Tasks for PBI yet")

    def test_one_task(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        task = create_task(name='task', desc='for testing', burndown=10, est=10, status='NS', pbi=pbi)
        url = reverse('backtrack:new_task', args=(pbi.id,))
        response = self.client.get(url)
        # self.assertQuerysetEqual(response.context['pbi.task_set'], ['<Task: task>'])
        self.assertContains(response, "task")

    def test_three_tasks(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        task1 = create_task(name='task1', desc='for testing.', burndown=10, est=10, status='NS', pbi=pbi)
        task2 = create_task(name='task2', desc='for testing..', burndown=20, est=20, status='NS', pbi=pbi)
        task3 = create_task(name='task3', desc='for testing...', burndown=30, est=30, status='NS', pbi=pbi)
        url = reverse('backtrack:new_task', args=(pbi.id,))
        response = self.client.get(url)
        # self.assertQuerysetEqual(response.context['pbi.task_set'], ['<Task: task1>', '<Task: task2>', '<Task: task3>'])
        self.assertContains(response, "task1")
        self.assertContains(response, "task2")
        self.assertContains(response, "task3")

    def delete_task(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        task = create_task(name='task', desc='for testing', burndown=10, est=10, status='NS', pbi=pbi)
        task.delete()
        url = reverse('backtrack:new_task', args=(pbi.id,))
        response = self.client.get(url)
        # self.assertQuerysetEqual(response.context['pbi.task_set'], [])
        self.assertContains(response, "No Tasks for PBI yet")

"""
class ModifyTaskViewTest(TestCase):
    def test_modify_task(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
        task = create_task(name='task', desc='for testing', burndown=10, est=10, status='NS', pbi=pbi)
        data = {
            'name':'new task',
            'desc':'new for testing',
            'burndown':20,
            'status':'IP'
        }
        url = reverse('backtrack:modify_task', args=(task.id,))
        response = self.client.post(url, data)
        # c.get('/customers/details/', {'name': 'fred', 'age': 7}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # response = self.client.post(url, data, content_type=’application/x-www-form-urlencoded’)
        self.assertEqual(response.status_code, 200)
        # self.assertQuerysetEqual(response.context['pbi.task_set'], ['<Task: new task>'])
        self.assertContains(response, "new task")


class modifyPBITest(testCase):
    def test_modify_pbi(self):
        project = create_project(name="Test project", desc="this is a project for testing")
        sprint = create_sprint(number=1, project=project)
        pbi = create_pbi(name='pbi', desc="pbi for testing", priority=1, storypoints=20, status='NS', project=project, sprint=sprint)
"""
