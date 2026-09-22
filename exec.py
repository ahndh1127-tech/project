import streamlit as st

# 앱 제목 설정
st.title("자기소개 앱")
st.write("아래 정보를 입력하고 '소개 보기' 버튼을 눌러주세요!")

# 사용자 입력 받기
name = st.text_input("이름")
job = st.text_input("직업")
hobby = st.text_input("취미")

# '소개 보기' 버튼 생성
if st.button("소개 보기"):
    # 필수 입력값이 비어있는지 확인
    if name and job and hobby:
        st.success(f"저는 {job}으로 일하는 {name}입니다. 취미는 {hobby}예요.")
    else:
        st.warning("이름, 직업, 취미를 모두 입력해 주세요!")
        