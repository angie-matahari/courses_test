# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LessonRoom(models.Model):
    _name = 'lesson.room'
    _description = 'Lesson Room'

    name = fields.Char(required=True)
    room_details = fields.Text(string='Room Details')
    capacity = fields.Integer(string='Capacity', default=1, required=True)