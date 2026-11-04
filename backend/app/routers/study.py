import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Lesson, Semester, StudyWork, Subject, User
from ..schemas import (
    BreakRange,
    LessonOut,
    LessonsIn,
    SemesterIn,
    SemesterOut,
    StudyOut,
    SubjectIn,
    SubjectOut,
    SubjectPatch,
    WorkIn,
    WorkOut,
    WorkPatch,
)
from ..security import current_user
from ..sync import check_offline

# Study (personal): the current semester, its subjects with weekly classes, assignments and exams.
# Classes are expanded on the client (calendar, Today) and here (Today, reminders) the same way.
router = APIRouter(prefix="/study", tags=["study"])


def breaks_of(s: Semester) -> list[tuple[date, date]]:
    out = []
    for part in filter(None, s.breaks.split(",")):
        a, _, b = part.partition(":")
        out.append((date.fromisoformat(a), date.fromisoformat(b or a)))
    return out


def has_class(lesson: Lesson, s: Semester, day: date) -> bool:
    """Is there this class on this day (weekday, semester dates, breaks)."""
    if not (s.start <= day <= s.end) or (day.weekday() + 1) % 7 != lesson.weekday:
        return False
    return not any(a <= day <= b for a, b in breaks_of(s))


async def current_semester(db: AsyncSession, user_id: int) -> Semester | None:
    """The latest semester (the one being edited in the app)."""
    return await db.scalar(select(Semester).where(Semester.user_id == user_id).order_by(Semester.start.desc(), Semester.id.desc()).limit(1))


def _semester_out(s: Semester) -> SemesterOut:
    return SemesterOut(id=s.id, title=s.title, start=s.start, end=s.end, breaks=[BreakRange(start=a, end=b) for a, b in breaks_of(s)], remind=s.remind)


def _subject_out(s: Subject) -> SubjectOut:
    return SubjectOut(
        id=s.id, name=s.name, teacher=s.teacher, room=s.room, color=s.color, links=json.loads(s.links or "[]"), note=s.note,
        lessons=[LessonOut(id=x.id, subject_id=s.id, weekday=x.weekday, start=x.start, end=x.end, kind=x.kind, room=x.room) for x in s.lessons],
    )


async def _subject(db: AsyncSession, subject_id: int, user: User) -> Subject:
    s = await db.get(Subject, subject_id)
    if s is None or s.user_id != user.id:
        raise HTTPException(404, "Subject not found")
    return s


async def _work(db: AsyncSession, work_id: int, user: User) -> StudyWork:
    w = await db.get(StudyWork, work_id)
    if w is None or w.user_id != user.id:
        raise HTTPException(404, "Work not found")
    return w


@router.get("", response_model=StudyOut)
async def study(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    sem = await current_semester(db, user.id)
    subjects = (await db.scalars(select(Subject).where(Subject.semester_id == sem.id).order_by(Subject.name))).all() if sem else []
    works = (await db.scalars(select(StudyWork).where(StudyWork.user_id == user.id).order_by(StudyWork.due, StudyWork.id))).all()
    return StudyOut(semester=_semester_out(sem) if sem else None, subjects=[_subject_out(s) for s in subjects], works=works)


@router.put("/semester", response_model=SemesterOut)
async def save_semester(body: SemesterIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Create the semester or update the current one."""
    if body.end < body.start or any(b.end < b.start for b in body.breaks):
        raise HTTPException(422, "End before start")
    sem = await current_semester(db, user.id)
    if sem is None:
        sem = Semester(user_id=user.id)
        db.add(sem)
    sem.title, sem.start, sem.end, sem.remind = body.title.strip(), body.start, body.end, body.remind
    sem.breaks = ",".join(f"{b.start}:{b.end}" if b.end != b.start else f"{b.start}" for b in sorted(body.breaks, key=lambda b: b.start))
    await db.commit()
    return _semester_out(sem)


@router.post("/subjects", response_model=SubjectOut, status_code=201)
async def create_subject(body: SubjectIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    sem = await current_semester(db, user.id)
    if sem is None:
        raise HTTPException(409, "Create the semester first")
    s = Subject(
        user_id=user.id, semester_id=sem.id, name=body.name.strip(), teacher=body.teacher.strip(), room=body.room.strip(),
        color=body.color, links=json.dumps([x.model_dump() for x in body.links], ensure_ascii=False), note=body.note,
    )
    s.lessons = []
    db.add(s)
    await db.commit()
    return _subject_out(s)


@router.patch("/subjects/{subject_id}", response_model=SubjectOut)
async def update_subject(subject_id: int, body: SubjectPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    s = await _subject(db, subject_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field == "links":
            s.links = json.dumps([x.model_dump() for x in value or []], ensure_ascii=False)
        elif value is not None:
            setattr(s, field, value.strip() if isinstance(value, str) and field != "note" else value)
    await db.commit()
    return _subject_out(s)


@router.delete("/subjects/{subject_id}", status_code=204)
async def delete_subject(subject_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _subject(db, subject_id, user))
    await db.commit()


@router.put("/lessons", response_model=list[SubjectOut])
async def save_lessons(body: LessonsIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """The whole weekly timetable at once (the table editor): replaces all classes of the semester."""
    sem = await current_semester(db, user.id)
    if sem is None:
        raise HTTPException(409, "Create the semester first")
    subjects = (await db.scalars(select(Subject).where(Subject.semester_id == sem.id))).all()
    ids = {s.id for s in subjects}
    if any(x.subject_id not in ids for x in body.lessons):
        raise HTTPException(404, "Subject not found")
    if any(x.end <= x.start for x in body.lessons):
        raise HTTPException(422, "End must be after start")
    await db.execute(delete(Lesson).where(Lesson.subject_id.in_(ids)))
    db.add_all(Lesson(**x.model_dump()) for x in body.lessons)
    await db.commit()
    for s in subjects:
        await db.refresh(s, ["lessons"])
    return [_subject_out(s) for s in sorted(subjects, key=lambda s: s.name)]


@router.post("/works", response_model=WorkOut, status_code=201)
async def create_work(body: WorkIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if body.subject_id is not None:
        await _subject(db, body.subject_id, user)
    w = StudyWork(user_id=user.id, **body.model_dump())
    w.title = w.title.strip()
    db.add(w)
    await db.commit()
    return w


@router.patch("/works/{work_id}", response_model=WorkOut)
async def update_work(
    work_id: int, body: WorkPatch, request: Request, response: Response, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)
):
    w = await _work(db, work_id, user)
    check_offline(request, response, w.updated_at)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field == "subject_id" and value is not None:
            await _subject(db, value, user)
        if field in ("subject_id", "due_time") or value is not None:
            setattr(w, field, value.strip() if field == "title" else value)
    await db.commit()
    return w


@router.delete("/works/{work_id}", status_code=204)
async def delete_work(work_id: int, request: Request, response: Response, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    w = await _work(db, work_id, user)
    check_offline(request, response, w.updated_at)
    await db.delete(w)
    await db.commit()
