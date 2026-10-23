from abc import ABC, abstractmethod


class Lesson:

  def __init__(
      self,
      title: str,
      teacher: str,
      group: str,
      room: str,
      day: str,
      start_time: str,
      end_time: str,
  ):
    self.title = title
    self.teacher = teacher
    self.group = group
    self.room = room
    self.day = day
    self.start_time = start_time  # формат "HH:MM"
    self.end_time = end_time  # формат "HH:MM"

  @property
  def start_minutes(self) -> int:
    h, m = map(int, self.start_time.split(":"))
    return h * 60 + m

  @property
  def end_minutes(self) -> int:
    h, m = map(int, self.end_time.split(":"))
    return h * 60 + m


class ConflictPolicy(ABC):

  @abstractmethod
  def check_conflict(self, lesson1: Lesson, lesson2: Lesson) -> bool:
    """Возвращает True, если между занятиями есть конфликт."""
    pass


class StrictPolicy(ConflictPolicy):

  def check_conflict(self, lesson1: Lesson, lesson2: Lesson) -> bool:
    if lesson1.day.lower() != lesson2.day.lower():
      return False

    shared_resource = (
        lesson1.room == lesson2.room
        or lesson1.group == lesson2.group
        or lesson1.teacher == lesson2.teacher
    )
    if not shared_resource:
      return False

    latest_start = max(lesson1.start_minutes, lesson2.start_minutes)
    earliest_end = min(lesson1.end_minutes, lesson2.end_minutes)

    return latest_start < earliest_end


class BufferPolicy(ConflictPolicy):

  def __init__(self, buffer_minutes: int = 10):
    self.buffer_minutes = buffer_minutes

  def check_conflict(self, lesson1: Lesson, lesson2: Lesson) -> bool:
    if lesson1.day.lower() != lesson2.day.lower():
      return False

    shared_resource = (
        lesson1.room == lesson2.room
        or lesson1.group == lesson2.group
        or lesson1.teacher == lesson2.teacher
    )
    if not shared_resource:
      return False

    if lesson1.start_minutes <= lesson2.start_minutes:
      l1, l2 = lesson1, lesson2
    else:
      l1, l2 = lesson2, lesson1

    return (l1.end_minutes + self.buffer_minutes) > l2.start_minutes


class Schedule:

  def __init__(self, policy: ConflictPolicy):
    self.lessons = []
    self.policy = policy

  def add_lesson(self, lesson: Lesson):
    self.lessons.append(lesson)

  def filter_by_day(self, day: str) -> list:
    return [l for l in self.lessons if l.day.lower() == day.lower()]

  def sort_lessons(self):
    days_order = {
        "понедельник": 1,
        "вторник": 2,
        "среда": 3,
        "четверг": 4,
        "пятница": 5,
        "суббота": 6,
        "воскресенье": 7,
    }
    self.lessons.sort(
        key=lambda l: (
            days_order.get(l.day.lower(), 8),
            l.start_minutes,
        )
    )

  def find_conflicts(self) -> list:
    conflicts = []
    n = len(self.lessons)
    for i in range(n):
      for j in range(i + 1, n):
        if self.policy.check_conflict(self.lessons[i], self.lessons[j]):
          conflicts.append((self.lessons[i], self.lessons[j]))
    return conflicts

  def generate_free_intervals(
      self,
      day: str,
      resource_type: str,
      resource_name: str,
      day_start: str = "08:00",
      day_end: str = "18:00",
  ):
    """Ленивый генератор свободных интервалов времени для ресурса (группа/преподаватель/аудитория)."""
    day_lessons = [
        l
        for l in self.lessons
        if l.day.lower() == day.lower()
        and (
            (resource_type == "group" and l.group == resource_name)
            or (resource_type == "teacher" and l.teacher == resource_name)
            or (resource_type == "room" and l.room == resource_name)
        )
    ]
    day_lessons.sort(key=lambda l: l.start_minutes)

    def parse_time(t_str):
      h, m = map(int, t_str.split(":"))
      return h * 60 + m

    def format_time(minutes):
      return f"{minutes // 60:02d}:{minutes % 60:02d}"

    current_time = parse_time(day_start)
    end_limit = parse_time(day_end)

    for lesson in day_lessons:
      if lesson.start_minutes > current_time:
        yield (format_time(current_time), format_time(lesson.start_minutes))
      if lesson.end_minutes > current_time:
        current_time = lesson.end_minutes

    if current_time < end_limit:
      yield (format_time(current_time), format_time(end_limit))

  def get_rescheduling_recommendations(self) -> list:
    conflicts = self.find_conflicts()
    recommendations = []
    for l1, l2 in conflicts:
      recommendations.append(
          f"Конфликт между занятием '{l1.title}' (Группа: {l1.group},"
          f" Преподаватель: {l1.teacher}, Ауд: {l1.room}) и '{l2.title}'"
          f" (Группа: {l2.group}, Преподаватель: {l2.teacher}, Ауд: {l2.room})"
          f" в день '{l1.day}'. Рекомендация: перенесите одно из занятий на"
          " другое время или свободное окно."
      )
    return recommendations


def main():
  policy = StrictPolicy()
  schedule = Schedule(policy)

  # Добавление занятий (включая намеренные конфликты)
  schedule.add_lesson(
      Lesson(
          "Математика",
          "Иванов И.И.",
          "ИП-101",
          "Ауд. 101",
          "Понедельник",
          "09:00",
          "10:30",
      )
  )
  schedule.add_lesson(
      Lesson(
          "Физика",
          "Петров П.П.",
          "ИП-101",
          "Ауд. 102",
          "Понедельник",
          "10:40",
          "12:10",
      )
  )
  schedule.add_lesson(
      Lesson(
          "Информатика",
          "Иванов И.И.",
          "ИП-102",
          "Ауд. 103",
          "Понедельник",
          "10:00",
          "11:30",
      )
  )
  schedule.add_lesson(
      Lesson(
          "Химия",
          "Сидоров С.С.",
          "ИП-103",
          "Ауд. 101",
          "Понедельник",
          "09:30",
          "11:00",
      )
  )

  print("=== 1. РАСПИСАНИЕ (До сортировки) ===")
  for l in schedule.lessons:
    print(
        f"{l.day}: {l.start_time}-{l.end_time} | {l.title} | Преп: {l.teacher} |"
        f" Группа: {l.group} | {l.room}"
    )

  schedule.sort_lessons()
  print("\n=== 2. РАСПИСАНИЕ (После сортировки) ===")
  for l in schedule.lessons:
    print(
        f"{l.day}: {l.start_time}-{l.end_time} | {l.title} | Преп: {l.teacher} |"
        f" Группа: {l.group} | {l.room}"
    )

  print("\n=== 3. ФИЛЬТРАЦИЯ ПО ДНЮ (Понедельник) ===")
  monday_lessons = schedule.filter_by_day("Понедельник")
  for l in monday_lessons:
    print(f"{l.start_time} - {l.end_time}: {l.title} ({l.group})")

  print("\n=== 4. ПЕРЕЧЕНЬ КОНФЛИКТОВ ===")
  conflicts = schedule.find_conflicts()
  if conflicts:
    print(f"Всего найдено конфликтов: {len(conflicts)}")
    for idx, (l1, l2) in enumerate(conflicts, 1):
      print(
          f"  Конфликт {idx}: '{l1.title}' ({l1.start_time}-{l1.end_time}) и"
          f" '{l2.title}' ({l2.start_time}-{l2.end_time})"
      )
  else:
    print("Конфликтов не обнаружено.")

  print("\n=== 5. РЕКОМЕНДАЦИИ ПО ПЕРЕНОСУ ЗАНЯТИЙ ===")
  recs = schedule.get_rescheduling_recommendations()
  for rec in recs:
    print(f"• {rec}")

  print(
      "\n=== 6. ЛЕНИВЫЙ ГЕНЕРАТОР СВОБОДНЫХ ОКОН (Преподаватель: Иванов И.И.,"
      " Понедельник) ==="
  )
  free_windows = schedule.generate_free_intervals(
      "Понедельник", "teacher", "Иванов И.И.", "08:00", "16:00"
  )
  for window in free_windows:
    print(f"Свободное окно: {window[0]} - {window[1]}")

  print("\n=== 7. ПРОВЕРКА С BUFFERPOLICY (Буфер 15 минут) ===")
  buffer_policy = BufferPolicy(buffer_minutes=15)
  schedule_buffer = Schedule(buffer_policy)
  schedule_buffer.lessons = list(schedule.lessons)
  buffer_conflicts = schedule_buffer.find_conflicts()
  print(f"Найдено конфликтов с учетом буферного времени: {len(buffer_conflicts)}")


if __name__ == "__main__":
  main()