import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="생활상황 기반 B2B 서비스 모듈 추천 시스템",
    page_icon="🧩",
    layout="wide"
)

# =====================================================
# 0. 기본 설정
# =====================================================

ROC_WEIGHTS = {
    "직접 측정 변수": 0.611,
    "관련 설명 변수": 0.278,
    "보조 구분 변수": 0.111
}

LIFE_INDICES = [
    "반복·루틴관리 지수",
    "이동·접근성 지수",
    "공유·돌봄조정 지수",
    "대기·틈새시간 활용 지수",
    "활동전환·맥락전환 지수",
    "시간압박 지수",
    "피로·인지부담 지수"
]

MODULES = [
    "이동·실행지원 모듈",
    "계획·구조화 모듈",
    "알림·행동촉진 모듈",
    "기록·피드백 모듈",
    "공유·사회적조정 모듈",
    "추천·개인화지원 모듈"
]

MODULE_EXPLANATIONS = {
    "이동·실행지원 모듈": {
        "핵심 의미": "사용자가 실제 장소로 이동하거나 생활 행동을 실행할 수 있도록 돕는 모듈입니다.",
        "왜 필요한가": "생활서비스는 정보 확인에서 끝나는 것이 아니라 실제 행동으로 이어져야 합니다. 병원 방문, 등하교, 출퇴근, 외출, 방문 돌봄처럼 장소 이동이나 실행 단계가 중요한 서비스에서 필요합니다.",
        "주요 기능 예시": "경로 안내, 방문 예약, 체크인, 위치 기반 안내, 이동 일정 연동, 실행 단계 안내, 현장 도착 확인",
        "서비스 제공자 활용 방식": "서비스 제공자는 이 모듈을 통해 사용자가 해야 할 일을 실제 행동으로 옮기도록 지원할 수 있습니다. 단순 안내가 아니라 이동 경로, 방문 시간, 실행 순서까지 연결해 서비스 완결성을 높일 수 있습니다.",
        "적합 서비스 예시": "이동 서비스, 병원 예약 서비스, 방문 돌봄 서비스, 오프라인 클래스, 생활 심부름 서비스, 복지 방문 서비스"
    },
    "계획·구조화 모듈": {
        "핵심 의미": "사용자가 해야 할 일을 일정, 순서, 절차로 정리해주는 모듈입니다.",
        "왜 필요한가": "반복적으로 해야 할 일이 많거나 시간압박이 높은 경우, 사용자는 무엇을 언제 어떤 순서로 해야 하는지 정리하는 데 부담을 느낍니다.",
        "주요 기능 예시": "일정표, 체크리스트, 루틴 설정, 템플릿, 우선순위 정리, 단계별 수행 가이드, 반복 일정 자동 생성",
        "서비스 제공자 활용 방식": "서비스 제공자는 복잡한 생활 과업을 작은 단계로 나누고, 사용자가 쉽게 따라 할 수 있는 구조를 제공할 수 있습니다. 일정 기능과 템플릿 기능을 묶어 반복 관리 부담을 줄이는 데 활용할 수 있습니다.",
        "적합 서비스 예시": "가사 관리, 육아 일정, 건강관리 루틴, 학습 계획, 운동 루틴, 업무 관리 서비스, 자기계발 서비스"
    },
    "알림·행동촉진 모듈": {
        "핵심 의미": "필요한 시점에 사용자에게 신호를 보내 행동을 유도하는 모듈입니다.",
        "왜 필요한가": "복약, 예약, 마감, 돌봄, 반복 일정처럼 놓치면 문제가 생기는 서비스에서는 사용자가 제때 행동하도록 유도하는 기능이 중요합니다.",
        "주요 기능 예시": "푸시 알림, 마감 알림, 복약 알림, 예약 알림, 반복 알림, 행동 유도 메시지, 지연 시 재알림",
        "서비스 제공자 활용 방식": "서비스 제공자는 이 모듈을 통해 사용자의 행동 누락을 줄이고, 중요한 생활 과업을 제때 수행하도록 유도할 수 있습니다. 다만 피로·인지부담이 높은 타깃에게는 과도한 알림이 부담이 될 수 있으므로 요약형 알림이나 핵심 알림 중심으로 설계하는 것이 적합합니다.",
        "적합 서비스 예시": "건강관리, 복약관리, 육아, 돌봄, 학습 마감 관리, 일정관리 서비스, 병원 예약 서비스"
    },
    "기록·피드백 모듈": {
        "핵심 의미": "사용자의 활동, 상태, 결과를 기록하고 다시 이해 가능한 형태로 보여주는 모듈입니다.",
        "왜 필요한가": "생활관리 서비스에서는 사용자가 무엇을 했는지, 상태가 어떻게 변했는지, 어떤 결과가 있었는지 확인할 수 있어야 합니다.",
        "주요 기능 예시": "활동 기록, 건강 기록, 진행률 표시, 요약 리포트, 통계, 피드백 메시지, 주간·월간 리포트, 상태 변화 그래프",
        "서비스 제공자 활용 방식": "서비스 제공자는 이 모듈을 통해 사용자가 서비스 이용 결과를 체감하게 만들 수 있습니다. 기록된 데이터를 바탕으로 사용자에게 변화, 성과, 문제점을 피드백하여 지속 이용을 유도할 수 있습니다.",
        "적합 서비스 예시": "건강관리, 운동관리, 학습관리, 가사관리, 돌봄 기록, 웰니스 서비스, 자기관리 서비스"
    },
    "공유·사회적조정 모듈": {
        "핵심 의미": "가족, 보호자, 공동 사용자와 정보를 공유하고 역할을 조정하게 돕는 모듈입니다.",
        "왜 필요한가": "육아, 돌봄, 가족 일정, 공동 가사처럼 여러 사람이 함께 관여하는 서비스에서는 정보 공유와 역할 분담이 필요합니다.",
        "주요 기능 예시": "가족 공유, 보호자 알림, 공동 일정, 역할 분담, 권한 설정, 공동 체크리스트, 상태 공유, 담당자 지정",
        "서비스 제공자 활용 방식": "서비스 제공자는 이 모듈을 통해 서비스 이용 단위를 개인에서 가족, 보호자, 공동 사용자 단위로 확장할 수 있습니다. 특히 돌봄 서비스나 육아 서비스에서는 누가 무엇을 했는지 공유하고 조정하는 기능이 중요합니다.",
        "적합 서비스 예시": "육아 서비스, 노인 돌봄, 가족 건강관리, 공동 가사관리, 가족 일정관리, 보호자 연계 서비스"
    },
    "추천·개인화지원 모듈": {
        "핵심 의미": "사용자의 상황, 시간, 피로도, 생활조건에 맞는 선택지를 제안하는 모듈입니다.",
        "왜 필요한가": "사용자가 선택해야 할 옵션이 많거나, 시간이 부족하거나, 피로도가 높으면 직접 탐색하고 판단하는 과정 자체가 부담이 됩니다.",
        "주요 기능 예시": "맞춤 추천, 콘텐츠 추천, 루틴 추천, 서비스 추천, 다음 행동 추천, 개인화 메시지, 상황 기반 제안, 우선순위 추천",
        "서비스 제공자 활용 방식": "서비스 제공자는 동일한 기능을 모든 사용자에게 똑같이 제공하는 대신, 타깃 고객군의 생활상황에 맞는 선택지를 제안할 수 있습니다. 피로·인지부담이 높은 타깃에게는 선택지를 줄여주고, 대기·틈새시간 활용 지수가 높은 타깃에게는 짧게 이용 가능한 서비스를 추천할 수 있습니다.",
        "적합 서비스 예시": "여가 추천, 웰니스 추천, 학습 콘텐츠 추천, 건강 루틴 추천, 맞춤형 생활관리 서비스, 개인화 커머스 서비스"
    }
}

# =====================================================
# 1. 입력값 점수화 함수
# =====================================================

def level_score(value):
    mapping = {
        "낮음": 0.0,
        "보통": 0.5,
        "높음": 1.0
    }
    return mapping.get(value, 0.0)


def yes_no_score(value):
    mapping = {
        "아니오": 0.0,
        "예": 1.0
    }
    return mapping.get(value, 0.0)


def dual_income_score(value):
    mapping = {
        "해당 없음": 0.0,
        "외벌이": 0.5,
        "맞벌이": 1.0
    }
    return mapping.get(value, 0.0)


def work_study_score(value):
    mapping = {
        "비경제활동": 0.0,
        "학생": 0.6,
        "취업자": 0.7,
        "취업+학습 병행": 1.0
    }
    return mapping.get(value, 0.0)


def marital_score(value):
    mapping = {
        "미혼": 0.0,
        "기혼": 0.7,
        "이혼·사별": 0.4
    }
    return mapping.get(value, 0.0)


def age_routine_score(value):
    mapping = {
        "청소년": 0.4,
        "청년층": 0.3,
        "중장년층": 0.6,
        "노년층": 1.0
    }
    return mapping.get(value, 0.0)


def age_mobility_score(value):
    mapping = {
        "청소년": 0.3,
        "청년층": 0.6,
        "중장년층": 0.6,
        "노년층": 0.8
    }
    return mapping.get(value, 0.0)


def age_transition_score(value):
    mapping = {
        "청소년": 0.7,
        "청년층": 0.8,
        "중장년층": 0.7,
        "노년층": 0.4
    }
    return mapping.get(value, 0.0)


def leisure_need_score(value):
    mapping = {
        "만족": 0.0,
        "보통": 0.5,
        "불만족": 1.0
    }
    return mapping.get(value, 0.0)


def avg(values):
    values = [v for v in values if v is not None]
    if len(values) == 0:
        return 0
    return sum(values) / len(values)


# =====================================================
# 2. 서비스 분야별 생활상황 관련성 점수
# =====================================================

SERVICE_PROFILE = {
    "가사": {
        "반복": 1.0,
        "이동": 0.2,
        "공유": 0.6,
        "대기": 0.2,
        "전환": 0.4,
        "시간압박": 0.5,
        "피로": 0.6
    },
    "육아": {
        "반복": 1.0,
        "이동": 0.5,
        "공유": 1.0,
        "대기": 0.2,
        "전환": 1.0,
        "시간압박": 1.0,
        "피로": 0.8
    },
    "건강관리": {
        "반복": 1.0,
        "이동": 0.4,
        "공유": 0.6,
        "대기": 0.2,
        "전환": 0.3,
        "시간압박": 0.7,
        "피로": 0.7
    },
    "학습": {
        "반복": 0.7,
        "이동": 0.1,
        "공유": 0.2,
        "대기": 0.7,
        "전환": 0.8,
        "시간압박": 0.8,
        "피로": 0.6
    },
    "이동": {
        "반복": 0.2,
        "이동": 1.0,
        "공유": 0.2,
        "대기": 0.4,
        "전환": 0.8,
        "시간압박": 0.8,
        "피로": 0.4
    },
    "웰니스": {
        "반복": 0.6,
        "이동": 0.3,
        "공유": 0.2,
        "대기": 0.8,
        "전환": 0.3,
        "시간압박": 0.3,
        "피로": 0.8
    },
    "여가": {
        "반복": 0.2,
        "이동": 0.4,
        "공유": 0.3,
        "대기": 1.0,
        "전환": 0.4,
        "시간압박": 0.2,
        "피로": 0.5
    }
}


# =====================================================
# 3. 13개 입력조건 → 7개 생활지수 계산
# =====================================================

def calculate_life_indices(target):
    service_type = target["service_type"]
    profile = SERVICE_PROFILE[service_type]

    care_burden = level_score(target["care_burden_level"])
    child_care = level_score(target["child_care_need"])
    elderly_household = yes_no_score(target["elderly_household"])
    dual_income = dual_income_score(target["dual_income"])
    work_study = work_study_score(target["work_study_status"])
    work_burden = level_score(target["work_burden_level"])
    time_pressure = level_score(target["time_pressure"])
    fatigue = level_score(target["fatigue_level"])
    leisure_need = leisure_need_score(target["leisure_satisfaction"])
    marital = marital_score(target["marital_status"])

    age_routine = age_routine_score(target["age_group"])
    age_mobility = age_mobility_score(target["age_group"])
    age_transition = age_transition_score(target["age_group"])

    w_direct = ROC_WEIGHTS["직접 측정 변수"]
    w_related = ROC_WEIGHTS["관련 설명 변수"]
    w_aux = ROC_WEIGHTS["보조 구분 변수"]

    indices = {}

    direct = avg([profile["반복"], care_burden, child_care, elderly_household])
    related = avg([work_study, work_burden, time_pressure])
    aux = avg([age_routine, marital])
    indices["반복·루틴관리 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([profile["이동"]])
    related = avg([work_study, work_burden, elderly_household, time_pressure])
    aux = avg([age_mobility])
    indices["이동·접근성 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([care_burden, child_care])
    related = avg([profile["공유"], dual_income, elderly_household, marital])
    aux = avg([age_routine])
    indices["공유·돌봄조정 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([leisure_need, time_pressure])
    related = avg([profile["대기"], work_burden, work_study])
    aux = avg([age_transition, marital])
    indices["대기·틈새시간 활용 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([work_study, dual_income, child_care, profile["전환"]])
    related = avg([time_pressure, work_burden, care_burden])
    aux = avg([age_transition, marital])
    indices["활동전환·맥락전환 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([time_pressure])
    related = avg([profile["시간압박"], work_burden, dual_income, child_care, care_burden])
    aux = avg([age_transition, marital])
    indices["시간압박 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    direct = avg([fatigue])
    related = avg([profile["피로"], time_pressure, work_burden, care_burden])
    aux = avg([leisure_need, age_routine])
    indices["피로·인지부담 지수"] = 100 * (
        w_direct * direct + w_related * related + w_aux * aux
    )

    indices = {k: round(max(0, min(v, 100)), 1) for k, v in indices.items()}
    return indices


# =====================================================
# 4. QFD 관계행렬: 7개 생활지수 → 6개 기능 모듈
# =====================================================

QFD_MATRIX = pd.DataFrame(
    {
        "이동·실행지원 모듈": [1, 9, 1, 1, 3, 3, 1],
        "계획·구조화 모듈": [9, 3, 3, 3, 9, 9, 3],
        "알림·행동촉진 모듈": [9, 3, 3, 1, 9, 9, 1],
        "기록·피드백 모듈": [9, 1, 9, 3, 3, 1, 9],
        "공유·사회적조정 모듈": [3, 1, 9, 1, 3, 1, 3],
        "추천·개인화지원 모듈": [3, 3, 3, 9, 9, 9, 9],
    },
    index=LIFE_INDICES
)


# =====================================================
# 5. 7개 생활지수 → 6개 기능 모듈 점수 계산
# =====================================================

def calculate_module_scores(life_indices):
    module_scores = {}

    for module in MODULES:
        numerator = 0
        denominator = 0

        for life_index in LIFE_INDICES:
            relation_score = QFD_MATRIX.loc[life_index, module]
            life_score = life_indices[life_index]

            numerator += life_score * relation_score
            denominator += relation_score

        module_scores[module] = round(numerator / denominator, 1)

    return module_scores


def recommend_modules(target, top_n=3):
    life_indices = calculate_life_indices(target)
    module_scores = calculate_module_scores(life_indices)

    sorted_modules = sorted(
        module_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return life_indices, module_scores, sorted_modules[:top_n]


# =====================================================
# 6. Streamlit 화면 구성
# =====================================================

st.title("생활상황 필요도 기반 B2B 서비스 모듈 추천 시스템")

st.write(
    """
    서비스 제공자가 타깃 고객군의 조건을 입력하면,
    시스템이 7개 생활상황 필요도 지수를 계산하고,
    QFD 관계행렬을 이용해 적합한 6개 기능 모듈의 우선순위를 추천합니다.
    """
)

st.sidebar.header("서비스 제공자 입력 조건")

service_type = st.sidebar.selectbox(
    "서비스 분야",
    ["가사", "육아", "건강관리", "학습", "이동", "웰니스", "여가"]
)

gender = st.sidebar.selectbox(
    "성별",
    ["남성", "여성"]
)

age_group = st.sidebar.selectbox(
    "연령대",
    ["청소년", "청년층", "중장년층", "노년층"]
)

marital_status = st.sidebar.selectbox(
    "혼인 상태",
    ["미혼", "기혼", "이혼·사별"]
)

care_burden_level = st.sidebar.selectbox(
    "돌봄 부담 수준",
    ["낮음", "보통", "높음"]
)

child_care_need = st.sidebar.selectbox(
    "자녀 돌봄 필요",
    ["낮음", "보통", "높음"]
)

dual_income = st.sidebar.selectbox(
    "맞벌이 여부",
    ["해당 없음", "외벌이", "맞벌이"]
)

elderly_household = st.sidebar.selectbox(
    "고령자가구 여부",
    ["아니오", "예"]
)

work_study_status = st.sidebar.selectbox(
    "일·학습 상태",
    ["비경제활동", "학생", "취업자", "취업+학습 병행"]
)

work_burden_level = st.sidebar.selectbox(
    "근무 부담 수준",
    ["낮음", "보통", "높음"]
)

time_pressure = st.sidebar.selectbox(
    "시간 부족 정도",
    ["낮음", "보통", "높음"]
)

fatigue_level = st.sidebar.selectbox(
    "피곤함 정도",
    ["낮음", "보통", "높음"]
)

leisure_satisfaction = st.sidebar.selectbox(
    "여가 만족도",
    ["만족", "보통", "불만족"]
)

top_n = st.sidebar.selectbox(
    "추천 모듈 개수",
    [1, 2, 3, 4, 5, 6],
    index=2
)

target = {
    "service_type": service_type,
    "gender": gender,
    "age_group": age_group,
    "marital_status": marital_status,
    "care_burden_level": care_burden_level,
    "child_care_need": child_care_need,
    "dual_income": dual_income,
    "elderly_household": elderly_household,
    "work_study_status": work_study_status,
    "work_burden_level": work_burden_level,
    "time_pressure": time_pressure,
    "fatigue_level": fatigue_level,
    "leisure_satisfaction": leisure_satisfaction
}

if st.sidebar.button("모듈 추천 실행"):
    life_indices, module_scores, recommended = recommend_modules(target, top_n)

    st.subheader("1. 입력 조건 요약")
    input_df = pd.DataFrame(target.items(), columns=["입력 항목", "선택값"])
    st.table(input_df)

    st.info(
        """
        성별은 현재 버전에서는 타깃 고객군을 설명하기 위한 구분 변수로만 사용하고,
        모듈 추천 점수에는 직접 반영하지 않았습니다.
        이는 성별에 따른 기능 필요도를 별도 근거 없이 임의로 차등화하지 않기 위함입니다.
        """
    )

    st.subheader("2. 7개 생활상황 필요도 지수")
    life_df = pd.DataFrame(
        life_indices.items(),
        columns=["생활상황 필요도 지수", "점수"]
    ).sort_values("점수", ascending=False)
    st.table(life_df)

    st.subheader("3. QFD 관계행렬")
    st.write(
        """
        생활상황 필요도 지수와 기능 모듈의 관계를 QFD 방식으로 연결했습니다.
        관계 강도는 약함 1, 보통 3, 강함 9로 설정했습니다.
        """
    )
    st.table(QFD_MATRIX)

    st.subheader("4. 6개 기능 모듈 적합도 점수")
    module_df = pd.DataFrame(
        module_scores.items(),
        columns=["기능 모듈", "점수"]
    ).sort_values("점수", ascending=False)
    st.table(module_df)

    st.subheader(f"5. 추천 모듈 TOP {top_n}")

    for rank, (module, score) in enumerate(recommended, start=1):
        st.markdown(f"### {rank}순위. {module} — {score}점")

    st.subheader("6. 추천 모듈 상세 해석")

    for rank, (module, score) in enumerate(recommended, start=1):
        info = MODULE_EXPLANATIONS[module]

        st.markdown(f"### {rank}순위. {module} — {score}점")

        detail_df = pd.DataFrame(
            [
                ["핵심 의미", info["핵심 의미"]],
                ["왜 필요한가", info["왜 필요한가"]],
                ["주요 기능 예시", info["주요 기능 예시"]],
                ["서비스 제공자 활용 방식", info["서비스 제공자 활용 방식"]],
                ["적합 서비스 예시", info["적합 서비스 예시"]],
            ],
            columns=["구분", "내용"]
        )

        st.table(detail_df)

    st.subheader("7. 추천 해석")

    top_module = recommended[0][0]
    top_life_index = life_df.iloc[0]["생활상황 필요도 지수"]
    top_life_score = life_df.iloc[0]["점수"]

    st.write(
        f"""
        선택한 타깃 조건에서는 **{top_life_index}**가 가장 높게 나타났습니다.
        해당 지수의 점수는 **{top_life_score}점**입니다.

        QFD 관계행렬에 따라 이 생활상황과 강하게 연결된 기능 모듈의 점수가 높게 계산되었고,
        최종적으로 **{top_module}**이 가장 우선적인 모듈로 추천되었습니다.
        """
    )

    st.subheader("8. 계산 방식 요약")

    st.markdown(
        """
        **1단계. 입력조건 → 생활상황 필요도 지수**

        각 생활지수는 직접 측정 변수, 관련 설명 변수, 보조 구분 변수로 구성했습니다.
        ROC 방식에 따라 가중치를 각각 0.611, 0.278, 0.111로 적용했습니다.

        **2단계. 생활상황 필요도 지수 → 기능 모듈 점수**

        7개 생활지수와 6개 기능 모듈의 관계를 QFD 행렬로 구성했습니다.
        관계 강도는 약함 1, 보통 3, 강함 9로 설정했습니다.
        모듈 점수는 생활지수 점수와 QFD 관계점수를 곱한 뒤 가중평균하여 계산했습니다.

        **3단계. 모듈 해석 제공**

        추천된 모듈에 대해 핵심 의미, 필요한 상황, 주요 기능 예시,
        서비스 제공자의 활용 방식, 적합 서비스 예시를 함께 제시했습니다.
        이를 통해 서비스 제공자는 단순히 어떤 모듈이 높은지만 보는 것이 아니라,
        해당 모듈을 실제 서비스 기획에서 어떻게 활용할 수 있는지 판단할 수 있습니다.
        """
    )

else:
    st.info("왼쪽 입력 조건을 선택한 뒤, 모듈 추천 실행 버튼을 눌러주세요.")