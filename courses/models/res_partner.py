# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    instructor = fields.Boolean(string='Is Instructor', default=False, track_visibility='always')
    teaching_course_ids = fields.One2many('course.course', 'instructor_id', string='Teaching Courses', readonly=True, groups='courses.group_courses_instructor,courses.group_courses_admin', track_visibility='onchange')
    teaching_lesson_ids = fields.One2many('course.lesson', 'instructor_id', string='Teaching Lessons', readonly=True, groups='courses.group_courses_instructor,courses.group_courses_admin', track_visibility='onchange')
    enrolled_course_ids = fields.Many2many('course.course', 'res_partner_enrolled_course_rel', 'partner_ids', 'course_ids', string='Enrolled Courses', readonly=True, track_visibility='onchange')
    enrolled_lesson_ids = fields.Many2many('course.lesson', 'res_partner_enrolled_lesson_rel', 'partner_ids', 'lesson_ids', string='Enrolled Lessons', readonly=True, track_visibility='onchange')
    completed_lesson_ids = fields.Many2many('course.lesson', 'res_partner_completed_lesson_rel', 'partner_ids', 'lesson_ids', string='Completed Lessons', readonly=True, track_visibility='onchange')
    courses_instructor_count = fields.Integer(compute='_compute_courses_instructor_count', string='# of Instructor Courses', store=True, default=0)
    courses_enrolled_count = fields.Integer(compute='_compute_courses_enrolled_count', string='# of Enrolled Courses', store=True, default=0)
    lessons_enrolled_count = fields.Integer(compute='_compute_lessons_enrolled_count', string='# of Enrolled Lessons', store=True, default=0)
    lessons_teaching_count = fields.Integer(compute='_compute_lessons_teaching_count', string='# of Instructor Courses', store=True, default=0)
    lessons_attended_count = fields.Integer(compute='_compute_lessons_attended_count', string='# of Attended Lessons', store=True, default=0)
    
    @api.depends('completed_lesson_ids')
    def _compute_lessons_attended_count(self):
        for record in self:
            record.lessons_attended_count = len(record.completed_lesson_ids)
    
    @api.depends('teaching_lesson_ids')
    def _compute_lessons_teaching_count(self):
        for record in self:
            record.lessons_teaching_count = len(record.teaching_lesson_ids)
    
    @api.depends('enrolled_lesson_ids')
    def _compute_lessons_enrolled_count(self):
        for record in self:
            record.lessons_enrolled_count = len(record.enrolled_lesson_ids)
    
    @api.depends('enrolled_course_ids')
    def _compute_courses_enrolled_count(self):
        for record in self:
            record.courses_instructor_count = len(record.enrolled_course_ids)
    
    @api.depends('teaching_course_ids')
    def _compute_courses_instructor_count(self):
        for record in self:
            record.courses_instructor_count = len(record.teaching_course_ids)

    @api.multi
    def action_open_student_lessons(self):
        return {
            'name': _('Student Lessons'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'course.lesson',
            'target': 'new',
            'domain': [('id', 'in', self.enrolled_lesson_ids.ids)],
        }

    @api.multi
    def action_open_instructor_lessons(self):
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'course.lesson',
            'target': 'new',
            'domain': [('instructor_id', '=', self.id)],
        }