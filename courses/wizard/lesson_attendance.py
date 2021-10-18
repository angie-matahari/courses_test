# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class LessonAttendance(models.TransientModel):
    _name = 'lesson.attendance'
    _description = 'Lesson Attendance'

    lesson_id = fields.Many2one('course.lesson', string='Lesson', required=True)
    attendance_ids = fields.One2many('lesson.attendance.line', 'attendance_id', string='Attendances', required=True)

    @api.model
    def default_get(self, default_fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only take attendance for one lesson at a time."))
        res = super(LessonAttendance, self).default_get(default_fields)
        
        lesson = self.env['course.lesson'].browse(self.env.context.get('active_id'))
        attendance_lines = []
        if lesson:
            res.update({'lesson_id': lesson.id})

            for student in lesson.student_enrolled_ids:
                attendance_lines.append((0, 0, {
                    'student_id': student.id
                }))
            _logger.info(attendance_lines)
            res.update({
                'attendance_ids': attendance_lines
            })
        return res

    @api.multi
    def action_take_attendance(self):
        _logger.info(self.attendance_ids.mapped('student_id'))
        if not any(self.attendance_ids.mapped('attended')):
            raise UserError(_("No student has been marked present. If no student attended, please cancel the lesson."))
        attendance = [(4, attendance.student_id.id) for attendance in self.attendance_ids.filtered(lambda a: a.attended)]
        _logger.info(attendance)
        self.lesson_id.write({
            'student_attendee_ids': [(5, 0)] + attendance
        })


class LessonAttendanceLine(models.TransientModel):
    _name = 'lesson.attendance.line'
    _description = 'Lesson Attendance Lines'

    attendance_id = fields.Many2one('lesson.attendance', string='Lesson Attendance', required=True, readonly=True, ondelete="cascade")
    student_id = fields.Many2one('res.partner', string='Student', required=True, readonly=True)
    attended = fields.Boolean(string='Attended', default=False)