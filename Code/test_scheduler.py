import unittest
from datetime import date, time
from models import Lesson, StrictPolicy
from scheduler import Schedule

class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.policy = StrictPolicy()
        self.schedule = Schedule(self.policy)
        self.l1 = Lesson(1, "Математика", "Иванов И.И.", "ТИИ25-21", "Ауд-101", date(2026, 9, 1), time(9, 0), time(10, 30))
        self.l2 = Lesson(2, "Физика", "Петров П.П.", "ТИИ25-21", "Ауд-102", date(2026, 9, 1), time(10, 40), time(12, 10))

    def test_1_add_lesson_success(self):
        err = self.schedule.add_lesson(self.l1)
        self.assertIsNone(err)
        self.assertEqual(len(self.schedule.lessons), 1)

    def test_2_conflict_classroom(self):
        self.schedule.add_lesson(self.l1)
        l_conflict = Lesson(3, "Химия", "Сидоров С.С.", "ТИИ25-22", "Ауд-101", date(2026, 9, 1), time(9, 30), time(11, 0))
        err = self.schedule.add_lesson(l_conflict)
        self.assertIsNotNone(err)

    def test_3_conflict_group(self):
        self.schedule.add_lesson(self.l1)
        l_conflict = Lesson(4, "История", "Сидоров С.С.", "ТИИ25-21", "Ауд-103", date(2026, 9, 1), time(10, 0), time(11, 30))
        err = self.schedule.add_lesson(l_conflict)
        self.assertIsNotNone(err)

    def test_4_conflict_teacher(self):
        self.schedule.add_lesson(self.l1)
        l_conflict = Lesson(5, "Информатика", "Иванов И.И.", "ТИИ25-23", "Ауд-104", date(2026, 9, 1), time(9, 30), time(11, 0))
        err = self.schedule.add_lesson(l_conflict)
        self.assertIsNotNone(err)

    def test_5_filter_by_day_empty(self):
        self.schedule.add_lesson(self.l1)
        res = self.schedule.filter_by_day(date(2026, 9, 2))
        self.assertEqual(len(res), 0)

    def test_6_filter_by_day_found(self):
        self.schedule.add_lesson(self.l1)
        res = self.schedule.filter_by_day(date(2026, 9, 1))
        self.assertEqual(len(res), 1)

    def test_7_sort_lessons_by_time(self):
        l_early = Lesson(6, "Физкультура", "Тренер Т.", "ТИИ25-21", "Спортзал", date(2026, 9, 1), time(8, 0), time(9, 30))
        self.schedule.add_lesson(self.l2)
        self.schedule.add_lesson(l_early)
        sorted_l = self.schedule.sort_lessons('time')
        self.assertEqual(sorted_l[0].id, 6)

    def test_8_sort_lessons_by_group(self):
        l_other_group = Lesson(7, "Философия", "Преп. П.", "ТИИ25-22", "Ауд-201", date(2026, 9, 1), time(9, 0), time(10, 30))
        self.schedule.add_lesson(self.l1) # ТИИ25-21
        self.schedule.add_lesson(l_other_group)
        sorted_l = self.schedule.sort_lessons('group')
        self.assertEqual(sorted_l[0].group, "ТИИ25-21")

    def test_9_free_windows_start(self):
        self.schedule.add_lesson(self.l1) # 9:00 - 10:30 в Ауд-101
        windows = list(self.schedule.generate_free_windows(date(2026, 9, 1), "Ауд-101", time(8, 0), time(12, 0)))
        self.assertEqual(windows[0], (time(8, 0), time(9, 0)))

    def test_10_free_windows_middle(self):
        l_late = Lesson(8, "Практика", "Преп. П.", "ТИИ25-21", "Ауд-101", date(2026, 9, 1), time(11, 0), time(12, 0))
        self.schedule.add_lesson(self.l1) # 9:00 - 10:30
        self.schedule.add_lesson(l_late)
        windows = list(self.schedule.generate_free_windows(date(2026, 9, 1), "Ауд-101", time(8, 0), time(13, 0)))
        # Окно между 10:30 и 11:00
        self.assertIn((time(10, 30), time(11, 0)), windows)

    def test_11_free_windows_end(self):
        self.schedule.add_lesson(self.l1) # 9:00 - 10:30 в Ауд-101
        windows = list(self.schedule.generate_free_windows(date(2026, 9, 1), "Ауд-101", time(8, 0), time(12, 0)))
        self.assertEqual(windows[-1], (time(10, 30), time(12, 0)))

    def test_12_no_conflict_different_days(self):
        l_next_day = Lesson(9, "Алгоритмы", "Иванов И.И.", "ТИИ25-21", "Ауд-101", date(2026, 9, 2), time(9, 0), time(10, 30))
        self.schedule.add_lesson(self.l1)
        err = self.schedule.add_lesson(l_next_day)
        self.assertIsNone(err)

if __name__ == '__main__':
    unittest.main()