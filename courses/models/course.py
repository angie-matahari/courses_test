# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import datetime

import logging
_logger = logging.getLogger(__name__)

class Course(models.Model):
    _name = 'course.course'
    _description = 'Course'
    _order = 'date_start desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {'cancelled': [('readonly', True)], 'done': [('readonly', True)], 'in_progress': [('readonly', True)]}

    name = fields.Char(required=True, track_visibility='always')
    description = fields.Text(string='Course Description')
    instructor_id = fields.Many2one('res.partner', string='Instructor', domain=[('instructor', '=', True),('is_company', '=', False)], required=True, track_visibility='onchange')
    lesson_ids = fields.One2many('course.lesson', 'course_id', string='Lessons', track_visibility='onchange')
    student_enrolled_ids = fields.Many2many('res.partner', 'res_partner_enrolled_course_rel', 'course_ids', 'partner_ids',
        string='Enrolled Students', domain="[('id', '!=', instructor_id),('is_company', '=', False)]", track_visibility='onchange')
    state = fields.Selection([
        ('in_planning', 'In-Planning'),
        ('ready', 'Ready'),
        ('in_progress', 'In-Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='in_planning', required=True, track_visibility='always')
    date_start = fields.Date(string='Start Date', track_visibility='onchange')
    date_end = fields.Date(string='End Date', track_visibility='onchange')
    lesson_count = fields.Integer(compute='_compute_lesson_count', string='# of Lessons', store=True, default=0)
    student_count = fields.Integer(compute='_compute_student_count', string='# of Students', store=True, default=0)

    @api.multi
    def unlink(self):
        for record in self:
            if not record.state == 'cancelled':
                raise UserError(_('In order to delete a course, you must cancel it first.'))
        return super(Course, self).unlink()

    @api.depends('student_enrolled_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_enrolled_ids)
    
    @api.depends('lesson_ids')
    def _compute_lesson_count(self):
        for record in self:
            record.lesson_count = len(record.lesson_ids)

    @api.multi
    def button_ready(self):
        if not self.lesson_ids or not self.student_enrolled_ids or not self.date_end or not self.date_start:
            raise ValidationError("Cannot move state to ready if the course does not have lessons, enrolled students or scheduled dates.")
        self.write({'state': 'ready'})
        return {}

    @api.multi
    def button_start(self):
        if self.date_start != fields.Date.today():
            raise UserError("Please adjust start and end dates.")
        self.write({'state': 'in_progress'})
        return {}

    @api.multi
    def button_done(self):
        if self.state != 'in_progress':
            raise UserError(_("Course must be in progress to complete it."))
        self.write({'state': 'done'})
        self.lesson_ids.filtered(lambda l: l.state not in ['done', 'cancelled']).write({'state': 'cancelled'})
        return {}

    @api.multi
    def button_cancel(self):
        if self.state == 'done':
            raise UserError(_("Done course cannot be cancelled."))
        self.write({'state': 'cancelled'})
        self.lesson_ids.filtered(lambda l: l.state not in ['done', 'cancelled']).write({'state': 'cancelled'})
        return {}

    @api.multi
    def button_plan(self):
        if self.state != 'cancelled':
            raise UserError(_("The course must be cancelled to start planning."))
        self.write({'state': 'in_planning'})
        self.lesson_ids.write({'state': 'planned'})
        return {}

    @api.constrains('student_count')
    def _constrains_student_count(self):
        largest_room_capacity = max(self.env['lesson.room'].search([]).mapped('capacity'), default=0)
        for record in self:
            if record.student_count > largest_room_capacity:
                raise ValidationError("You cannot enroll more students than the maximum capacity of the available lesson rooms.")

    @api.constrains('instructor_id', 'student_enrolled_ids')
    def _constrains_instructor_id(self):
        for record in self:
            if record.instructor_id.id in record.student_enrolled_ids.ids:
                raise ValidationError("Instructor is also a student. Please pick another instructor or delete the instructor from the list of students.")


class CourseLesson(models.Model):
    _name = 'course.lesson'
    _description = 'Lesson'
    _order = 'date_scheduled desc, course_id, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    LESSON_READONLY_STATES = {'cancelled': [('readonly', True)], 'done': [('readonly', True)], 'in_progress': [('readonly', True)]}

    name = fields.Char(required=True, track_visibility='always')
    lesson_details = fields.Text(string='Lesson Details')
    course_id = fields.Many2one('course.course', string='Course', required=True, ondelete='cascade', track_visibility='always')
    instructor_id = fields.Many2one('res.partner', string='Instructor', related='course_id.instructor_id', readonly=True, track_visibility='always')
    course_details = fields.Text(string='Course Details', related='course_id.description', readonly=True)
    course_state = fields.Selection(string='Course State', related='course_id.state')
    room_id = fields.Many2one('lesson.room', string='Room', required=True, track_visibility='always')
    room_capacity = fields.Integer(string='Room Capacity', related='room_id.capacity', readonly=True, track_visibility='always')
    student_enrolled_ids = fields.Many2many('res.partner', 'res_partner_enrolled_lesson_rel', 'lesson_ids', 'partner_ids', related='course_id.student_enrolled_ids', string='Enrolled Students', readonly=True, track_visibility='always')
    student_attendee_ids = fields.Many2many('res.partner', 'res_partner_completed_lesson_rel', 'lesson_ids', 'partner_ids', string='Lesson Attendees', readonly=True, track_visibility='onchange')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In-Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='planned', required=True, track_visibility='always')
    date_scheduled = fields.Datetime(string='Scheduled Date/Time', required=True, track_visibility='always')
    duration = fields.Integer(string='Duration(Min)', default=60, track_visibility='onchange')
    students_enrolled_count = fields.Integer(compute='_compute_students_enrolled_count', string='# of Enrolled Students', store=True, default=0)
    students_attended_count = fields.Integer(compute='_compute_students_attended_count', string='# of Attended Students', store=True, default=0)
    
    @api.depends('student_attendee_ids')
    def _compute_students_attended_count(self):
        for record in self:
            record.students_attended_count = len(record.student_attendee_ids)
    
    @api.depends('student_enrolled_ids')
    def _compute_students_enrolled_count(self):
        for record in self:
            record.students_enrolled_count = len(record.student_enrolled_ids)

    @api.multi
    def button_start(self):
        if not (self.course_id.state == 'in_progress' and self.state == 'planned'):
            raise UserError(_("The course must be in progress to start a lesson."))
        self.write({'state': 'in_progress'})
        return {}

    @api.multi
    def button_done(self):
        if self.state != 'in_progress':
            raise UserError(_("The lesson must be in progress to move it to complete."))
        if not self.student_attendee_ids:
            raise UserError(_("Please mark attendance before completing the lesson."))
        self.write({'state': 'done'})
        return {}

    @api.multi
    def button_cancel(self):
        if self.state not in ['planned', 'in_progress']:
            raise UserError(_("The lesson must be in planning or in progress to cancel."))
        self.write({'state': 'cancelled'})
        return {}

    @api.multi
    def button_plan(self):
        if not (self.course_state in ['ready', 'in_planning', 'in_progress'] and self.state == 'cancelled'):
            raise UserError(_("The course must be in progress, in planning or ready to roll out to plan a lesson."))
        self.write({'state': 'planned'})
        return {}

    @api.constrains('date_scheduled', 'course_id')
    def _constrains_date_scheduled(self):
        for record in self:
            if not bool(record.course_id.date_start) or not bool(record.course_id.date_end):
                continue
            duration = record.duration or 60
            stop_time = record.date_scheduled + relativedelta(minutes=duration)
            course_date_start = datetime.datetime.combine(record.course_id.date_start, datetime.datetime.min.time())
            course_date_stop = datetime.datetime.combine(record.course_id.date_end, datetime.datetime.max.time())
            if not (course_date_start <= record.date_scheduled <= course_date_stop and course_date_start <= stop_time <= course_date_stop):
                raise ValidationError(_("The date scheduled for the lesson is outside the bounds of the course schedule."))

    @api.constrains('students_enrolled_count', 'room_id')
    def _constrains_students_enrolled_count(self):
        for record in self:
            if record.students_enrolled_count > record.room_capacity:
                raise ValidationError("You cannot assign a room with a smaller capacity than necessary.")

    @api.constrains('room_id', 'date_scheduled', 'duration')
    def _constrains_room_id(self):
        for record in self:
            duration = record.duration or 60
            stop_time = record.date_scheduled + relativedelta(minutes=duration)
            lessons_with_same_room = self.search([('room_id', '=', record.room_id.id),('id', '!=', record.id),('state', 'in', ['planned', 'in_progress']),('date_scheduled', '=', record.date_scheduled)])
            if bool(lessons_with_same_room):
                raise ValidationError("There are other lessons scheduled in the same room at this lesson's scheduled time. Please choose another room or time.")
