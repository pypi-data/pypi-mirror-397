LECTURE_DATA = {
    "inverse": """
def inverse():
  str=input("Input :") #User input
  print() #한줄 띄우기
  for i in range(len(str)):
    print(str[i::-1]) #inverse the output, str 거꾸로
inverse()

    """,

    "AI": """ 
    [Settings]
    !pip install google
    !pip install -q -U google-genai

    import os
    os.environ['GEMINI_API_KEY'] = "AIzaSyAofx7yVVhnr59u5Q6X0RaRFtrubfwJwhQ"

    from google import genai

    [API Calls]
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=" 나는 IPYNB 파일로 코딩해. 이모티콘, 다른 말 절대 아무것도 하지말고 코드만. 복사해서 바로 사용할 수 있게",
    )

    print(response.text)

    """
}

def get_note(lecture_name):
    return LECTURE_DATA.get(lecture_name, "해당 강의 노트를 찾을 수 없습니다. (예: 함수, lec)")
