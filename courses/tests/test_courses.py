# -*- coding: utf-8 -*-
import datetime

from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError, ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)

class TestCourses(SavepointCase):

    def setUp(self):
        super(TestCourses, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(TestCourses, cls).setUpClass()
        Partner = cls.env['res.partner']
        Room = cls.env['lesson.room']
        Course = cls.env['course.course']
        Lesson = cls.env['course.lesson']

        instructor_group = cls.env.ref('courses.group_courses_instructor').id
        student_group = cls.env.ref('courses.group_courses_student').id
        cls.instructor1, cls.instructor2 = Partner.create([
            {
                'name': 'Instructor1',
                'instructor': True,
                'user_ids': [(0, 0, {
                    'name': 'Instructor1',
                    'login': 'instructor1@courses.com',
                    'groups_id': [(4, instructor_group)]
                })]
            },
            {
                'name': 'Instructor2',
                'instructor': True,
                'user_ids': [(0, 0, {
                    'name': 'Instructor2',
                    'login': 'instructor2@courses.com',
                    'groups_id': [(4, instructor_group)]
                })]
            }
        ])
        
        cls.room1, cls.room2, cls.room3 = Room.create([
            {
                'name': 'Room1',
                'capacity': 4
            },
            {
                'name': 'Room2',
                'capacity': 4
            },
            {
                'name': 'Room3',
                'capacity': 5
            }
        ])

        cls.student1, cls.student2, cls.student3, cls.student4, cls.student5, cls.student6 = Partner.create([
            {
                'name': 'Student1',
                'user_ids': [(0, 0, {
                    'name': 'Student1',
                    'login': 'student1@courses.com',
                    'groups_id': [(4, student_group)]
                })]
            },
            {
                'name': 'Student2',
                'user_ids': [(0, 0, {
                    'name': 'Student2',
                    'login': 'student2@courses.com',
                    'groups_id': [(4, student_group)]
                })]
            },
            {
                'name': 'Student3',
                'user_ids': [(0, 0, {
                    'name': 'Student3',
                    'login': 'student3@courses.com',
                    'groups_id': [(4, student_group)]
                })]
            },
            {
                'name': 'Student4',
                'user_ids': [(0, 0, {
                    'name': 'Student4',
                    'login': 'student4',
                    'groups_id': [(4, student_group)]
                })]
            },
            {
                'name': 'Student5',
                'user_ids': [(0, 0, {
                    'name': 'Student5',
                    'login': 'student5@courses.com',
                    'groups_id': [(4, student_group)]
                })]
            },
            {
                'name': 'Student6',
                'user_ids': [(0, 0, {
                    'name': 'Student6',
                    'login': 'student6@courses.com',
                    'groups_id': [(4, student_group)]
                })]
            }
        ])
        
        cls.course1, cls.course2 = Course.create([
            {
                'name': 'Course1',
                'instructor_id': cls.instructor1.id,
                'date_start': datetime.date(2021, 10, 19),
                'date_end': datetime.date(2021, 10, 25)
            },
            {
                'name': 'Course2',
                'instructor_id': cls.instructor2.id,
                'date_start': datetime.date(2021, 10, 18),
                'date_end': datetime.date(2021, 10, 24)
            }
        ])
        
        cls.lesson1, cls.lesson2, cls.lesson3, cls.lesson4, cls.lesson5, cls.lesson6, cls.lesson7 = Lesson.create([
            {
                'name': 'Lesson1',
                'course_id': cls.course1.id,
                'room_id': cls.room1.id,
                'date_scheduled': datetime.datetime(2021, 10, 19, 9)
            },
            {
                'name': 'Lesson2',
                'course_id': cls.course1.id,
                'room_id': cls.room1.id,
                'date_scheduled': datetime.datetime(2021, 10, 22, 9)
            },
            {
                'name': 'Lesson3',
                'course_id': cls.course1.id,
                'room_id': cls.room2.id,
                'date_scheduled': datetime.datetime(2021, 10, 24, 9)
            },
            {
                'name': 'Lesson4',
                'course_id': cls.course2.id,
                'room_id': cls.room3.id,
                'date_scheduled': datetime.datetime(2021, 10, 18, 9)
            },
            {
                'name': 'Lesson5',
                'course_id': cls.course2.id,
                'room_id': cls.room3.id,
                'date_scheduled': datetime.datetime(2021, 10, 20, 9)
            },
            {
                'name': 'Lesson6',
                'course_id': cls.course2.id,
                'room_id': cls.room3.id,
                'date_scheduled': datetime.datetime(2021, 10, 21, 9)
            },
            {
                'name': 'Lesson7',
                'course_id': cls.course2.id,
                'room_id': cls.room3.id,
                'date_scheduled': datetime.datetime(2021, 10, 23, 9)
            }
        ])

    def test_student_view_own_courses_lessons(self):
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id)]
        })
        with self.assertRaises(AccessError):
            self.course2.sudo(self.student1).read()
        with self.assertRaises(AccessError):
            self.lesson5.sudo(self.student1).read()

    def test_instructor_view_own_courses_lessons(self):
        with self.assertRaises(AccessError):
            self.course2.sudo(self.instructor1).read()
        with self.assertRaises(AccessError):
            self.lesson5.sudo(self.instructor1).read()

    # courses
    def test_courses_move_to_ready(self):
        with self.assertRaises(ValidationError):
            self.course1.button_ready()
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id), ]
        })
        self.course1.button_ready()
        self.assertEqual(self.course1.state, 'ready', f'Course1 {self.course1.state} is not ready.')
        
    def test_courses_move_to_start(self):
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id), ]
        })
        self.course1.button_ready()
        with self.assertRaises(UserError):
            self.course1.button_start()
        self.course1.write({
            'date_start': datetime.date.today(),
        })
        self.course1.button_start()
        self.assertEqual(self.course1.state, 'in_progress', f'Course1 {self.course1.state} is not in_progress.')

    def test_courses_move_to_done(self):
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id), ]
        })
        self.course1.button_ready()
        self.course1.write({
            'date_start': datetime.date.today(),
        })
        self.course1.button_start()
        self.course1.button_done()
        self.assertEqual(self.course1.state, 'done', f'Course1 {self.course1.state} is not done.')
        self.assertEqual(self.lesson1.state, 'cancelled', f'Lesson1 {self.lesson1.state} is not cancelled.')

    def test_courses_move_to_cancelled(self):
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id), ]
        })
        self.course1.button_ready()
        self.course1.write({
            'date_start': datetime.date.today(),
        })
        self.course1.button_start()
        self.course1.button_done()
        with self.assertRaises(UserError):
            self.course1.button_cancel()
        self.course2.button_cancel()
        self.assertEqual(self.course2.state, 'cancelled', f'Course1 {self.course2.state} is not cancelled.')
        self.assertEqual(self.lesson5.state, 'cancelled', f'Lesson1 {self.lesson5.state} is not cancelled.')
    
    def test_courses_move_to_planning(self):
        self.course1.write({
            'student_enrolled_ids': [(4, self.student1.id), ]
        })
        self.course1.button_ready()
        self.course1.write({
            'date_start': datetime.date.today(),
        })
        self.course1.button_start()
        self.course1.button_done()
        with self.assertRaises(UserError):
            self.course1.button_plan()
        self.course2.button_cancel()
        self.course2.button_plan()
        self.assertEqual(self.course2.state, 'in_planning', f'Course1 {self.course2.state} is not in_planning.')
        self.assertEqual(self.lesson5.state, 'planned', f'Lesson1 {self.lesson5.state} is not planned.')

    # # test course cannot have more students than room size
    def test_course_students_room_constraint(self):
        with self.assertRaises(ValidationError):
            self.course2.write({
            'student_enrolled_ids': [(4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student5.id), (4, self.student6.id)]
        })

    # # test cannot put instructor in students list 
    def test_instructor_enrolled_student_same_course_constraints(self):
        with self.assertRaises(ValidationError):
            self.course2.write({
            'student_enrolled_ids': [(4, self.instructor2.id)]
        })
    
    # # lessons
    def test_lesson_move_to_in_progress(self):
        with self.assertRaises(UserError):
            self.lesson5.button_start()
        self.course2.write({
            'student_enrolled_ids': [(5, 0), (4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student6.id)]
        })
        self.course2.button_start()
        self.lesson5.button_start()
        self.assertEqual(self.lesson5.state, 'in_progress', f'Lesson5 {self.lesson5.state} is not in_progress.')

    def test_lesson_move_to_done(self):
        self.course2.write({
            'student_enrolled_ids': [(5, 0), (4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student6.id)]
        })
        self.course2.button_start()
        self.lesson5.button_start()
        with self.assertRaises(UserError):
            self.lesson3.button_done()
        with self.assertRaises(UserError):
            self.lesson5.button_done()
        # test mark attendance
        mark_attendance = self.env['lesson.attendance'].with_context({'active_ids': [self.lesson5.id], 'active_model': 'course.lesson'}).create({})
        # assert lesson id is lesson5
        self.assertEqual(mark_attendance.lesson_id, self.lesson5, f'Mark Attendance lesson {mark_attendance.lesson_id} is not {self.lesson5}')
        self.assertEqual(mark_attendance.attendance_ids.ids.sort(), [self.student1.id, self.student2.id, self.student3.id, self.student4.id, self.student6.id].sort(), 
            f'Mark Attendance students {mark_attendance.attendance_ids.ids} is not {[self.student1.id, self.student2.id, self.student3.id, self.student4.id, self.student6.id]}')
        # assert student lin on mark attendance
        with self.assertRaises(UserError):
            mark_attendance.action_take_attendance()
        mark_attendance.attendance_ids.filtered(lambda a: a.student_id.id in [self.student1.id, self.student2.id]).write({'attended': True})
        self.assertEqual(mark_attendance.attendance_ids.filtered(lambda a: a.attended).ids.sort(), [self.student1.id, self.student2.id].sort(), 
            f'Mark Attendance attended {mark_attendance.attendance_ids.filtered(lambda a: a.attended).ids.sort()} is not {[self.student1.id, self.student2.id].sort()}')
        # make attendance true
        mark_attendance.action_take_attendance()
        self.lesson5.button_done()
        self.assertEqual(self.lesson5.state, 'done', f'Lesson5 state {self.lesson5.state} is not done')
        self.assertEqual(self.lesson5.student_attendee_ids.ids.sort(), [self.student1.id, self.student2.id].sort(),
            f'Lesson5 attendees {self.lesson5.student_attendee_ids.ids} are not {[self.student1.id, self.student2.id]}')
        self.assertEqual(self.student1.completed_lesson_ids.ids, [self.lesson5.id], f'Student1 completed lessons {self.student1.completed_lesson_ids.ids} are not {self.lesson5.id}')
        self.assertEqual(self.student1.lessons_attended_count, 1, f'Student1 completed lesson count {self.student1.lessons_attended_count} is not 1')

    def test_lesson_move_to_cancelled(self):
        self.course2.write({
            'student_enrolled_ids': [(5, 0), (4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student6.id)]
        })
        self.course2.button_start()
        self.lesson5.button_start()
        mark_attendance = self.env['lesson.attendance'].with_context({'active_ids': [self.lesson5.id], 'active_model': 'course.lesson'}).create({})
        mark_attendance.attendance_ids.filtered(lambda a: a.student_id.id in [self.student1.id, self.student2.id]).write({'attended': True})
        mark_attendance.action_take_attendance()
        self.lesson5.button_done()
        with self.assertRaises(UserError):
            self.lesson5.button_cancel()
        self.lesson3.button_cancel()
        self.assertEqual(self.lesson3.state, 'cancelled', f'Lesson3 state {self.lesson3.state} is not cancelled')

    def test_lesson_move_to_planning(self):
        self.course2.write({
            'student_enrolled_ids': [(5, 0), (4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student6.id)]
        })
        self.course2.button_start()
        self.lesson5.button_start()
        mark_attendance = self.env['lesson.attendance'].with_context({'active_ids': [self.lesson5.id], 'active_model': 'course.lesson'}).create({})
        mark_attendance.attendance_ids.filtered(lambda a: a.student_id.id in [self.student1.id, self.student2.id]).write({'attended': True})
        mark_attendance.action_take_attendance()
        self.lesson5.button_done()
        self.lesson3.button_cancel()
        with self.assertRaises(UserError):
            self.lesson5.button_plan()
        self.lesson3.button_plan()
        self.assertEqual(self.lesson3.state, 'planned', f'Lesson3 state {self.lesson3.state} is not planned')

    # # test lesson cannot have room less than students
    def test_lesson_student_room_constraint(self):
        self.course2.write({
            'student_enrolled_ids': [(5, 0), (4, self.student1.id), (4, self.student2.id), (4, self.student3.id), (4, self.student4.id), (4, self.student6.id)]
        })
        with self.assertRaises(ValidationError):
            self.lesson4.write({'room_id': self.room2.id})

    # # test room scheduling overlap
    def test_lesson_course_schedule_map(self):
        with self.assertRaises(ValidationError):
            self.lesson3.write({'date_scheduled': datetime.datetime(2021, 10, 26, 10)})

    def test_lesson_room_schedule_overlap(self):
        with self.assertRaises(ValidationError):
            self.lesson4.write({'date_scheduled': datetime.datetime(2021, 10, 21, 9)})