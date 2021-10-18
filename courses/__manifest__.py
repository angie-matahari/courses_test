# -*- coding: utf-8 -*-
{
    'name': "Courses",

    'summary': """
        Create and Schedule your courses and lessons for instructors and students""",

    'description': """
        Create courses with related lessons. 
        Schedule course and lessons and view them on a calendar.
        Create lesson rooms and assign them to individual lessons based on room capacity
        and enrolled students.
        View lessons and courses attached to instructors and students.
        
        Avails three user groups; students, instructor and admin
    """,

    'author': "Angela Mathare <angie.mathare@gmail.com>",

    'category': 'Specific Industry Applications',
    'version': '0.1',

    'depends': ['base', 'contacts', 'mail'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/lesson_attendance_views.xml',
        'views/course_views.xml',
        'views/lesson_room_views.xml',
        'views/instructor_views.xml',
        'views/student_views.xml',
        'views/res_partner_views.xml',
    ],

    'installable': True,
    'application': True
}
