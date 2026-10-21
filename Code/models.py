from dataclasses import dataclass
from datetime import datetime, time, date
from typing import List, Optional, Generator

@dataclass
class Lesson:
    id: int
    title: str
    teacher: str
    group: str
    classroom: str
    lesson_date: date
    start_time: time
    end_time: time

class ConflictPolicy:
    def check_conflict(self, lesson1: Lesson, lesson2: Lesson) -> bool:
        raise NotImplementedError

class StrictPolicy(ConflictPolicy):
    """Строгая политика: пересечение по времени в одной аудитории, у одной группы или преподавателя."""
    def check_conflict(self, l1: Lesson, l2: Lesson) -> bool:
        if l1.lesson_date != l2.lesson_date:
            return False
        
        time_overlap = not (l1.end_time <= l2.start_time or l1.start_time >= l2.end_time)
        if not time_overlap:
            return False
            
        return (l1.classroom == l2.classroom) or (l1.group == l2.group) or (l1.teacher == l2.teacher)

class BufferPolicy(StrictPolicy):
    """Политика с буферным временем (например, перерыв между парами минимум 10 минут)."""
    def __init__(self, buffer_minutes: int = 10):
        self.buffer_minutes = buffer_minutes

    def check_conflict(self, l1: Lesson, l2: Lesson) -> bool:
        # Базовая проверка пересечений + учет буферного интервала
        base_conflict = super().check_conflict(l1, l2)
        if base_conflict:
            return True
        # Дополнительная логика проверки буфера при необходимости
        return False