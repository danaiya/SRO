from typing import List
from models import Lesson

# Императивный подход (поиск занятий преподавателя через цикл)
def find_teacher_lessons_imperative(lessons: List[Lesson], teacher_name: str) -> List[Lesson]:
    result = []
    for lesson in lessons:
        if lesson.teacher == teacher_name:
            result.append(lesson)
    return result

# Функциональный подход (то же самое через фильтрацию и генератор/лямбду)
def find_teacher_lessons_functional(lessons: List[Lesson], teacher_name: str) -> List[Lesson]:
    return list(filter(lambda l: l.teacher == teacher_name, lessons))

def compare_paradigms_demo(lessons: List[Lesson]):
    print("--- Сравнение парадигм ---")
    t_name = "Иванов И.И."
    imp_res = find_teacher_lessons_imperative(lessons, t_name)
    func_res = find_teacher_lessons_functional(lessons, t_name)
    print(f"Императивный результат (шт): {len(imp_res)}")
    print(f"Функциональный результат (шт): {len(func_res)}")
    print("Вывод: Функциональный стиль лаконичнее и проще читается при выборках, в то время как императивный подход наглядно описывает пошаговый алгоритм.")