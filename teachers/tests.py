from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from students.models import Assignment, Submission, Student
from teachers.models import Teacher
from classes.models import SchoolClass, Subject


User = get_user_model()


class TeacherAssignmentTests(TestCase):
    def setUp(self):
        # create a user and teacher profile
        self.user = User.objects.create_user(username='tuser', password='pass')
        self.teacher = Teacher.objects.create(user=self.user, full_name='Test Teacher', staff_id='T001')

        # create a class and subject
        self.school_class = SchoolClass.objects.create(name='Form 1')
        self.subject = Subject.objects.create(name='Mathematics')
        self.teacher.classes.add(self.school_class)
        self.teacher.subjects.add(self.subject)

        # create student and profile
        self.su = User.objects.create_user(username='suser', password='pass')
        self.student = Student.objects.create(user=self.su, school_class=self.school_class)

        self.client = Client()

    def test_teacher_can_create_assignment(self):
        self.client.login(username='tuser', password='pass')
        url = reverse('teachers:create_assignment')
        resp = self.client.post(url, {
            'title': 'Test Assignment',
            'description': 'Do problems',
            'school_class': self.school_class.id,
            'subject': self.subject.id,
            'total_marks': 50,
        })
        # expect redirect to assignments list
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Assignment.objects.filter(title='Test Assignment').exists())

    def test_teacher_can_grade_submission(self):
        # create assignment and submission
        assignment = Assignment.objects.create(title='A', school_class=self.school_class, teacher=self.teacher)
        submission = Submission.objects.create(assignment=assignment, student=self.student)

        self.client.login(username='tuser', password='pass')
        url = reverse('teachers:grade_submission', args=[assignment.id, submission.id])
        resp = self.client.post(url, {'marks_obtained': 45, 'feedback': 'Good work'})
        self.assertEqual(resp.status_code, 302)
        submission.refresh_from_db()
        self.assertEqual(submission.marks_obtained, 45)

    def test_student_cannot_access_create_assignment(self):
        self.client.login(username='suser', password='pass')
        url = reverse('teachers:create_assignment')
        resp = self.client.get(url)
        # student should be redirected (not permitted)
        self.assertNotEqual(resp.status_code, 200)
