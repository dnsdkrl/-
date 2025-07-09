import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

st.title("AI 기반 효율적 공부 계획 앱")

# 1. 사용자 입력
st.header("공부 계획 설정")
goal = st.text_input("공부 목표를 입력하세요 (예: 자격증 합격, 토익 점수 향상 등)")
subjects = st.text_area("공부할 과목을 쉼표(,)로 구분하여 입력하세요 (예: 수학, 영어, 과학)").split(',')
subjects = [s.strip() for s in subjects if s.strip()]
daily_hours = st.number_input("하루 공부 가능 시간 (시간 단위)", min_value=1, max_value=24, value=4)

if st.button("공부 계획 생성하기"):
    if not goal or not subjects or daily_hours <= 0:
        st.error("모든 항목을 올바르게 입력해주세요.")
    else:
        st.success("공부 계획이 생성되었습니다!")
        
        # 2. 간단 AI 공부 계획 생성 (과목별 시간 균등 분배)
        hours_per_subject = daily_hours / len(subjects)
        plan = {subject: round(hours_per_subject, 2) for subject in subjects}

        st.subheader("오늘의 공부 계획")
        for sub, hr in plan.items():
            st.write(f"- {sub}: {hr} 시간")

        # 저장된 계획 데이터 프레임으로 관리
        df_plan = pd.DataFrame({
            "과목": list(plan.keys()),
            "계획 공부 시간(시간)": list(plan.values()),
            "실제 공부 시간(시간)": [0]*len(plan)
        })

        st.session_state['df_plan'] = df_plan

# 3. 공부 진행 및 기록
if 'df_plan' in st.session_state:
    st.header("공부 시간 기록하기")
    df_plan = st.session_state['df_plan']

    with st.form(key='study_form'):
        for i, row in df_plan.iterrows():
            hrs = st.number_input(f"{row['과목']} 공부한 시간 입력", min_value=0.0, max_value=24.0, step=0.25, key=f"input_{i}")
            df_plan.at[i, "실제 공부 시간(시간)"] = hrs
        submitted = st.form_submit_button("기록 저장")

        if submitted:
            st.success("공부 시간이 저장되었습니다.")
            st.session_state['df_plan'] = df_plan

    # 4. 공부 성과 시각화
    st.header("오늘의 공부 성과")
    fig, ax = plt.subplots()
    ax.bar(df_plan['과목'], df_plan['실제 공부 시간(시간)'], label='실제 공부 시간', alpha=0.7)
    ax.plot(df_plan['과목'], df_plan['계획 공부 시간(시간)'], color='r', marker='o', linestyle='--', label='계획 공부 시간')
    ax.set_ylabel('시간 (시간)')
    ax.legend()
    st.pyplot(fig)

# 5. 집중 모드 타이머
st.header("집중 모드 타이머")
timer_minutes = st.number_input("집중할 시간 (분)", min_value=1, max_value=120, value=25)
if st.button("타이머 시작"):
    st.write(f"{timer_minutes}분 집중 모드 시작!")
    for remaining in range(timer_minutes*60, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer_str = f'{mins:02d}:{secs:02d}'
        st.write(f"남은 시간: {timer_str}", unsafe_allow_html=True)
        time.sleep(1)
    st.balloons()
    st.success("집중 모드 완료! 수고하셨어요!")
