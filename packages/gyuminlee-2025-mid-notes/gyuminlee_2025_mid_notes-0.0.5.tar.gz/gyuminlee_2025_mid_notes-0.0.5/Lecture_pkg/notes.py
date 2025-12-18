LECTURE_DATA = {
    "employeeclass": """
import time
import datetime

print("--- 'checktime' 데코레이터 정의 중 ---")

def checktime(func):
    def wrapper(*args, **kwargs):
        start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n--- [{func.__name__}] 작업 시작 (현재 시간: {start_time_str}) ---")
        start_perf = time.perf_counter()
        
        result = func(*args, **kwargs) 
        
        end_perf = time.perf_counter()
        exec_time = end_perf - start_perf
        
        print(f"--- [{func.__name__}] 작업 완료 (총 소요 시간: {exec_time:.6f}초) ---")
        return result
    return wrapper

print("--- 'checktime' 데코레이터 정의 완료 ---")


print("\n--- 기본 'Employee' 클래스 정의 중... ---")

class Employee:
    company_name = "Gyumin Asset Management"

    def __init__(self, name, employee_id, base_salary):
        self.name = name 
        self._employee_id = employee_id
        self.base_salary = base_salary
        print(f"  [신규 입사] {self.name}({self._employee_id})님 환영합니다.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not new_name or len(new_name.strip()) == 0:
            print(f"경고: 이름은 빈 값일 수 없습니다. 변경이 취소됩니다.")
        else:
            self._name = new_name.strip()

    @property
    def email(self):
        email_id = self._name.lower().replace(' ', '')
        return f"{email_id}.{self._employee_id}@{self.company_name.split(' ')[0].lower()}.com"

    @property
    def employee_id(self):
        return self._employee_id

    def calculate_salary(self):
        return self.base_salary

    def work(self):
        print(f"{self.name}({self.employee_id})님이(가) 기본 업무를 봅니다.")

    def __str__(self):
        return f"[직원: {self.name}, 사번: {self.employee_id}, 이메일: {self.email}]"

print("--- 'Employee' 클래스 정의 완료 ---")

print("\n--- 'Manager' 자식 클래스 정의 중... ---")

class Manager(Employee):
    def __init__(self, name, employee_id, base_salary, management_bonus):
        super().__init__(name, employee_id, base_salary)
        self.management_bonus = management_bonus

    def calculate_salary(self):
        total_salary = super().calculate_salary() + self.management_bonus
        return total_salary

    @checktime
    def work(self):
        print(f"  > {self.name} 매니저가 팀 성과를 분석하고 회의를 주관합니다.")
        time.sleep(0.3)
        print(f"  > 회의 완료.")

    def __str__(self):
        return f"[매니저: {self.name}, 사번: {self.employee_id}, 관리팀 보너스: {self.management_bonus}]"

print("--- 'Manager' 클래스 정의 완료 ---")

print("\n--- 'Staff' 자식 클래스 정의 중... ---")

class Staff(Employee):
    def __init__(self, name, employee_id, base_salary, project):
        super().__init__(name, employee_id, base_salary)
        self.project = project

    @checktime
    def work(self):
        print(f"  > {self.name} 스태프가 '{self.project}' 프로젝트 실무를 담당합니다.")
        time.sleep(0.15)
        print(f"  > '{self.project}' 태스크 1개 완료.")
    def __str__(self):
        return f"[스태프: {self.name}, 사번: {self.employee_id}, 담당: {self.project}]"

print("--- 'Staff' 클래스 정의 완료 ---")

print("\n\n" + "="*50)
print("회사 구성원 생성 및 기능 테스트 시작")
print("="*50)

print("\n--- 1. 인스턴스 생성 ---")
m1 = Manager("김철수", "M1001", 7000, 2000)
s1 = Staff("이영희", "S2001", 4500, "신규 펀드 리서치")
s2 = Staff("박지성", "S2002", 4200, "포트폴리오 백테스팅")

print(m1) 
print(s1) 
print(s2)

print("\n--- 2. @property (email) 테스트 ---")
print(f"'{m1.name}'님의 이메일: {m1.email}")
print(f"'{s1.name}'님의 이메일: {s1.email}")

print("\n--- 3. @property (setter) 유효성 검사 테스트 ---")
print(f"'{s2.name}'의 이름 변경 시도 (-> '   ')")
s2.name = "   " 
print(f"현재 이름: {s2.name}")

print(f"\n'{s2.name}'의 이름 변경 시도 (-> '  박지성 리  ')")
s2.name = "  박지성 리  "
print(f"현재 이름: {s2.name}") 
print(f"변경된 이메일: {s2.email}")

print("\n--- 4. 급여 계산 테스트 (메소드 오버라이딩) ---")
print(f"'{m1.name}' 매니저 총 급여: {m1.calculate_salary()} (기본급: {m1.base_salary} + 보너스: {m1.management_bonus})")
print(f"'{s1.name}' 스태프 총 급여: {s1.calculate_salary()} (기본급: {s1.base_salary})")

print("\n--- 5. 업무 수행 (checktime 데코레이터) 테스트 ---")
m1.work()
s1.work() 
s2.work() 

print("\n" + "="*50)
print("모든 테스트 완료")
print("="*50)
    """,

    "dateclass":"""
from datetime import datetime, timedelta

class Date:
    def __init__(self, year=None, month=None, day=None):
        if year and month and day:
            self.date = f"{year}, {month}, {day}"
        else:
            self.date = "today"

    def show(self):
        print(f"date: {self.date}")

    @staticmethod
    def now():
        return Date()

    @staticmethod
    def yesterday(year, month, day):
        d = datetime(year, month, day) - timedelta(days=1)
        return Date(d.year, d.month, d.day)
    
# 실행 예시

a = Date(2022, 4, 7)
a.show()

b = Date.now()
b.show()

c = Date.yesterday(2022, 4, 7)
c.show()
    """,

    "foodclass":"""
class Food(object):
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __repr__(self):
        return f"Food('{self.name}', {self.price})"

    def __lt__(self, other):
        if not isinstance(other, Food):
            return NotImplemented
        return self.price < other.price

    def __add__(self, other):
        if not isinstance(other, Food):
            return NotImplemented
        return Food(f"{self.name}+{other.name}", self.price + other.price)
#테스트
food_1 = Food('아이스크림', 3000)
food_2 = Food('햄버거', 5000)
food_3 = Food('빙수', 8000)

print(food_1)
print(food_2)
print(food_3)

print(food_1 < food_2)   # True
print(food_3 < food_2)   # False

combo = food_1 + food_2
print(combo)
print(combo.price)
    """,

    "leapclass":"""
class DateCalculator:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def is_leap_year(self):
        y = self.year
        return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

    def get_day_of_week(self):
        import datetime
        date = datetime.date(self.year, self.month, self.day)
        return date.strftime("%A")   # Monday, Tuesday 등

try:
    year = int(input("연도를 입력하세요: "))
    month = int(input("월을 입력하세요: "))
    day = int(input("일을 입력하세요: "))
    calc = DateCalculator(year, month, day)
    weekday = calc.get_day_of_week()

    print("──────────────────────────────")
    print(f"입력한 날짜: {year}년 {month}월 {day}일")
    print(f"윤년 여부: {'윤년입니다' if calc.is_leap_year() else '윤년이 아닙니다'}")
    print(f"요일: {weekday}")
    print("──────────────────────────────")

except ValueError:
    print("유효하지 않은 날짜입니다. 다시 입력하세요.")

    """,

    "datetime%":"""
퍼2writefile W_2.py
import sys
import datetime

if len(sys.argv) != 4:
    print("사용법: python W_2.py <year> <month> <day>")
    sys.exit()

year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])

date = datetime.date(year, month, day)
weekday = date.weekday()  # 월(0) ~ 일(6)

weekday_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

print(weekday_kor[weekday])

퍼1run W_2.py 2023 9 29

    """,
    
    "rockpaper":"""
import random

options = ["가위", "바위", "보"]

player = input("가위, 바위, 보 중 하나를 선택하시오: ")

computer = random.choice(options)

print(f"플레이어: {player}")
print(f"컴퓨터: {computer}")

if player == computer:
    print("비겼습니다.")
elif (player == "가위" and computer == "보") or \
     (player == "바위" and computer == "가위") or \
     (player == "보" and computer == "바위"):
    print("당신이 이겼습니다.")
else:
    print("컴퓨터가 이겼습니다.")

    """,

    "leap%":"""
퍼2writefile leapArg.py
import sys
import datetime

if len(sys.argv) != 4:
    print("사용법: python leapArg.py <year> <month> <day>")
    sys.exit()

year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])

def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

date = datetime.date(year, month, day)
weekday = date.weekday()   # 월=0 ~ 일=6

weekday_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

print("윤년" if is_leap(year) else "평년")
print(weekday_kor[weekday])

퍼1run leapArg.py 2018 4 15

    """,

    "scoreclass":"""
class ScoreError(Exception):
    def __init__(self, message="점수는 0점에서 100점 사이의 값이어야 합니다."):
        self.message = message
        super().__init__(self.message)
try:
    score = int(input("점수를 입력하시오: "))
    if score < 0 or score > 100:
        raise ScoreError()  # ScoreError 발생시킴
    print(f"점수는 {score}입니다.")
except ScoreError as e:
    print(e)
except ValueError:
    print("잘못된 입력입니다. 숫자를 입력해주세요.")
    """,

    "listerror":"""
num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

while True:
    try:
        idx_str = input("인덱스를 입력하시오: ")
        idx = int(idx_str)
        print(num[idx])

    except IndexError:
        print("-1")

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        break  # 무한 루프 종료

    except ValueError:
        print("정수를 입력해주세요.")
    """,

    "fileread":"""
    scores = []

with open("score.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()             
    for line in lines:
        scores.append(int(line.strip())) 
print(scores)
    """,

    "filetodic":"""
content = 따3 2 Alice Paul David Bob
4 Cindy Stella Bill
1 Henry Jenny Jessica Erin Tim
3 John Joe Tom 따3

with open("ban_stu.txt", "w", encoding="utf-8") as f:
    f.write(content)

ban_dict = {}

with open("ban_stu.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    data = line.strip().split()
    key = data[0]
    values = data[1:]
    ban_dict[key] = values

for key, values in ban_dict.items():
    print(key, *values)

    """,

    "openwrite":"""
import pickle

with open("information.txt", "wt", encoding="utf-8") as f:
    f.write("3\n")
    f.write("3.14\n")
    f.write("\"3.14\"\n")   # 문자열 형태 그대로 출력
    
with open("information.txt", "rt", encoding="utf-8") as f:
    text_data = f.read()
    print(text_data)

data_list = [3, 3.14, "3.14"]

with open("information.dat", "wb") as f:
    for item in data_list:
        pickle.dump(item, f)

loaded_items = []
with open("information.dat", "rb") as f:
    while True:
        try:
            loaded_items.append(pickle.load(f))
        except EOFError:
            break

print(loaded_items)

    """,

    "personcode":"""
import re

data = 따3
park sunje 890901-1074422
kim sunhee 990103-2079912
따3
pattern = re.compile(r"(\d{6})-(\d)(\d{6})")

def mask_rrn(match: re.Match) -> str:
    front = match.group(1)
    gender_digit = match.group(2)

    if gender_digit in ("1", "3"):
        gender = "남"
    elif gender_digit in ("2", "4"):
        gender = "여"
    else:
        gender = "기타"

    return f"{front}-******* ({gender})"

print(pattern.sub(mask_rrn, data))

sample_text = 따3 홍길동 560922-1089123 02-705-8491
홍길순 560922-2089123 042-7052-8491
김바한솔 911212-1089123 042-705-8491
김연찬 920922-1089123 031-7054-8491
따3
with open("Testdata.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)

with open("Testdata.txt", "r", encoding="utf-8") as f:
    file_data = f.read()

masked_from_file = pattern.sub(mask_rrn, file_data)
print(masked_from_file)
    
    """,

    "html":"""
import re

html = 따3<HEAD>
<TITLE>Seo Maria's Homepage</TITLE>
</HEAD>따3

pattern = re.compile(r'(?<=<title>).*?(?=</title>)', re.IGNORECASE)

match = pattern.search(html)

if match:
    print(match.group())  
else:
    print("매칭되는 제목이 없습니다.")

    """,
    
    "foo":"""
import re

files = "foo.bar, autoexec.bat, sendmail.cf, checksum.exe"
pattern_no_bat = re.compile(
    r'\b\w+\.(?!bat\b)\w+\b', 
    re.IGNORECASE
)
result_no_bat = pattern_no_bat.findall(files)
print("1. bat만 제외:", ", ".join(result_no_bat))

pattern_no_bat_exe = re.compile(
    r'\b\w+\.(?!(?:bat|exe)\b)\w+\b', 
    re.IGNORECASE
)

result_no_bat_exe = pattern_no_bat_exe.findall(files)
print("2. bat, exe 제외:", ", ".join(result_no_bat_exe))
    """,

    "subsquare":"""
import re
text = "Please, square the following numbers, 3 7 11 13 17 19"
def square_num(match):
    num = int(match.group())
    return str(num ** 2)
result = re.sub(r"\d+", square_num, text)
print(result)

    """,

    "price":"""
import re

data = 따3
ABC01: $23.45
HGG42: $5.01
CFXE1: $889.00
XTC99: $69.89
Total items found: 4
따3

prices = re.findall(r"\$(\d+\.\d+)", data)

for p in prices:
    print(p)
    """,

    "pricenumb":"""
import re

data = 따3
I paid $30 for 100 apples,
50 oranges, and 60 pears.
I saved $5 on this order.
따3

prices = re.findall(r"\$(\d+)", data)

all_numbers = re.findall(r"\d+", data)
quantities = [n for n in all_numbers if n not in prices]

print("가격을 나타내는 숫자들")
for p in prices:
    print(p)

print("수량을 나타내는 숫자들")
for q in quantities:
    print(q)

    """,

    "name":"""
employeeclass, dateclass, foodclass,leapclass, 
datetime%, rockpaper, leap%, scoreclass, 
fileread, filetodic, openwrite, personcode, html, foo, 
subsquare, price, pricenumb
    """,

    "end":"""
!pip uninstall gyuminlee-2025-mid-notes -y
!pip cache purge
from IPython.display import clear_output
clear_output()
퍼1history -c
    """,

    "ai": """ 
    !pip install google
    !pip install -q -U google-genai

    import os
    os.environ['GEMINI_API_KEY'] = "AIzaSyAofx7yVVhnr59u5Q6X0RaRFtrubfwJwhQ"

    from google import genai

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=" Using Jupyter Notebook. ONLY codes so I can copy and paste it. NO emoticons, or other words.",
    )

    print(response.text)

    """
}

def get_note(lecture_name):
    return LECTURE_DATA.get(lecture_name, "해당 강의 노트를 찾을 수 없습니다. (예: 함수, lec)")
