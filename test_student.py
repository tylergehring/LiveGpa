import unittest
from unittest.mock import patch, Mock
import student
import datetime

MOCK_PROFILE = {
    'first_name': 'Alice',
    'last_name': 'Smith',
    'id': 123,
    'email': 'alice@example.com',
    'avatar_url': 'http://avatar.url',
    'bio': 'Student bio',
    'pronouns': 'she/her',
    'locale': 'en',
}
MOCK_PAGE_VIEWS = [
    {'created_at': '2025-07-01T12:00:00Z'}
]
MOCK_COURSES = [
    {
        'id': 1,
        'name': 'Math 101',
        'course_code': 'MATH101',
        'term': {'name': 'Spring 2025'},
        'start_at': '2025-01-10T00:00:00Z',
        'end_at': '2025-08-01T00:00:00Z',
        'weighted_total': True
    },
    {
        'id': 2,
        'name': 'History 201',
        'course_code': 'HIST201',
        'term': {'name': 'Spring 2025'},
        'start_at': '2025-01-10T00:00:00Z',
        'end_at': '2025-08-01T00:00:00Z',
        'weighted_total': False
    }
]
MOCK_ENROLLMENTS = [
    [{
        'grades': {
            'current_score': 95,
            'current_grade': 'A',
            'final_score': 94,
            'final_grade': 'A',
            'unposted_current_score': None,
            'unposted_final_score': None
        }
    }],
    [{
        'grades': {
            'current_score': 85,
            'current_grade': 'B',
            'final_score': 84,
            'final_grade': 'B',
            'unposted_current_score': None,
            'unposted_final_score': None
        }
    }]
]
MOCK_COURSE_DETAILS = [
    {'course_credit_hours': 4},
    {'course_credit_hours': 3}
]
MOCK_ASSIGNMENTS = [
    [
        {
            'id': 101,
            'name': 'Homework 1',
            'due_at': '2025-02-01T00:00:00Z',
            'points_possible': 100,
            'omit_from_final_grade': False,
            'score_statistics': {'mean': 90},
            'submission': {
                'score': 100,
                'grade': 'A',
                'submitted_at': '2025-01-31T00:00:00Z',
                'late': False,
                'missing': False
            }
        }
    ],
    [
        {
            'id': 201,
            'name': 'Essay 1',
            'due_at': '2025-03-01T00:00:00Z',
            'points_possible': 100,
            'omit_from_final_grade': False,
            'score_statistics': {'mean': 80},
            'submission': {
                'score': 80,
                'grade': 'B-',
                'submitted_at': '2025-03-01T00:00:00Z',
                'late': False,
                'missing': False
            }
        }
    ]
]

def mock_requests_get(url, headers=None, params=None):
    if url.endswith('/users/self/profile'):
        return Mock(ok=True, json=lambda: MOCK_PROFILE)
    if url.endswith('/users/self/page_views?per_page=1'):
        return Mock(ok=True, json=lambda: MOCK_PAGE_VIEWS)
    if '/courses/?' in url:
        return Mock(ok=True, json=lambda: MOCK_COURSES)
    if '/enrollments' in url:
        # params['user_id'] will distinguish course
        if '1' in url:
            return Mock(ok=True, json=lambda: MOCK_ENROLLMENTS[0])
        else:
            return Mock(ok=True, json=lambda: MOCK_ENROLLMENTS[1])
    if url.endswith('/courses/1'):
        return Mock(ok=True, json=lambda: MOCK_COURSE_DETAILS[0])
    if url.endswith('/courses/2'):
        return Mock(ok=True, json=lambda: MOCK_COURSE_DETAILS[1])
    if '/assignments' in url:
        if '/1/' in url:
            return Mock(ok=True, json=lambda: MOCK_ASSIGNMENTS[0])
        else:
            return Mock(ok=True, json=lambda: MOCK_ASSIGNMENTS[1])
    return Mock(ok=False, text='Not Found')

class TestStudent(unittest.TestCase):
    @patch('requests.get', side_effect=mock_requests_get)
    def test_full_student_lifecycle(self, mock_get):
        s = student.Student('fake_api_key')
        # Profile
        self.assertEqual(s.data.first_name, 'Alice')
        self.assertEqual(s.data.last_name, 'Smith')
        self.assertEqual(s.data.email, 'alice@example.com')
        self.assertEqual(s.data.last_login, '2025-07-01T12:00:00Z')
        # Courses
        self.assertEqual(len(s.data.courses), 2)
        self.assertEqual(s.data.courses[0]['name'], 'Math 101')
        self.assertEqual(s.data.courses[1]['name'], 'History 201')
        # Enrollments/Grades
        self.assertEqual(s.data.courses[0]['grade']['current_score'], 95)
        self.assertEqual(s.data.courses[1]['grade']['current_score'], 85)
        self.assertEqual(s.data.courses[0]['credits'], 4)
        self.assertEqual(s.data.courses[1]['credits'], 3)
        # GPA calculation
        self.assertAlmostEqual(s.data.gpa, (4*4.0 + 3*3.0)/7, places=3)
        self.assertEqual(s.data.total_credits, 7)
        # Term data
        self.assertIn('Spring 2025', s.data.term_data)
        self.assertGreater(s.data.term_data['Spring 2025']['term_gpa'], 0)
        # Assignments
        s.get_assignments()
        self.assertEqual(len(s.data.courses[0]['assignments']), 1)
        self.assertEqual(s.data.courses[0]['assignments'][0]['name'], 'Homework 1')
        self.assertEqual(s.data.courses[1]['assignments'][0]['name'], 'Essay 1')
        self.assertEqual(s.data.courses[0]['assignments'][0]['submission']['score'], 100)
        self.assertEqual(s.data.courses[1]['assignments'][0]['submission']['score'], 80)

    @patch('requests.get', side_effect=mock_requests_get)
    def test_partial_student(self, mock_get):
        s = student.Student('fake_api_key', grab_all=False)
        # Should not fetch anything until methods are called
        self.assertEqual(s.data.first_name, 'None')
        s.get_user_profile()
        self.assertEqual(s.data.first_name, 'Alice')
        s.get_courses()
        self.assertEqual(len(s.data.courses), 2)
        s.get_detailed_enrollments()
        self.assertEqual(s.data.courses[0]['grade']['current_score'], 95)
        s.calc_gpa()
        self.assertAlmostEqual(s.data.gpa, (4*4.0 + 3*3.0)/7, places=3)

if __name__ == '__main__':
    unittest.main()
