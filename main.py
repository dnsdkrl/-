import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ----------------------
# AI 공부 계획 앱 타이틀
# ----------------------
st.title("AI 기반 효율적 공부 계획 앱 + 뽀모도로 타이머 + 피드백")

# ----------------------
# 공부 계획 입력 받기
# ----------------------
st.header("공부 계획 설정")
goal = st.text_input("공부 목표를 입력하세요 (예: 자격증 합격, 토익 점수 향상 등)")
subjects_input = st.text_area("공부할 과목을 쉼표(,)로 구분하여 입력하세요 (예: 수학, 영어, 과학)")
subjects = [s.strip() for s in subjects_input.split(',') if s.strip()]
daily_hours = st.number_input("하루 공부 가능 시간 (시간 단위)", min_value=1, max_value=24, value=4)

if st.button("공부 계획 생성하기"):
    if not goal or not subjects or daily_hours <= 0:
        st.error("모든 항목을 올바르게 입력해주세요.")
    else:
        hours_per_subject = daily_hours / len(subjects)
        plan = {subject: round(hours_per_subject, 2) for subject in subjects}
        st.success("공부 계획이 생성되었습니다!")
        st.subheader("오늘의 공부 계획")
        for sub, hr in plan.items():
            st.write(f"- {sub}: {hr} 시간")

        df_plan = pd.DataFrame({
            "과목": list(plan.keys()),
            "계획 공부 시간(시간)": list(plan.values()),
            "실제 공부 시간(시간)": [0]*len(plan)
        })
        st.session_state['df_plan'] = df_plan

# ----------------------
# 공부 시간 기록 & 시각화
# ----------------------
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

    # 성과 시각화
    st.header("오늘의 공부 성과")
    fig, ax = plt.subplots()
    ax.bar(df_plan['과목'], df_plan['실제 공부 시간(시간)'], label='실제 공부 시간', alpha=0.7)
    ax.plot(df_plan['과목'], df_plan['계획 공부 시간(시간)'], color='r', marker='o', linestyle='--', label='계획 공부 시간')
    ax.set_ylabel('시간 (시간)')
    ax.legend()
    st.pyplot(fig)

    # ----------------------
    # 피드백
    # ----------------------
    st.header("오늘의 피드백")
    feedbacks = []
    for _, row in df_plan.iterrows():
        diff = row["실제 공부 시간(시간)"] - row["계획 공부 시간(시간)"]
        if diff < -0.5:
            feedbacks.append(f"{row['과목']}: 계획보다 공부 시간이 적어요. 내일 더 집중해봐요!")
        elif diff > 0.5:
            feedbacks.append(f"{row['과목']}: 계획보다 공부 시간이 많네요! 잘했어요.")
        else:
            feedbacks.append(f"{row['과목']}: 계획한 만큼 공부했어요. 꾸준히 하세요!")
    for fb in feedbacks:
        st.write("- ", fb)

    satisfaction = st.slider("오늘 공부 만족도는 어땠나요?", 1, 5, 3)
    st.write(f"만족도 점수: {satisfaction}/5")

# ----------------------
# 뽀모도로 스타일 타이머 (자동 새로고침 방식)
# ----------------------
def draw_timer(remaining_sec, total_sec):
    percent = remaining_sec / total_sec if total_sec else 0
    fig = go.Figure(go.Pie(
        values=[percent, 1 - percent],
        labels=['남은 시간', '지난 시간'],
        hole=0.7,
        marker_colors=['#EF553B', '#E5ECF6'],
        textinfo='none',
        sort=False,
        direction='clockwise'
    ))
    fig.update_layout(showlegend=False,
                      margin=dict(t=0,b=0,l=0,r=0),
                      annotations=[dict(text=f"{remaining_sec//60:02d}:{remaining_sec%60:02d}", 
                                        x=0.5, y=0.5, font_size=40, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'remaining_sec' not in st.session_state:
    st.session_state.remaining_sec = 25 * 60
if 'total_sec' not in st.session_state:
    st.session_state.total_sec = st.session_state.remaining_sec

# 1초마다 페이지 자동 새로고침
timer_count = st_autorefresh(interval=1000, limit=None, key="timer_autorefresh")

st.header("뽀모도로 스타일 타이머")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("시작"):
        st.session_state.timer_running = True
with col2:
    if st.button("일시정지"):
        st.session_state.timer_running = False
with col3:
    if st.button("종료"):
        st.session_state.timer_running = False
        st.session_state.remaining_sec = st.session_state.total_sec

if st.session_state.timer_running and st.session_state.remaining_sec > 0:
    st.session_state.remaining_sec -= 1

draw_timer(st.session_state.remaining_sec, st.session_state.total_sec)

if st.session_state.remaining_sec == 0 and st.session_state.timer_running:
    st.session_state.timer_running = False
    st.balloons()
    st.success("시간 종료! 수고하셨어요!")
