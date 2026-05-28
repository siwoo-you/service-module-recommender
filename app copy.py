import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서비스 모듈 추천 시스템",
    page_icon="🧩",
    layout="wide"
)

# -----------------------------
# 1. 생활상황 점수 계산 함수
# -----------------------------
def calculate_situation_scores(target):
    scores = {
        "반복관리": 0,
        "이동상황": 0,
        "공유필요": 0,
        "대기상황": 0,
        "전환상황": 0
    }

    age_group = target["age_group"]
    household_type = target["household_type"]
    service_type = target["service_type"]
    fatigue_level = target["fatigue_level"]
    time_pressure = target["time_pressure"]
    mobility_need = target["mobility_need"]
    sharing_need = target["sharing_need"]

    # 연령대 기반 규칙
    if age_group == "노년층":
        scores["반복관리"] += 30
        scores["공유필요"] += 20
    elif age_group == "청년층":
        scores["이동상황"] += 20
        scores["전환상황"] += 25
        scores["대기상황"] += 15
    elif age_group == "중장년층":
        scores["반복관리"] += 20
        scores["이동상황"] += 20
        scores["공유필요"] += 15
    elif age_group == "청소년":
        scores["전환상황"] += 20
        scores["대기상황"] += 20

    # 가구특성 기반 규칙
    if household_type == "맞벌이가구":
        scores["반복관리"] += 20
        scores["공유필요"] += 25
        scores["전환상황"] += 15
    elif household_type == "돌봄가구":
        scores["공유필요"] += 35
        scores["반복관리"] += 25
    elif household_type == "1인가구":
        scores["반복관리"] += 15
        scores["대기상황"] += 10
    elif household_type == "고령자가구":
        scores["반복관리"] += 30
        scores["공유필요"] += 25

    # 서비스 분야 기반 규칙
    if service_type == "건강관리":
        scores["반복관리"] += 35
        scores["공유필요"] += 15
    elif service_type == "가사":
        scores["반복관리"] += 30
        scores["공유필요"] += 20
    elif service_type == "육아":
        scores["공유필요"] += 35
        scores["반복관리"] += 25
        scores["이동상황"] += 10
    elif service_type == "학습":
        scores["전환상황"] += 25
        scores["대기상황"] += 20
        scores["반복관리"] += 10
    elif service_type == "이동":
        scores["이동상황"] += 40
        scores["전환상황"] += 20
    elif service_type == "웰니스":
        scores["반복관리"] += 20
        scores["대기상황"] += 25
    elif service_type == "여가":
        scores["대기상황"] += 30
        scores["전환상황"] += 10

    # 피로도, 시간부족, 이동/공유 필요성
    if fatigue_level == "높음":
        scores["반복관리"] += 15
        scores["대기상황"] += 10

    if time_pressure == "높음":
        scores["전환상황"] += 20
        scores["반복관리"] += 15

    if mobility_need == "높음":
        scores["이동상황"] += 30
    elif mobility_need == "보통":
        scores["이동상황"] += 15

    if sharing_need == "높음":
        scores["공유필요"] += 30
    elif sharing_need == "보통":
        scores["공유필요"] += 15

    # 최대 100점으로 제한
    for key in scores:
        scores[key] = min(scores[key], 100)

    return scores


# -----------------------------
# 2. 기능 모듈 점수 계산 함수
# -----------------------------
def calculate_module_scores(situation_scores, target):
    module_scores = {
        "알림 모듈": 0,
        "기록 모듈": 0,
        "공유 모듈": 0,
        "요약 모듈": 0,
        "일정 모듈": 0,
        "이동 모듈": 0,
        "추천 모듈": 0,
        "템플릿 모듈": 0
    }

    반복관리 = situation_scores["반복관리"]
    이동상황 = situation_scores["이동상황"]
    공유필요 = situation_scores["공유필요"]
    대기상황 = situation_scores["대기상황"]
    전환상황 = situation_scores["전환상황"]

    module_scores["알림 모듈"] = 반복관리 * 0.4 + 대기상황 * 0.2 + 전환상황 * 0.4
    module_scores["기록 모듈"] = 반복관리 * 0.5 + 공유필요 * 0.3 + 대기상황 * 0.2
    module_scores["공유 모듈"] = 공유필요
    module_scores["요약 모듈"] = 반복관리 * 0.3 + 공유필요 * 0.3 + 전환상황 * 0.4
    module_scores["일정 모듈"] = 이동상황 * 0.3 + 전환상황 * 0.4 + 공유필요 * 0.3
    module_scores["이동 모듈"] = 이동상황
    module_scores["추천 모듈"] = 대기상황 * 0.6 + 반복관리 * 0.2 + 전환상황 * 0.2
    module_scores["템플릿 모듈"] = 반복관리 * 0.4 + 공유필요 * 0.4 + 대기상황 * 0.2

    service_type = target["service_type"]

    # 서비스 분야별 보정
    if service_type == "건강관리":
        module_scores["기록 모듈"] += 15
        module_scores["알림 모듈"] += 10
        module_scores["공유 모듈"] += 10
        module_scores["템플릿 모듈"] += 10
    elif service_type == "육아":
        module_scores["공유 모듈"] += 20
        module_scores["기록 모듈"] += 15
        module_scores["템플릿 모듈"] += 20
        module_scores["알림 모듈"] += 10
    elif service_type == "가사":
        module_scores["공유 모듈"] += 15
        module_scores["알림 모듈"] += 15
        module_scores["템플릿 모듈"] += 10
    elif service_type == "학습":
        module_scores["일정 모듈"] += 15
        module_scores["기록 모듈"] += 10
        module_scores["요약 모듈"] += 10
    elif service_type == "이동":
        module_scores["이동 모듈"] += 20
        module_scores["일정 모듈"] += 15
        module_scores["알림 모듈"] += 10
    elif service_type == "웰니스":
        module_scores["추천 모듈"] += 15
        module_scores["요약 모듈"] += 15
        module_scores["알림 모듈"] += 5

    # 피로도 조정
    if target["fatigue_level"] == "높음":
        module_scores["알림 모듈"] *= 0.8
        module_scores["요약 모듈"] += 10
        module_scores["추천 모듈"] += 5

    for key in module_scores:
        module_scores[key] = round(min(module_scores[key], 100), 1)

    return module_scores


# -----------------------------
# 3. 추천 결과 생성 함수
# -----------------------------
def recommend_modules(target, top_n=4):
    situation_scores = calculate_situation_scores(target)
    module_scores = calculate_module_scores(situation_scores, target)

    sorted_modules = sorted(
        module_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return situation_scores, module_scores, sorted_modules[:top_n]


# -----------------------------
# 4. Streamlit 화면 구성
# -----------------------------
st.title("🧩 생활시간 데이터 기반 B2B 서비스 모듈 추천 시스템")

st.write(
    """
    서비스 기획자가 타깃 사용자 조건을 입력하면,  
    시스템이 생활상황 점수와 기능 모듈 점수를 계산하여 적합한 서비스 모듈 조합을 추천합니다.
    """
)

st.sidebar.header("기획자 입력 조건")

service_type = st.sidebar.selectbox(
    "서비스 분야",
    ["가사", "육아", "건강관리", "학습", "이동", "웰니스", "여가"]
)

age_group = st.sidebar.selectbox(
    "타깃 연령대",
    ["청소년", "청년층", "중장년층", "노년층"]
)

household_type = st.sidebar.selectbox(
    "가구특성",
    ["일반가구", "1인가구", "맞벌이가구", "돌봄가구", "고령자가구"]
)

fatigue_level = st.sidebar.selectbox(
    "피로도",
    ["낮음", "보통", "높음"]
)

time_pressure = st.sidebar.selectbox(
    "시간부족 정도",
    ["낮음", "보통", "높음"]
)

mobility_need = st.sidebar.selectbox(
    "이동 필요성",
    ["낮음", "보통", "높음"]
)

sharing_need = st.sidebar.selectbox(
    "공유 필요성",
    ["낮음", "보통", "높음"]
)

target = {
    "service_type": service_type,
    "age_group": age_group,
    "household_type": household_type,
    "fatigue_level": fatigue_level,
    "time_pressure": time_pressure,
    "mobility_need": mobility_need,
    "sharing_need": sharing_need
}

if st.sidebar.button("모듈 추천 실행"):
    situation_scores, module_scores, recommended = recommend_modules(target)

    st.subheader("1. 입력 조건 요약")
    input_df = pd.DataFrame(target.items(), columns=["입력 항목", "선택값"])
    st.table(input_df)

    st.subheader("2. 생활상황 점수")
    situation_df = pd.DataFrame(
        situation_scores.items(),
        columns=["생활상황", "점수"]
    ).sort_values("점수", ascending=False)

    st.dataframe(situation_df, use_container_width=True)
    st.bar_chart(situation_df.set_index("생활상황"))

    st.subheader("3. 기능 모듈 점수")
    module_df = pd.DataFrame(
        module_scores.items(),
        columns=["기능 모듈", "점수"]
    ).sort_values("점수", ascending=False)

    st.dataframe(module_df, use_container_width=True)
    st.bar_chart(module_df.set_index("기능 모듈"))

    st.subheader("4. 추천 모듈 TOP 4")

    for rank, (module, score) in enumerate(recommended, start=1):
        st.markdown(f"### {rank}순위. {module} — {score}점")

    st.subheader("5. 추천 해석")

    top_module = recommended[0][0]

    if fatigue_level == "높음":
        fatigue_comment = "해당 타깃층은 피로도가 높으므로 잦은 알림보다 요약, 추천, 템플릿 중심 기능을 우선 고려하는 것이 적합합니다."
    else:
        fatigue_comment = "해당 타깃층은 피로도 부담이 크지 않으므로 알림, 기록, 일정 기능을 비교적 적극적으로 활용할 수 있습니다."

    st.write(
        f"""
        선택한 조건에서는 **{top_module}**의 필요도가 가장 높게 나타났습니다.  
        이는 입력된 타깃 조건이 반복관리, 공유필요, 이동, 전환 등의 생활상황 점수에 반영된 결과입니다.  

        {fatigue_comment}
        """
    )

else:
    st.info("왼쪽 입력 조건을 선택한 뒤, **모듈 추천 실행** 버튼을 눌러주세요.")