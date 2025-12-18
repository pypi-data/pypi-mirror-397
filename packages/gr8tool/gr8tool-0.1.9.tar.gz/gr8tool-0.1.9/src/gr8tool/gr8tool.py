import csv
from enum import IntEnum
from functools import wraps
from typing import Optional, Iterable, Iterator, Generator, Callable, TextIO
import os
from dataclasses import dataclass, field
import re
import time
from logger_maoze import anilog, colorize, centerize, generator_loadingbar, iterable_loadingbar, term_cols, casclog
from dotenv import load_dotenv
import datetime as dt
import requests
import json
import pypdf as pdf
import pytermgui as ptg

load_dotenv()

root_dir = "2025WS-EidP"
max_exercise = 14


class Presented(IntEnum):
    never = 0
    once = 1
    twice = 2


'''
    Grading tool for tutors.
'''


@dataclass
class Student:

    name: str

    points_per_exercise: dict[int, float]

    presented: Presented = field(init=False)

    accPoints: float = 0.0

    grading_done: dict[int, bool] = field(default_factory=lambda: {i: False for i in range(1, max_exercise + 1)})

    def __post_init__(self):
        self.points_per_exercise = {i: 0.0 for i in range(1, max_exercise + 1)}
        self.presented = Presented.never
        self.calc_accPoints()

    def __str__(self):
        res = colorize(self.name + ": \n", "magenta")
        for exercise, points in self.points_per_exercise.items():
            res += "     " + colorize(f"exercise-{exercise}", "cyan") + " => " + colorize(f" {points}", "magenta") + " P. \n"
        res += 30 * "_" + "\n Overall points " + colorize(f"<{self.accPoints}>\n", "green")
        return res

    def __eq__(self, other: "Student") -> bool:
        return self.name == other.name

    def __lt__(self, other: "Student") -> bool:
        return self.name < other.name

    def set_points(self, ex, points):
        diff_points = self.points_per_exercise[ex] - points
        self.points_per_exercise[ex] = points
        self.accPoints -= diff_points

    def add_points(self, ex, points):
        self.points_per_exercise[ex] += points
        self.accPoints += points

    def calc_accPoints(self):
        self.accPoints = 0.0
        for _, points in self.points_per_exercise.items():
            self.accPoints += points





def sortout(f):
    @wraps(f)
    def wrapper(*args):
        yield from sorted(f(*args))
    return wrapper


@dataclass
class GradingTool:
    students: dict[str, Student] = field(default_factory=dict)
    files: list[str] = field(default_factory=list, init=False, repr=False)

    # get week starting from 13. Oktober 2025
    week: int = 1

    def __post_init__(self):
        self.week = max_exercise
        self.update(False)
        self.week = dt.datetime.now().isocalendar().week - dt.datetime(2025, 10, 13).isocalendar().week

    def __str__(self):
        res = ''
        for _, student in sorted(self.students.items()):
            res += str(student) + "\n"
        return res

    def update(self, verbose: bool = False):
        for ex in iterable_loadingbar(range(1, self.week + 1), percentage=True):
            self.extract_points_from_exercise(ex, verbose)
        file_patterns = [".md", ".py"]
        self.files = find_files(".", file_patterns, exercise=self.week, verbose=verbose)
        if verbose:
            anilog(colorize(f"--- Found {len(self.files)} files for week {self.week}. ---", "green"))


    def get_student(self, name: str) -> Student | None:
        return self.students[name] if name in self.students.keys() else None

    def add_student(self, name: str, verbose: bool = False):
        if name not in self.students.keys():
            self.students[name] = Student(name, dict())
            if verbose:
                anilog(f"--- Student {self.students[name].name} added. ---")
        return self.students[name]

    def grading_files(self, ex: int, desc: bool = False) -> Iterator[tuple[Student, TextIO]]:
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        grd_files = []
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] != exercise:
                stu_name = root.split("/")[-2]
                student = self.add_student(stu_name)
                grd_files += [(student, root + '/README.md') for file in files if file == "README.md"]
        for student, path in sorted(grd_files, key=lambda x: x[0].name, reverse=desc):
            with open(path, 'r') as f:
                yield student, f

    def grading_file_paths(self, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] != exercise:
                stu_name = root.split("/")[-2]
                student = self.add_student(stu_name)
                for file in files:
                    if file == "README.md":
                        yield (student, root + '/README.md')

    def grading_file_of_student(self, name: str, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        student = self.get_student(name)
        if student is None:
            return None
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] == name:
                for file in files:
                    if file == "README.md":
                        with open(root + '/README.md', 'r') as f:
                            yield f
        return None

    def grading_file_path_of_student(self, name: str, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        student = self.get_student(name)
        if student is None:
            return None
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] == name:
                for file in files:
                    if file == "README.md":
                        return root + '/README.md'
        return None

    def code_files(self, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] != exercise:
                stu_name = root.split("/")[-2]
                student = self.add_student(stu_name)
                for file in files:
                    if file.endswith(".py"):
                        with open(root + '/' + file, 'r') as f:
                            yield (student, f)

    def code_files_paths(self, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] != exercise:
                stu_name = root.split("/")[-2]
                student = self.add_student(stu_name)
                yield from ((student, root + '/' + file) for file in files if file.endswith(".py"))

    def code_files_of_student(self, name: str, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        student = self.get_student(name)
        if student is None:
            return None
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] == name:
                for file in files:
                    if file.endswith(".py"):
                        with open(root + '/' + file, 'r') as f:
                            yield student, f
        return None

    def code_files_paths_of_student(self, name: str, ex: int):
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        student = self.get_student(name)
        if student is None:
            return None
        for root, dirs, files in os.walk(".", topdown=True):
            if exercise in root and root_dir in root and root.split("/")[-2] == name:
                for file in files:
                    if file.endswith(".py"):
                        yield student, root + '/' + file
        return None

    def all_minus_points(self, file) -> float:
        acc = 0
        for line in file:
            try:
                acc += self.extract_minus_points(line)
            except TypeError:
                continue
        return acc

    def max_points_of_file(self, line):
        if "# exercise" in line.rstrip():
            match = re.search(r'\((\d+(\.\d+)?) / (\d+(\.\d+)?)\)', line)
            if match:
                return float(match.group(2))
        return 0

    def minus_points_from_line(self, minus_points, line):
        try:
            minus_points += self.extract_minus_points(line)
        except TypeError:
            pass

    def extract_points(self, line: str) -> float:
        match = re.search(r'\((\d+(\.\d+)?) / (\d+(\.\d+)?)\)', line)
        if match:
            return float(match.group(1))
        raise TypeError

    def extract_minus_points(self, line: str) -> float:
        match = re.search(r'[-\d+.\d+]?', line)
        if match:
            return float(match.group(1))
        raise TypeError

    def extract_points_from_student(self, name: str, verbose: bool = False):
        student = self.get_student(name)
        if student is None:
            print(f"Student {name} not found.")
            return
        if verbose:
            print(f"----Extracting the points of {name}----")
        for ex in student.points_per_exercise.keys():
            for _, gfile in self.grading_files(ex):
                for line in gfile:
                    if "# exercise" in line.rstrip():
                        try:
                            student.add_points(ex, self.extract_points(line))
                        except TypeError:
                            print(f"Points for {name} could not be extracted.")

    def extract_points_from_exercise(self, ex: int, verbose: bool = False):
        """
            Searches in all student directories for the markdown file to
            extract the points.
        """
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        if verbose:
            print(f"----Extracting the points of {exercise}----")
        for student, gfile in self.grading_files(ex):
            if verbose:
                print(student.name)
            for line in gfile:
                if "# exercise" in line.rstrip():
                    if verbose:
                        print(line)
                    try:
                        student.set_points(ex, self.extract_points(line))
                    except TypeError:
                        pass

    def check_grading_of_student(self, name: str, ex: int):
        """
            Checks the grading of the student {name} for exercise {ex}.
        """
        student = self.get_student(name)
        if student is None:
            print(f"Student {name} not found.")
            return
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        anilog(f"----Checking the grading of {student.name} for {exercise}----")
        for gfile in self.grading_file_of_student(name, ex):
            exercise_points = 0.0
            total_points = 0.0
            try:
                for line in gfile:
                    if "# " + exercise in line.rstrip():
                        total_points += self.extract_points(line)
                    if "# Aufgabe" in line.rstrip():
                        exercise_points += self.extract_points(line)
            except TypeError:
                anilog(f"❌ Grading of {student.name} not done.")
            else:
                if not exercise_points == total_points and ex != 14:
                    anilog(f"❌ Grading of {student.name} is not correct. \n" +
                           f" ===> Calculation of points differ -> {exercise_points} <--> {total_points}")
                    student.grading_done[ex] = False
                else:
                    anilog(f"✅  Grading of {student.name} done ----")
                    student.grading_done[ex] = True

    def check_grading_of_exercise(self, ex: int):
        """
            Checks the grading of the exercise.
        """
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        anilog(f"----Checking the grading of {exercise}----")
        done = 0
        missing = 0
        for student, gfile in self.grading_files(ex):
            exercise_points = 0.0
            total_points = 0.0
            try:
                for line in gfile:
                    if "# " + exercise in line.rstrip():
                        total_points += self.extract_points(line)
                    if "# Aufgabe" in line.rstrip():
                        exercise_points += self.extract_points(line)
            except TypeError:
                anilog(f"❌ Grading of {student.name} not done.", 0.005)
                missing += 1
            else:
                if not exercise_points == total_points and ex != 14:
                    anilog(f"❌ Grading of {student.name} is not correct. \n" +
                           f" ===> Calculation of points differ -> {exercise_points} <--> {total_points}", 0.005)
                    student.grading_done[ex] = False
                    missing += 1
                else:
                    anilog(f"✅  Grading of {student.name} done ----", 0.005)
                    student.grading_done[ex] = True
                    done += 1
        if missing == 0:
            anilog(colorize(f"All {done} gradings done.", "green") + "✅")
        else:
            anilog(colorize(f"[{done}|{done + missing}] gradings done. {missing} missing.", "magenta"))

    def check_grading_of_exercises_until(self, until):
        """
            Checks grading of the exercises until a certain exercise.
        """
        for ex in range(1, until):
            self.check_grading_of_exercise(ex)

    def grade_exercise(self, ex: int):
        """
            Grades the student files for exercise {ex}.
        """
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        anilog(f"----Checking the grading of {exercise}----")
        for student in self.students.values():
            self.grade_exercise_of_student(student.name, ex)

    def grade_exercise_of_student(self, name: str, ex: int):
        """
            Grades the student files for exercise {ex}.
        """
        student = self.get_student(name)
        if not student:
            anilog(colorize(f"Student {name} not found.", "red"))
            return
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        sheet = "sheet" + str(ex) if ex > 9 else "sheet0" + str(ex)
        anilog(f"Grading {student.name}...\r")
        code_files = list(self.code_files_of_student(student.name, ex))
        if not code_files:
            anilog(colorize(f"❌ No code files found for {student.name}.", "red"))
            return
        prompt = (
            f"Grade the following code files for {exercise}. "
            "Provide a detailed feedback and a score between 0 and the maximum points. "
            "The maximum points for this exercise is 10.0. "
        )
        for _, code_file in self.code_files_of_student(student.name, ex):
            prompt += f"\n\nCode file content:\n```{code_file.read()}```\n"
        try:
            reader = pdf.PdfReader("exercises/" + sheet + ".pdf")
            page = reader.pages[0]
            prompt += f"\n\nThe exercise description is as follows:\n```{page.extract_text()}```\n"
        except FileNotFoundError:
            anilog(colorize(f"❌ Exercise description for {exercise} not found.", "red"))
            return

        prompt += "\n\nProvide the feedback and score in the following format:\n"
        prompt += "Feedback: <detailed feedback>\n"
        prompt += "Score: <score>\n"
        prompt += "<score> should be a table for each subexercise. and I sum of all exercises.\n"
        prompt += "Total: <total_score>\n"
        prompt += "Compare your grading with the grading as seen in " + str(self.grading_file_path_of_student(student.name, ex)) + "\n"

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "anthropic/claude-haiku-4.5",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                                },

                            ],
                        }
                ]
            })
        )
        score_match = re.search(r'Total:\s*(\d+(\.\d+)?)', response.text)
        if score_match:
            score = float(score_match.group(1))
            student.set_points(ex, score)
            anilog(colorize(f"✅ Graded {student.name} with {score} points.", "green"))

        anilog(f"Feedback for {student.name}:\n{colorize(json.loads(response.content)["choices"][0]["message"]["content"], "magenta")}")

    def fix_grading_of_exercise(self, ex: int, subex: int, points: float):
        """
            Fixes the grading of the exercise {ex} and subexercise {subex} to
            {points}.
        """
        exercise = "exercise-" + str(ex) if ex > 9 else "exercise-0" + str(ex)
        if ex == 14:
            exercise = "test-exam"
        anilog(f"----Fixing the grading of {exercise}----")
        for student, gfile in self.grading_files(ex):
            pass

    def check_grading_from_to(self, from_ex: int, to_ex: int):
        """
            Checks grading of the exercises from {from_ex} to {to_ex}.
        """
        for i in range(from_ex, to_ex + 1):
            self.check_grading_of_exercise(i)

    def replace_line_in_grading_files(self, *stu_names, ex, line, text):
        anilog(f"--- Replacing line {line} in grading files of exercise {ex} for students {', '.join(stu_names)}. ---")
        for stu_name in stu_names:
            lines = []
            for file in self.grading_file_of_student(stu_name, ex):
                lines = file.readlines()
                if line < len(lines):
                    lines[line] = text
                    anilog(f"--- Replacing line {line} in {stu_name} file. ---")
                else:
                    anilog(colorize("Couldn't read {stu_name} file.", "red"), 0.005)
            if path := self.grading_file_path_of_student(stu_name, ex):
                with open(path, 'w') as file:
                    file.writelines(lines)
            else:
                anilog(colorize("Couldn't write to {stu_name} file.", "red"), 0.005)

    def add_line_in_end_of_grading_files(self, *stu_names, ex, text):
        anilog(f"--- Repl in grading files of exercise {ex} for students {', '.join(stu_names)}. ---")
        for stu_name in stu_names:
            lines = []
            for file in self.grading_file_of_student(stu_name, ex):
                lines = file.readlines()
                # Get line before the `Build` starts
                line = next((i for i, l in enumerate(lines) if l.startswith("## Build")), len(lines)) - 1
                if line < len(lines):
                    lines[line] = text + "\n" + lines[line]
                    anilog(f"--- Replacing line {line} in {stu_name} file. ---")
                else:
                    anilog(colorize("Couldn't read {stu_name} file.", "red"), 0.005)
            if path := self.grading_file_path_of_student(stu_name, ex):
                with open(path, 'w') as file:
                    file.writelines(lines)
            else:
                anilog(colorize("Couldn't write to {stu_name} file.", "red"), 0.005)

    def student_presented(self, stu_name: str):
        if student := self.get_student(stu_name):
            if student.presented is not Presented.twice:
                student.presented = Presented(student.presented.value + 1)


def find_files(directory: str, file_patterns: str | list[str], exercise: Optional[int] = None, verbose=False) -> list[str]:
    """Find all files with the given name in directory and subdirectories"""
    results = []
    if isinstance(file_patterns, str):
        file_patterns = [file_patterns]
    for root, _, files in generator_loadingbar(os.walk(directory), percentage=True, msg=colorize("Searching files...", "peach")):
        if file_patterns:
            for file in files:
                for pattern in file_patterns:
                    if file.endswith(pattern) and (exercise is None or f"exercise-{'0' if exercise < 10 else ''}{exercise}" in root or f"sheet{'0' if exercise < 10 else ''}{exercise}" in root):
                        results.append(os.path.join(root, file))
                        if verbose:
                            anilog(colorize(f"Found file: {os.path.join(root, file)}\n", "green"), 0)
    return results


def chatbot_setup() -> bool:
    if input(colorize("Enable chatbot?[y/n]: ", "blue")) != "y":
        anilog(colorize("Chatbot disabled!", "red"))
        return False
    anilog(colorize("Setting up chatbot...", "blue"))
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "anthropic/claude-haiku-4.5",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Greet the user and welcome to the grading service for tutors of `Einführung in die Programmierung` (Introduction to Programming).",
                            },
                        ]
                    }
                ],
            })
        )
        if response.status_code in [401, 402, 403, 404]:
            anilog(colorize(json.loads(response.content), "red"), delay=0.005)
        else:
            anilog(centerize(colorize(json.loads(response.content)["choices"][0]["message"]["content"], "yellow")), 0.005)
        return True
    except (requests.exceptions.RequestException, KeyError,
            requests.exceptions.ConnectionError) as e:
        anilog(colorize(f"Failed to connect to the chatbot service.\n"
                        f"Exception type: {type(e).__name__}\n"
                        f"Exception message: {e}\n"
                        f"Exception args: {e.args}\n", "red"))
    except KeyboardInterrupt:
        anilog(colorize("\nChatbot disabled!", "red"))
        return False
    return False


def save_read(files: list[str]) -> Iterator[str]:
    for file in files:
        try:
            with open(file, 'r') as f:
                yield f.read()
        except FileNotFoundError:
            continue


def chat(prompt: str, files: list[str] = []):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "anthropic/claude-haiku-4.5",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            *[
                                {
                                    "type": "text",
                                    "text": f"File content:\n```{file}```\n",
                                } for file in save_read(files=files)
                            ]
                        ]
                    }
                ],
            })
        )
        if 400 <= response.status_code <= 428:
            anilog(colorize(json.loads(response.content)["error"], "red"))
        else:
            anilog(centerize(colorize(json.loads(response.content)["choices"][0]["message"]["content"], "blue")), 0.005)
    except (requests.exceptions.RequestException, KeyError, requests.exceptions.ConnectionError) as e:
        anilog(colorize(f"Failed to connect to the chatbot service.\n"
                        f"Exception type: {type(e).__name__}\n"
                        f"Exception message: {e}\n"
                        f"Exception args: {e.args}\n", "red"))
    except KeyboardInterrupt:
        return


def tui():
    def macro_time(fmt: str) -> str:
        return time.strftime(fmt)
    ptg.tim.define("!time", macro_time)  # type: ignore

    with ptg.WindowManager() as manager:
        manager.layout.add_slot("Body")
        manager.add(
            ptg.Window("[bold]The current time is:[/]\n\n[!time 75]%c", box="EMPTY")
            )


def main():
    """
    Constructs an inverted index from a given text file, then asks the user in
    an infinite loop for keyword queries and outputs the title and description
    of up to three matching records.
    """
    available_cmds = "check <ex>, check <ex1> <ex2>, check all, check <student>, update, showall, list, set week=<num>, get week, grade [<student>] [<ex>], open <student> [<ex>], help, sync"
    print(colorize(term_cols * "-", "default"))
    anilog(centerize(colorize(f"Grading tool for EidP {time.strftime('%Y')}.", "blue")))
    print(centerize("Type 'exit' or 'quit' to exit the program."))
    print(centerize(f"Available commands: {available_cmds}"))
    print(colorize(term_cols * "-", "default"))
    anilog(colorize("Loading students and gradings...", "yellow"))
    gt = GradingTool()
    chatbot_available = chatbot_setup()
    anilog(colorize(f"✅ Current week -- {gt.week}", "blue"))
    # verbose = input(colorize("Enable verbose mode?[y/n]: ", "blue")) == "y"
    while inp := input("> "):
        cmd, *subcmds = tuple(inp.split(" "))
        match cmd:
            case "chat":
                if not chatbot_available:
                    chatbot_available = chatbot_setup()
                    if not chatbot_available:
                        continue

                while chat_inp := input("Chat> "):
                    if chat_inp in ["exit", "quit", "back"]:
                        anilog(colorize("Exiting chat...", "magenta"), 0.05)
                        break
                    chat(chat_inp, gt.files)
            case "exit" | "quit":
                anilog(colorize("Exiting...", "magenta"), 0.05)
                break
            case "check":
                if subcmds:
                    param1, *param2 = subcmds
                    if param2 and param2[0].isdigit() and param1.isdigit():
                        if 1 <= (ex1 := int(param1)) <= 14 and 1 <= (ex2 := int(param2[0])) <= 14:
                            gt.check_grading_from_to(ex1, ex2)
                    elif param1.isdigit():
                        if 1 <= (ex := int(param1)) <= 14:
                            gt.check_grading_of_exercise(ex)
                        else:
                            print("Exercise number must be between 1 and 14.")
                    elif param1 == "all":
                        gt.check_grading_from_to(1, gt.week)
                    elif student := gt.get_student(param1):
                        anilog(colorize(f"Checking grading of student {student.name}...", "yellow"))
                        gt.check_grading_of_student(student.name, gt.week)
                    else:
                        print(colorize("Invalid input. check <ex>, check <ex1> <ex2>, check all, check <student>", "red"))
                else:
                    gt.check_grading_of_exercise(gt.week)
            case "update":
                anilog(colorize("Updating gradings.", "yellow"))
                gt.update(True)
            case "showall":
                if not gt.students:
                    anilog(colorize("No student added.", "red"))
                for _, student in gt.students.items():
                    print(str(student))
                    time.sleep(0.2)
            case "list" | "ls":
                if subcmds:
                    param1, *param2 = subcmds
                    if param1.isdigit():
                        if 1 <= (ex := int(param1)) <= 14:
                            anilog(colorize(f"Listing students for exercise {ex}...", "yellow"))
                            if not gt.students:
                                anilog(colorize("No student added.", "red"))
                            pos = 0
                            for student, _ in gt.grading_file_paths(ex):
                                casclog(colorize(student.name, "green" if student.grading_done[ex] else "red"), " | ", pos == 3)
                                pos = (pos + 1) % 4
                            print()
                        else:
                            anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                    else:
                        anilog(colorize("Invalid input. list <exercise>", "red"))
                    continue
                if not gt.students:
                    anilog(colorize("No student added.", "red"))
                pos = 0
                for name in sorted(gt.students):
                    casclog(colorize(name, "green" if gt.students[name].grading_done[gt.week] else "red"), " | ", pos == 3)
                    pos = (pos + 1) % 4
                print()
            case "set":
                if not subcmds:
                    anilog(colorize("Invalid input. set <param>=<value>", "red"))
                    continue
                param, *_ = subcmds
                if param:
                    match param.split("="):
                        case ["week", num] if num.isdigit():
                            gt.week = int(num)
                            anilog(f"✅ Updated current week to {gt.week}")
                        case ["verbose", str(value)]:
                            if value.lower() in ["true", "yes", "1", "y"]:
                                verbose = True
                            elif value.lower() in ["false", "no", "0", "n"]:
                                verbose = False
                            else:
                                anilog(colorize("Invalid value for verbose. Use true/false.", "red"))
                            anilog(f"Verbose mode is {"off" if verbose else "on"}.")
                        case _:
                            anilog("Invalid setting.")
                else:
                    anilog("Invalid input.")
            case "get":
                if not subcmds:
                    anilog(colorize("Invalid input. get <param>", "red"))
                    continue
                param, *_ = subcmds
                if param:
                    match param:
                        case "week":
                            anilog(f"Current week is {gt.week}")
                        case _:
                            anilog("Invalid parameter.")
                else:
                    anilog("Invalid input.")
            case "grade":
                if not subcmds:
                    anilog(colorize(f"Grading current week {gt.week}...", "yellow"))
                    gt.grade_exercise(gt.week)
                    continue
                param, *param2 = subcmds
                if param:
                    student = gt.get_student(param)
                    if param2 and param2[0].isdigit():
                        if 1 <= (ex := int(param2[0])) <= 14:
                            if student:
                                anilog(colorize(f"Grading {student.name} for exercise {ex}...", "yellow"))
                                gt.grade_exercise_of_student(student.name, ex)
                            else:
                                anilog(colorize(f"Student {param} not found.", "red"))
                        else:
                            anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                    elif student:
                        anilog(colorize(f"Grading {student.name} for exercise {gt.week}...", "yellow"))
                        gt.grade_exercise_of_student(student.name, gt.week)
                    elif param.isdigit():
                        if 1 <= (ex := int(param)) <= 14:
                            anilog(colorize(f"Grading all students for exercise {ex}...", "yellow"))
                            gt.grade_exercise(ex)
                        else:
                            anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                    else:
                        anilog(colorize(f"Student {param} not found.", "red"))
                else:
                    anilog(colorize("Invalid input.", "red"))
            case "open" | "vim":
                if not subcmds:
                    anilog(colorize("Invalid input. open <student> [<ex>]", "red"))
                    continue
                param, *param2 = subcmds
                if param:
                    student = gt.get_student(param)
                    if param2 and param2[0].isdigit():
                        if 1 <= (ex := int(param2[0])) <= 14:
                            if student:
                                anilog(colorize(f"Opening directory of {student.name} for exercise {ex}...", "yellow"))
                                os.system(f"vim {gt.grading_file_path_of_student(student.name, ex)}")
                                continue
                            anilog(colorize(f"Student {param} not found.", "red"))
                            continue
                        anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                    elif student:
                        anilog(colorize(f"Opening directory of {student.name}...", "yellow"))
                        os.system(f"vim {gt.grading_file_path_of_student(student.name, gt.week)}")
                    else:
                        anilog(colorize(f"Student {param} not found.", "red"))
                else:
                    anilog(colorize("Invalid input.", "red"))
            case "write":
                if not subcmds:
                    anilog(colorize("Invalid input. write <student> <ex> <line> <text> | <ex> <text> | <student> [<ex>] <text>", "red"))
                    continue
                param1, *param2 = subcmds
                if param2:
                    if param1.isdigit():
                        if 1 <= (ex := int(param1)) <= 14:
                            text = " ".join(param2)
                            gt.add_line_in_end_of_grading_files(*gt.students.keys(), ex=ex, text=text)
                    elif student := gt.get_student(param1):
                        if param2[0].isdigit():
                            if 1 <= (ex := int(param2[0])) <= 14:
                                text = " ".join(param2[1:])
                                gt.add_line_in_end_of_grading_files(student.name, ex=ex, text=text)
                            else:
                                anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                        else:
                            text = " ".join(param2)
                            gt.add_line_in_end_of_grading_files(student.name, ex=gt.week, text=text)
                    else:
                        stu_name = param1
                        if param2[0].isdigit():
                            if 1 <= (ex := int(param2[0])) <= 14:
                                line_str, *text_parts = param2[1:]
                                if line_str.isdigit():
                                    line = int(line_str)
                                    text = " ".join(text_parts)
                                    gt.replace_line_in_grading_files(stu_name, ex=ex, line=line, text=text)
                                else:
                                    anilog(colorize("Line number must be an integer.", "red"))
                            else:
                                anilog(colorize("Exercise number must be between 1 and 14.", "red"))
                        else:
                            anilog(colorize("Invalid input. write <student> <ex> <line> <text> | <ex> <text>", "red"))
                else:
                    anilog(colorize("Invalid input. write <student> <ex> <line> <text> | <ex> <text> | <student> [<ex>] <text>", "red"))
            case "help":
                print(centerize("Type 'exit' or 'quit' to exit the program."))
                print(centerize(f"Available commands: {available_cmds}"))
            case "note":
                anilog(colorize("Opening NOTES.md...", "yellow"))
                os.system(f"touch ü{"0" if gt.week < 10 else ""}{gt.week}/NOTES.md")
                os.system(f"vim ü{"0" if gt.week < 10 else ""}{gt.week}/NOTES.md")
            case "pull":
                anilog(colorize("Pulling all student repos", "blue"))
                os.system("./cli.py --pull")
            case "push":
                anilog(colorize("Pushing all student repos", "blue"))
                commit_msg = input("> Default commit message?[y/n]: ")
                if commit_msg.lower() == "y":
                    if gt.week < 10:
                        os.system(f"""./cli.py --push "★ Feedback exercise-0{gt.week} ★" """)
                    else:
                        os.system(f"""./cli.py --push "★ Feedback exercise-{gt.week} ★" """)
                else:
                    commit_msg = input("> Enter commit message: ")
                    os.system(f"""./cli.py --push "{commit_msg}" """)
            case "sync":
                anilog(colorize("Sync all git repos", "blue"))
                repos = ["solutions", "tutors", "tutor-notes"]
                for repo in repos:
                    anilog(colorize(f"-> {repo}:", "magenta"))
                    os.system(f"git -C {repo} pull --rebase")
            case _ if (student := gt.get_student(cmd)):
                anilog(colorize(f"Showing grading of student {student.name}...", "yellow"))
                anilog(str(student))
            case _:
                anilog(colorize("Unknown command.", "red"))


def setup() -> GradingTool: 
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
            global max_exercise, root_dir
            max_exercise = config.get("max_weeks")
            root_dir = config.get("root_dir")
    except FileNotFoundError:
        anilog(colorize(f"Setting up grading tool for the first time...", "blue"))
        with open("config.json", 'x') as f:
            config = {
                "root_dir": "2025WS-EidP",
                "max_weeks": 14
            }
            json.dump(config, f, indent=4)
    return GradingTool()


if __name__ == "__main__":
#    setup()
    main()
