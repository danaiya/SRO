class Schedule:
    def __init__(self, policy: ConflictPolicy):
        self.lessons: List[Lesson] = []
        self.policy = policy

    def add_lesson(self, lesson: Lesson) -> Optional[str]:
        conflicts = self.find_conflicts_for(lesson)
        if conflicts:
            return f"Конфликт с занятием ID {conflicts[0].id}"
        self.lessons.append(lesson)
        return None

    def find_conflicts_for(self, new_lesson: Lesson) -> List[Lesson]:
        return [l for l in self.lessons if self.policy.check_conflict(l, new_lesson)]

    def get_conflicts_report(self) -> List[tuple]:
        report = []
        for i in range(len(self.lessons)):
            for j in range(i + 1, len(self.lessons)):
                if self.policy.check_conflict(self.lessons[i], self.lessons[j]):
                    report.append((self.lessons[i], self.lessons[j]))
        return report

    def filter_by_day(self, target_date: date) -> List[Lesson]:
        return [l for l in self.lessons if l.lesson_date == target_date]

    def sort_lessons(self, by: str = 'time') -> List[Lesson]:
        if by == 'time':
            return sorted(self.lessons, key=lambda l: (l.lesson_date, l.start_time))
        elif by == 'group':
            return sorted(self.lessons, key=lambda l: l.group)
        return self.lessons

    def generate_free_windows(self, target_date: date, target_room: str, 
                              work_start: time = time(8, 0), 
                              work_end: time = time(18, 0)) -> Generator[tuple, None, None]:
        """Ленивый генератор свободных окон в аудитории на определенный день."""
        day_lessons = sorted(
            [l for l in self.lessons if l.lesson_date == target_date and l.classroom == target_room],
            key=lambda l: l.start_time
        )
        
        current_time = work_start
        for lesson in day_lessons:
            if current_time < lesson.start_time:
                yield (current_time, lesson.start_time)
            if current_time < lesson.end_time:
                current_time = lesson.end_time
                
        if current_time < work_end:
            yield (current_time, work_end)