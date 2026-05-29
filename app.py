import re
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="생활시간조사 기반 B2B 서비스 모듈 추천 시스템",
    page_icon="🧩",
    layout="wide"
)

# =====================================================
# 0. 데이터 경로
# =====================================================

DATA_PATH = "data/시간량 데이터.csv"

# =====================================================
# 1. 기본 설정
# =====================================================

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

MODULE_COLORS = {
    "이동·실행지원 모듈": "#2563EB",
    "계획·구조화 모듈": "#7C3AED",
    "알림·행동촉진 모듈": "#F97316",
    "기록·피드백 모듈": "#059669",
    "공유·사회적조정 모듈": "#DC2626",
    "추천·개인화지원 모듈": "#0891B2",
}

LIFE_COLORS = {
    "반복·루틴관리 지수": "#7C3AED",
    "이동·접근성 지수": "#2563EB",
    "공유·돌봄조정 지수": "#DC2626",
    "대기·틈새시간 활용 지수": "#0891B2",
    "활동전환·맥락전환 지수": "#F97316",
    "시간압박 지수": "#EAB308",
    "피로·인지부담 지수": "#059669",
}

SERVICE_MODULE_FOCUS = {
    "가사·생활관리": {
        "이동·실행지원 모듈": 0.3,
        "계획·구조화 모듈": 1.0,
        "알림·행동촉진 모듈": 0.8,
        "기록·피드백 모듈": 0.8,
        "공유·사회적조정 모듈": 0.7,
        "추천·개인화지원 모듈": 0.5,
    },
    "육아·가족돌봄": {
        "이동·실행지원 모듈": 0.6,
        "계획·구조화 모듈": 0.9,
        "알림·행동촉진 모듈": 1.0,
        "기록·피드백 모듈": 0.8,
        "공유·사회적조정 모듈": 1.0,
        "추천·개인화지원 모듈": 0.6,
    },
    "건강·운동관리": {
        "이동·실행지원 모듈": 0.5,
        "계획·구조화 모듈": 0.8,
        "알림·행동촉진 모듈": 1.0,
        "기록·피드백 모듈": 1.0,
        "공유·사회적조정 모듈": 0.5,
        "추천·개인화지원 모듈": 0.8,
    },
    "학습·업무집중": {
        "이동·실행지원 모듈": 0.2,
        "계획·구조화 모듈": 1.0,
        "알림·행동촉진 모듈": 0.9,
        "기록·피드백 모듈": 1.0,
        "공유·사회적조정 모듈": 0.4,
        "추천·개인화지원 모듈": 0.8,
    },
    "이동·외출지원": {
        "이동·실행지원 모듈": 1.0,
        "계획·구조화 모듈": 0.7,
        "알림·행동촉진 모듈": 0.8,
        "기록·피드백 모듈": 0.4,
        "공유·사회적조정 모듈": 0.4,
        "추천·개인화지원 모듈": 0.7,
    },
    "여가·문화추천": {
        "이동·실행지원 모듈": 0.5,
        "계획·구조화 모듈": 0.4,
        "알림·행동촉진 모듈": 0.5,
        "기록·피드백 모듈": 0.5,
        "공유·사회적조정 모듈": 0.5,
        "추천·개인화지원 모듈": 1.0,
    },
    "웰니스·휴식수면": {
        "이동·실행지원 모듈": 0.3,
        "계획·구조화 모듈": 0.7,
        "알림·행동촉진 모듈": 0.7,
        "기록·피드백 모듈": 1.0,
        "공유·사회적조정 모듈": 0.3,
        "추천·개인화지원 모듈": 1.0,
    },
}

MODULE_EXPLANATIONS = {
    "이동·실행지원 모듈": {
        "핵심 의미": "사용자가 실제 장소로 이동하거나 생활 행동을 실행할 수 있도록 돕는 모듈입니다.",
        "주요 기능 예시": "경로 안내, 방문 예약, 체크인, 위치 기반 안내, 이동 일정 연동, 실행 단계 안내",
        "서비스 제공자 활용 방식": "정보 제공에서 끝나지 않고 사용자가 실제 행동으로 옮기도록 지원할 수 있습니다.",
    },
    "계획·구조화 모듈": {
        "핵심 의미": "해야 할 일을 일정, 순서, 절차로 정리해주는 모듈입니다.",
        "주요 기능 예시": "일정표, 체크리스트, 루틴 설정, 우선순위 정리, 단계별 수행 가이드",
        "서비스 제공자 활용 방식": "복잡한 생활 과업을 작은 단계로 나누어 반복 관리 부담을 줄일 수 있습니다.",
    },
    "알림·행동촉진 모듈": {
        "핵심 의미": "필요한 시점에 신호를 보내 행동을 유도하는 모듈입니다.",
        "주요 기능 예시": "푸시 알림, 마감 알림, 복약 알림, 예약 알림, 반복 알림, 지연 시 재알림",
        "서비스 제공자 활용 방식": "중요한 생활 과업을 놓치지 않도록 하며 서비스 이탈을 줄일 수 있습니다.",
    },
    "기록·피드백 모듈": {
        "핵심 의미": "활동, 상태, 결과를 기록하고 다시 이해 가능한 형태로 보여주는 모듈입니다.",
        "주요 기능 예시": "활동 기록, 건강 기록, 진행률, 요약 리포트, 통계, 상태 변화 그래프",
        "서비스 제공자 활용 방식": "사용자가 서비스 이용 결과와 변화를 체감하게 만들어 지속 이용을 유도할 수 있습니다.",
    },
    "공유·사회적조정 모듈": {
        "핵심 의미": "가족, 보호자, 공동 사용자와 정보를 공유하고 역할을 조정하게 돕는 모듈입니다.",
        "주요 기능 예시": "가족 공유, 보호자 알림, 공동 일정, 역할 분담, 권한 설정, 공동 체크리스트",
        "서비스 제공자 활용 방식": "개인 단위 서비스를 가족, 보호자, 공동 사용자 단위로 확장할 수 있습니다.",
    },
    "추천·개인화지원 모듈": {
        "핵심 의미": "상황, 시간, 피로도, 생활조건에 맞는 선택지를 제안하는 모듈입니다.",
        "주요 기능 예시": "맞춤 추천, 콘텐츠 추천, 루틴 추천, 다음 행동 추천, 상황 기반 제안",
        "서비스 제공자 활용 방식": "사용자가 직접 탐색하고 판단하는 부담을 줄이고 맞춤형 서비스를 제공할 수 있습니다.",
    },
}

# =====================================================
# 2. 화면 디자인 CSS
# =====================================================

st.markdown(
    """
    <style>
    .section-desc {
        color: #6B7280;
        font-size: 0.95rem;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
    }

    .rank-card {
        border: 1px solid #E5E7EB;
        border-left: 8px solid var(--card-color);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    }

    .rank-card-top {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }

    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 42px;
        height: 30px;
        padding: 0 10px;
        border-radius: 999px;
        background: var(--card-color);
        color: white;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .rank-module {
        font-size: 1.35rem;
        font-weight: 800;
        color: #111827;
    }

    .rank-score {
        font-size: 1.05rem;
        font-weight: 700;
        color: #374151;
        margin-top: 2px;
    }

    .detail-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1.4rem;
        margin-bottom: 0.7rem;
    }

    .detail-score {
        color: #4B5563;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 3. 공공데이터 열/코드 연결 설정
# =====================================================

REQUIRED_COLUMNS = [
    "성별코드", "연령코드", "혼인상태코드", "가구특성_고령자가구구분코드",
    "가구특성_외벌이맞벌이가구구분코드", "가구특성_돌봄가구구분코드",
    "돌봄필요가구원수", "10세미만가구원수", "18세미만자녀수", "미취학자녀수",
    "가구총소득구간코드", "가구원소득구간코드", "직업분류코드", "교육재학코드",
    "경제활동상태코드", "시간부족정도코드", "피곤함정도코드", "여가만족코드", "건강상태코드",
    "주업시간수", "부업시간수", "계절_시간량가중값"
]

GENDER_MAP = {"남성": 1, "여성": 2}
AGE_MAP = {
    "10대": [1],
    "20대": [2],
    "30대": [3],
    "40대": [4],
    "50대": [5],
    "고령층": [6, 7, 8],
}
MARITAL_MAP = {
    "미혼": [1],
    "기혼": [2],
    "사별 및 이혼": [3, 4],
}
ECONOMIC_MAP = {
    "취업자": [1],
    "실업자": [2],
    "비경제활동인구": [3],
}

HOUSEHOLD_TYPE_CODE_MAP = {
    "맞벌이": [10, 20],
    "외벌이": [31, 32, 41, 42],
    "고령자가구": [1, 2, 3, 6, 7],
    "돌봄가구": [1],
}

INCOME_LEVEL_MAP = {
    "저소득": [1, 2, 3],
    "중간소득": [4, 5, 6, 7],
    "고소득": [8, 9, 10, 11],
}

JOB_GROUP_MAP = {
    "관리직": ["1"],
    "전문직": ["2"],
    "사무직": ["3"],
    "서비스직": ["4"],
    "판매직": ["5"],
    "농림어업직": ["6"],
    "제조업": ["7", "8", "9"],
    "운송·물류직": ["8"],
    "기타": ["A"],
}

ACTION_GROUPS = {
    "개인유지수면": ["11", "12", "13", "14"],
    "업무학습": ["21", "22", "23", "24", "25", "26", "31", "32"],
    "가사돌봄": ["41", "42", "43", "44", "45", "46", "49", "51", "52", "53", "54"],
    "이동": ["91", "92", "93", "94", "95", "96", "97", "98"],
    "여가문화": ["61", "62", "71", "72", "73", "74", "81", "82", "84", "85", "89"],
    "건강운동": ["13", "83"],
    "대기휴식": ["241", "312", "851"],
}

DOMAIN_FOR_ENTROPY = [
    "개인유지수면",
    "업무학습",
    "가사돌봄",
    "이동",
    "여가문화",
    "건강운동"
]

# =====================================================
# 4. 데이터 로딩 및 유틸
# =====================================================

@st.cache_data
def load_data(path=DATA_PATH):
    try:
        df = pd.read_csv(path, encoding="cp949", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    df.columns = df.columns.str.strip()
    return df


def safe_numeric(x):
    return pd.to_numeric(x, errors="coerce")


def minmax(s):
    s = safe_numeric(s).replace([np.inf, -np.inf], np.nan).fillna(0)
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)


def reverse_minmax(s):
    return 1 - minmax(s)


def weighted_mean(values, weights=None):
    values = pd.Series(values).astype(float).replace([np.inf, -np.inf], np.nan)

    if weights is None:
        return values.mean()

    weights = pd.Series(weights, index=values.index).astype(float).replace([np.inf, -np.inf], np.nan)
    mask = values.notna() & weights.notna() & (weights > 0)

    if mask.sum() == 0:
        return values.mean()

    return float(np.average(values[mask], weights=weights[mask]))


def weighted_series_mean(df, score_cols, weight_col="계절_시간량가중값"):
    weights = df[weight_col] if weight_col in df.columns else None
    return pd.Series({col: weighted_mean(df[col], weights) for col in score_cols})


def get_action_code(col):
    m = re.search(r"_(\d+)\)", str(col))
    return m.group(1) if m else None


def select_action_columns(df, action_type, code_prefixes):
    selected = []
    for col in df.columns:
        if action_type not in str(col):
            continue
        code = get_action_code(col)
        if code is None:
            continue
        if any(code.startswith(prefix) for prefix in code_prefixes):
            selected.append(col)
    return selected


def validate_data_schema(df):
    rows = []
    for col in REQUIRED_COLUMNS:
        rows.append([col, "있음" if col in df.columns else "없음"])

    rows.append(["주행동시간량 열", f"{sum('주행동시간량' in str(c) for c in df.columns)}개"])
    rows.append(["동시행동시간량 열", f"{sum('동시행동시간량' in str(c) for c in df.columns)}개"])

    return pd.DataFrame(rows, columns=["확인 항목", "상태"])


def unique_codes(df, col):
    if col not in df.columns:
        return []

    vals = df[col].dropna().unique().tolist()

    try:
        return sorted([int(v) if float(v).is_integer() else v for v in vals])
    except Exception:
        return sorted([str(v) for v in vals])


def colored_bar_chart(df, label_col, value_col, color_map, height=330):
    chart_df = df.copy()
    chart_df["색상"] = chart_df[label_col].map(color_map).fillna("#6B7280")

    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X(f"{value_col}:Q", title="점수"),
            y=alt.Y(f"{label_col}:N", sort="-x", title=None),
            color=alt.Color("색상:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip(f"{label_col}:N", title="항목"),
                alt.Tooltip(f"{value_col}:Q", title="점수", format=".1f"),
            ],
        )
        .properties(height=height)
    )

    text = (
        alt.Chart(chart_df)
        .mark_text(align="left", baseline="middle", dx=5, fontSize=13, fontWeight="bold")
        .encode(
            x=alt.X(f"{value_col}:Q"),
            y=alt.Y(f"{label_col}:N", sort="-x"),
            text=alt.Text(f"{value_col}:Q", format=".1f"),
            color=alt.value("#374151"),
        )
    )

    st.altair_chart(chart + text, use_container_width=True)


def render_rank_card(rank, module, score):
    color = MODULE_COLORS.get(module, "#6B7280")
    st.markdown(
        f"""
        <div class="rank-card" style="--card-color:{color};">
            <div class="rank-card-top">
                <span class="rank-badge">{rank}순위</span>
                <span class="rank-module">{module}</span>
            </div>
            <div class="rank-score">최종 점수 {score:.1f}점</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_detail_title(rank, module, score):
    color = MODULE_COLORS.get(module, "#6B7280")
    st.markdown(
        f"""
        <div class="detail-title">
            <span style="color:{color};">{rank}순위</span>. {module}
            <span class="detail-score">— {score:.1f}점</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# 5. 공공데이터에서 내부 계산변수 생성
# =====================================================

def add_internal_features(df):
    out = df.copy()

    for group_name, prefixes in ACTION_GROUPS.items():
        main_cols = select_action_columns(out, "주행동시간량", prefixes)
        sub_cols = select_action_columns(out, "동시행동시간량", prefixes)

        out[f"{group_name}_주행동시간"] = (
            out[main_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            if main_cols else 0
        )

        out[f"{group_name}_동시행동시간"] = (
            out[sub_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            if sub_cols else 0
        )

        out[f"{group_name}_주행동비율"] = out[f"{group_name}_주행동시간"] / 1440
        out[f"{group_name}_동시행동비율"] = out[f"{group_name}_동시행동시간"] / 1440

    main_action_cols = [c for c in out.columns if "주행동시간량" in str(c)]
    sub_action_cols = [c for c in out.columns if "동시행동시간량" in str(c)]

    out["전체_주행동시간"] = (
        out[main_action_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        if main_action_cols else 0
    )

    out["전체_동시행동시간"] = (
        out[sub_action_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        if sub_action_cols else 0
    )

    out["전체_동시행동비율"] = out["전체_동시행동시간"] / 1440

    out["자녀부담"] = (
        safe_numeric(out.get("10세미만가구원수, 0", 0)).fillna(0)
        if "10세미만가구원수, 0" in out.columns else safe_numeric(out.get("10세미만가구원수", 0)).fillna(0)
    ) + safe_numeric(out.get("18세미만자녀수", 0)).fillna(0) + safe_numeric(out.get("미취학자녀수", 0)).fillna(0)

    out["돌봄부담"] = safe_numeric(out.get("돌봄필요가구원수", 0)).fillna(0)
    out["가구부담"] = out["자녀부담"] + out["돌봄부담"]

    out["총노동시간"] = (
        safe_numeric(out.get("주업시간수", 0)).fillna(0)
        + safe_numeric(out.get("부업시간수", 0)).fillna(0)
    )

    domain_cols = [f"{g}_주행동시간" for g in DOMAIN_FOR_ENTROPY]
    domain_mat = out[domain_cols].astype(float).clip(lower=0)
    row_sum = domain_mat.sum(axis=1).replace(0, np.nan)
    p = domain_mat.div(row_sum, axis=0).fillna(0)

    out["활동분산엔트로피"] = (
        -(p * np.log(p.replace(0, np.nan))).sum(axis=1).fillna(0)
        / np.log(len(domain_cols))
    )

    if "가구총소득구간코드" in out.columns and "가구원소득구간코드" in out.columns:
        out["소득구간_분석코드"] = safe_numeric(out["가구총소득구간코드"]).fillna(
            safe_numeric(out["가구원소득구간코드"])
        )
    elif "가구총소득구간코드" in out.columns:
        out["소득구간_분석코드"] = safe_numeric(out["가구총소득구간코드"])
    else:
        out["소득구간_분석코드"] = np.nan

    return out

# =====================================================
# 6. 7개 생활지수용 세부 지표 생성
# =====================================================

def make_life_indicators(feature_df):
    x = feature_df.copy()
    ind = pd.DataFrame(index=x.index)

    ind["시간부족"] = reverse_minmax(x["시간부족정도코드"])
    ind["피곤함"] = reverse_minmax(x["피곤함정도코드"])
    ind["여가불만족"] = minmax(x["여가만족코드"])
    ind["건강나쁨"] = minmax(x["건강상태코드"])

    ind["반복_루틴시간"] = minmax(
        x["개인유지수면_주행동비율"]
        + x["업무학습_주행동비율"]
        + x["가사돌봄_주행동비율"]
    )
    ind["반복_가사돌봄시간"] = minmax(x["가사돌봄_주행동비율"])
    ind["반복_노동시간"] = minmax(x["총노동시간"])
    ind["반복_시간부족"] = ind["시간부족"]

    ind["이동_주행동시간"] = minmax(x["이동_주행동비율"])
    ind["이동_동시행동시간"] = minmax(x["이동_동시행동비율"])
    ind["이동_시간부족"] = ind["시간부족"]

    ind["공유돌봄_돌봄시간"] = minmax(x["가사돌봄_주행동비율"])
    ind["공유돌봄_가구부담"] = minmax(x["가구부담"])
    ind["공유돌봄_자녀부담"] = minmax(x["자녀부담"])
    ind["공유돌봄_돌봄필요"] = minmax(x["돌봄부담"])

    ind["대기틈새_휴식대기시간"] = minmax(x["대기휴식_주행동비율"])
    ind["대기틈새_동시행동"] = minmax(x["전체_동시행동비율"])
    ind["대기틈새_여가불만족"] = ind["여가불만족"]
    ind["대기틈새_시간부족"] = ind["시간부족"]

    ind["전환_활동분산"] = minmax(x["활동분산엔트로피"])
    ind["전환_업무학습"] = minmax(x["업무학습_주행동비율"])
    ind["전환_가사돌봄"] = minmax(x["가사돌봄_주행동비율"])
    ind["전환_이동"] = minmax(x["이동_주행동비율"])
    ind["전환_시간부족"] = ind["시간부족"]

    ind["시간압박_주관부족"] = ind["시간부족"]
    ind["시간압박_업무학습"] = minmax(x["업무학습_주행동비율"])
    ind["시간압박_가사돌봄"] = minmax(x["가사돌봄_주행동비율"])
    ind["시간압박_이동"] = minmax(x["이동_주행동비율"])
    ind["시간압박_가구부담"] = minmax(x["가구부담"])

    ind["피로인지_주관피곤"] = ind["피곤함"]
    ind["피로인지_건강나쁨"] = ind["건강나쁨"]
    ind["피로인지_시간부족"] = ind["시간부족"]
    ind["피로인지_동시행동"] = minmax(x["전체_동시행동비율"])
    ind["피로인지_노동시간"] = minmax(x["총노동시간"])

    return ind.fillna(0).clip(0, 1)


LIFE_INDEX_GROUPS = {
    "반복·루틴관리 지수": ["반복_루틴시간", "반복_가사돌봄시간", "반복_노동시간", "반복_시간부족"],
    "이동·접근성 지수": ["이동_주행동시간", "이동_동시행동시간", "이동_시간부족"],
    "공유·돌봄조정 지수": ["공유돌봄_돌봄시간", "공유돌봄_가구부담", "공유돌봄_자녀부담", "공유돌봄_돌봄필요"],
    "대기·틈새시간 활용 지수": ["대기틈새_휴식대기시간", "대기틈새_동시행동", "대기틈새_여가불만족", "대기틈새_시간부족"],
    "활동전환·맥락전환 지수": ["전환_활동분산", "전환_업무학습", "전환_가사돌봄", "전환_이동", "전환_시간부족"],
    "시간압박 지수": ["시간압박_주관부족", "시간압박_업무학습", "시간압박_가사돌봄", "시간압박_이동", "시간압박_가구부담"],
    "피로·인지부담 지수": ["피로인지_주관피곤", "피로인지_건강나쁨", "피로인지_시간부족", "피로인지_동시행동", "피로인지_노동시간"],
}

# =====================================================
# 7. Entropy-ROC 계산
# =====================================================

def entropy_weights(X):
    X = X.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=0)
    X = X + 1e-12
    col_sum = X.sum(axis=0).replace(0, np.nan)
    P = X.div(col_sum, axis=1).fillna(0)
    n = len(X)

    if n <= 1:
        return pd.Series(np.ones(X.shape[1]) / X.shape[1], index=X.columns)

    E = -(P * np.log(P.replace(0, np.nan))).sum(axis=0).fillna(0) / np.log(n)
    D = 1 - E

    if D.sum() == 0:
        return pd.Series(np.ones(X.shape[1]) / X.shape[1], index=X.columns)

    return D / D.sum()


def roc_weights_by_entropy_rank(entropy_w):
    ranked_cols = list(entropy_w.sort_values(ascending=False).index)
    m = len(ranked_cols)
    roc_vals = []

    for rank in range(1, m + 1):
        roc_vals.append(sum(1 / k for k in range(rank, m + 1)) / m)

    return pd.Series(roc_vals, index=ranked_cols).reindex(entropy_w.index)


def entropy_roc_weights(X, alpha=0.5):
    ew = entropy_weights(X)
    rw = roc_weights_by_entropy_rank(ew)
    final = alpha * ew + (1 - alpha) * rw
    return final / final.sum()


def calculate_life_scores(indicators, alpha=0.5):
    life_score_df = pd.DataFrame(index=indicators.index)
    weight_info = {}

    for life_name, cols in LIFE_INDEX_GROUPS.items():
        X = indicators[cols]
        w = entropy_roc_weights(X, alpha=alpha)
        score = (X * w).sum(axis=1) * 100
        life_score_df[life_name] = score.clip(0, 100)
        weight_info[life_name] = w.round(4)

    return life_score_df, weight_info

# =====================================================
# 8. 타깃 고객군 필터링
# =====================================================

def apply_filter(base_df, filters):
    target = base_df.copy()
    notes = []

    if filters["gender"] != "전체":
        target = target[target["성별코드"] == GENDER_MAP[filters["gender"]]]

    if filters["age_group"] != "전체":
        target = target[target["연령코드"].isin(AGE_MAP[filters["age_group"]])]

    if filters["marital_status"] != "전체":
        target = target[target["혼인상태코드"].isin(MARITAL_MAP[filters["marital_status"]])]

    if filters["economic_status"] != "전체":
        target = target[safe_numeric(target["경제활동상태코드"]).isin(ECONOMIC_MAP[filters["economic_status"]])]

    if filters["household_type"] != "전체":
        h = filters["household_type"]

        if h == "1인가구":
            if "가구원수" in target.columns:
                target = target[safe_numeric(target["가구원수"]) == 1]
            elif "전체가구원수" in target.columns:
                target = target[safe_numeric(target["전체가구원수"]) == 1]
            else:
                target = target[target["가구특성_외벌이맞벌이가구구분코드"].isin([90])]
                notes.append("1인가구는 현재 CSV에서 가구원수 열을 찾지 못해 가구특성_외벌이맞벌이가구구분코드 90을 proxy로 사용했습니다.")

        elif h in ["맞벌이", "외벌이"]:
            target = target[target["가구특성_외벌이맞벌이가구구분코드"].isin(HOUSEHOLD_TYPE_CODE_MAP[h])]
            notes.append(f"{h} 필터는 가구특성_외벌이맞벌이가구구분코드 {HOUSEHOLD_TYPE_CODE_MAP[h]}를 사용했습니다.")

        elif h == "고령자가구":
            target = target[target["가구특성_고령자가구구분코드"].isin(HOUSEHOLD_TYPE_CODE_MAP[h])]

        elif h == "돌봄가구":
            target = target[target["가구특성_돌봄가구구분코드"].isin(HOUSEHOLD_TYPE_CODE_MAP[h])]

    if filters["child_status"] != "전체":
        c = filters["child_status"]

        if c == "자녀 없음":
            target = target[
                (safe_numeric(target["미취학자녀수"]).fillna(0) == 0)
                & (safe_numeric(target["10세미만가구원수"]).fillna(0) == 0)
                & (safe_numeric(target["18세미만자녀수"]).fillna(0) == 0)
            ]
        elif c == "미취학 자녀 있음":
            target = target[safe_numeric(target["미취학자녀수"]).fillna(0) > 0]
        elif c == "10세 미만 자녀 있음":
            target = target[safe_numeric(target["10세미만가구원수"]).fillna(0) > 0]
        elif c == "18세 미만 자녀 있음":
            target = target[safe_numeric(target["18세미만자녀수"]).fillna(0) > 0]

    if filters["care_need"] != "전체":
        if filters["care_need"] == "돌봄 필요 가구원 없음":
            target = target[safe_numeric(target["돌봄필요가구원수"]).fillna(0) == 0]
        elif filters["care_need"] == "돌봄 필요 가구원 있음":
            target = target[safe_numeric(target["돌봄필요가구원수"]).fillna(0) > 0]

    if filters["income_level"] != "전체":
        codes = INCOME_LEVEL_MAP[filters["income_level"]]
        target = target[safe_numeric(target["소득구간_분석코드"]).isin(codes)]

    if filters["job_group"] != "전체":
        j = filters["job_group"]

        if j in JOB_GROUP_MAP:
            job_codes = JOB_GROUP_MAP[j]
            target = target[target["직업분류코드"].astype(str).isin(job_codes)]

            if j == "제조업":
                notes.append("제조업은 산업분류가 아니라 직업분류코드 7·8·9를 이용한 proxy입니다.")

        elif j == "학생":
            target = target[safe_numeric(target["교육재학코드"]).isin([2, 3, 4])]
            notes.append("학생은 교육재학코드 2·3·4를 사용한 proxy입니다.")

        elif j == "무직":
            target = target[safe_numeric(target["경제활동상태코드"]).isin([2, 3])]

    return target, notes

# =====================================================
# 9. QFD 관계행렬 및 모듈 점수
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


def calculate_module_scores(group_life_scores, service_type):
    base_scores = {}
    adjusted_scores = {}
    focus = SERVICE_MODULE_FOCUS[service_type]

    for module in MODULES:
        relation = QFD_MATRIX[module]
        base = (group_life_scores * relation).sum() / relation.sum()
        adjusted = base * (0.90 + 0.10 * focus[module])
        base_scores[module] = round(base, 1)
        adjusted_scores[module] = round(adjusted, 1)

    return pd.Series(base_scores).sort_values(ascending=False), pd.Series(adjusted_scores).sort_values(ascending=False)

# =====================================================
# 10. Streamlit UI
# =====================================================

st.title("생활시간조사 기반 B2B 서비스 모듈 추천 시스템")
st.caption("서비스 제공자는 서비스 분야와 타깃 고객군 조건만 입력하고, 생활지수는 공공데이터에서 자동 계산합니다.")

try:
    raw_df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 불러오지 못했습니다. 파일 경로를 확인하세요: {DATA_PATH}")
    st.exception(e)
    st.stop()

schema_df = validate_data_schema(raw_df)
missing = schema_df[(schema_df["상태"] == "없음")]["확인 항목"].tolist()

if missing:
    st.error("필수 열이 부족합니다. 아래 열 이름을 확인하세요.")
    st.table(schema_df)
    st.stop()

feature_df = add_internal_features(raw_df)
all_indicator_df = make_life_indicators(feature_df)

st.sidebar.header("서비스 제공자 입력 조건")

service_type = st.sidebar.selectbox(
    "서비스 분야",
    ["가사·생활관리", "육아·가족돌봄", "건강·운동관리", "학습·업무집중", "이동·외출지원", "여가·문화추천", "웰니스·휴식수면"]
)

gender = st.sidebar.selectbox("성별", ["전체", "남성", "여성"])
age_group = st.sidebar.selectbox("연령대", ["전체", "10대", "20대", "30대", "40대", "50대", "고령층"])
marital_status = st.sidebar.selectbox("혼인 상태", ["전체", "미혼", "기혼", "사별 및 이혼"])
household_type = st.sidebar.selectbox("가구 유형", ["전체", "1인가구", "맞벌이", "외벌이", "고령자가구", "돌봄가구"])
child_status = st.sidebar.selectbox("자녀 여부", ["전체", "자녀 없음", "미취학 자녀 있음", "10세 미만 자녀 있음", "18세 미만 자녀 있음"])
care_need = st.sidebar.selectbox("돌봄 필요 여부", ["전체", "돌봄 필요 가구원 없음", "돌봄 필요 가구원 있음"])
income_level = st.sidebar.selectbox("소득 구간", ["전체", "저소득", "중간소득", "고소득"])
job_group = st.sidebar.selectbox(
    "직업군",
    ["전체", "사무직", "서비스직", "제조업", "전문직", "관리직", "판매직", "운송·물류직", "농림어업직", "학생", "무직", "기타"]
)
economic_status = st.sidebar.selectbox("경제활동 상태", ["전체", "취업자", "실업자", "비경제활동인구"])
top_n = st.sidebar.selectbox("추천 모듈 개수", [1, 2, 3, 4, 5, 6], index=2)

run_button = st.sidebar.button("모듈 추천 실행")

filters = {
    "service_type": service_type,
    "gender": gender,
    "age_group": age_group,
    "marital_status": marital_status,
    "household_type": household_type,
    "child_status": child_status,
    "care_need": care_need,
    "income_level": income_level,
    "job_group": job_group,
    "economic_status": economic_status,
}

if not run_button:
    st.info("왼쪽에서 서비스 분야와 타깃 고객군 조건을 선택한 뒤, 모듈 추천 실행 버튼을 누르세요.")

    c1, c2, c3 = st.columns(3)
    c1.metric("전체 표본 수", f"{len(raw_df):,}명")
    c2.metric("전체 열 수", f"{raw_df.shape[1]:,}개")
    c3.metric("데이터 경로", DATA_PATH)

    st.stop()

# =====================================================
# 11. 실행 결과
# =====================================================

target_feature_df, filter_notes = apply_filter(feature_df, filters)

if len(target_feature_df) == 0:
    st.error("조건에 해당하는 표본이 없습니다. 필터 조건을 완화하세요.")
    st.stop()

if len(target_feature_df) < 30:
    st.warning(f"현재 조건의 표본 수가 {len(target_feature_df):,}명입니다. 표본이 작아 결과가 불안정할 수 있습니다.")

for note in filter_notes:
    st.warning(note)

target_indicator_df = all_indicator_df.loc[target_feature_df.index]
target_life_score_df, weight_info = calculate_life_scores(target_indicator_df, alpha=0.5)
target_df = pd.concat([target_feature_df, target_life_score_df], axis=1)

weights = target_df["계절_시간량가중값"] if "계절_시간량가중값" in target_df.columns else None

group_life_scores = weighted_series_mean(target_df, LIFE_INDICES, "계절_시간량가중값").round(1)
base_module_scores, adjusted_module_scores = calculate_module_scores(group_life_scores, service_type)
recommended = adjusted_module_scores.head(top_n)

st.subheader("1. 서비스 제공자 입력 조건")

input_df = pd.DataFrame([
    ["서비스 분야", service_type],
    ["성별", gender],
    ["연령대", age_group],
    ["혼인 상태", marital_status],
    ["가구 유형", household_type],
    ["자녀 여부", child_status],
    ["돌봄 필요 여부", care_need],
    ["소득 구간", income_level],
    ["직업군", job_group],
    ["경제활동 상태", economic_status],
    ["추천 모듈 개수", top_n],
], columns=["입력 항목", "선택값"])

st.table(input_df)

st.subheader("2. 타깃 고객군 추출 결과")

col1, col2, col3 = st.columns(3)
col1.metric("전체 표본 수", f"{len(raw_df):,}명")
col2.metric("타깃 표본 수", f"{len(target_df):,}명")
col3.metric("타깃 비율", f"{len(target_df) / len(raw_df) * 100:.1f}%")

st.write(
    """
    서비스 제공자는 생활시간 값을 직접 입력하지 않습니다.
    위 조건으로 공공데이터에서 타깃 집단을 추출한 뒤,
    생활시간·주관상태·가구변수를 자동 계산합니다.
    """
)

st.subheader("3. 공공데이터 기반 내부 계산변수 요약")

internal_cols = [
    "개인유지수면_주행동시간", "업무학습_주행동시간", "가사돌봄_주행동시간",
    "이동_주행동시간", "여가문화_주행동시간", "건강운동_주행동시간",
    "전체_동시행동시간", "가구부담", "총노동시간",
    "시간부족정도코드", "피곤함정도코드", "여가만족코드", "건강상태코드"
]

summary_rows = []
for col in internal_cols:
    if col in target_df.columns:
        summary_rows.append([col, round(weighted_mean(target_df[col], weights), 2)])

summary_df = pd.DataFrame(summary_rows, columns=["내부 계산변수", "타깃 집단 가중평균"])
st.table(summary_df)

st.subheader("4. Entropy-ROC 기반 7개 생활지수")

life_df = group_life_scores.sort_values(ascending=False).reset_index()
life_df.columns = ["생활지수", "점수"]

st.table(life_df)
colored_bar_chart(life_df, "생활지수", "점수", LIFE_COLORS, height=360)

with st.expander("생활지수별 Entropy-ROC 세부 가중치 보기"):
    for life_name, w in weight_info.items():
        st.markdown(f"**{life_name}**")
        tmp = w.reset_index()
        tmp.columns = ["세부 지표", "가중치"]
        st.table(tmp)

st.subheader("5. QFD 관계행렬")
st.write("7개 생활지수와 6개 기능 모듈의 관계를 약함 1, 보통 3, 강함 9로 연결했습니다.")
st.table(QFD_MATRIX)

st.subheader("6. 6개 기능 모듈 점수")

module_df = pd.DataFrame({
    "기능 모듈": adjusted_module_scores.index,
    "QFD 원점수": base_module_scores.reindex(adjusted_module_scores.index).values,
    "서비스 분야 보정 후 점수": adjusted_module_scores.values,
})

st.table(module_df)
colored_bar_chart(module_df, "기능 모듈", "서비스 분야 보정 후 점수", MODULE_COLORS, height=330)

st.subheader(f"7. 추천 모듈 TOP {top_n}")
st.markdown('<div class="section-desc">점수가 높은 모듈일수록 선택한 타깃 고객군과 서비스 분야에 더 적합한 기능입니다.</div>', unsafe_allow_html=True)

for rank, (module, score) in enumerate(recommended.items(), start=1):
    render_rank_card(rank, module, score)

st.subheader("8. 추천 모듈 상세 해석")
st.markdown('<div class="section-desc">각 추천 모듈이 어떤 의미인지, 실제 서비스 기획에서 어떻게 활용할 수 있는지 정리했습니다.</div>', unsafe_allow_html=True)

for rank, (module, score) in enumerate(recommended.items(), start=1):
    info = MODULE_EXPLANATIONS[module]
    render_detail_title(rank, module, score)

    detail_df = pd.DataFrame([
        ["핵심 의미", info["핵심 의미"]],
        ["주요 기능 예시", info["주요 기능 예시"]],
        ["서비스 제공자 활용 방식", info["서비스 제공자 활용 방식"]],
    ], columns=["구분", "내용"])

    st.table(detail_df)

st.subheader("9. 최종 해석")

top_life = life_df.iloc[0]["생활지수"]
top_life_score = life_df.iloc[0]["점수"]
top_module = recommended.index[0]
top_module_score = recommended.iloc[0]

st.write(
    f"""
    선택한 타깃 고객군에서는 **{top_life}**가 가장 높게 나타났습니다.
    점수는 **{top_life_score}점**입니다.

    이 생활지수 구조를 QFD 관계행렬에 연결하고,
    서비스 분야 **{service_type}**의 기능 적합도를 보정한 결과,
    최종적으로 **{top_module}**이 가장 우선적인 기능 모듈로 추천되었습니다.
    최종 점수는 **{top_module_score}점**입니다.
    """
)

st.subheader("10. 계산 흐름 요약")

st.markdown(
    """
    **서비스 제공자 입력**  
    서비스 분야와 타깃 고객군 조건만 입력합니다.

    **공공데이터 필터링**  
    생활시간조사 데이터에서 성별, 연령대, 혼인상태, 가구유형, 자녀 여부, 돌봄 필요 여부,
    소득구간, 직업군, 경제활동상태를 기준으로 해당 집단을 추출합니다.

    **내부 변수 자동 계산**  
    주행동시간량, 동시행동시간량, 시간부족정도, 피곤함정도, 여가만족도, 건강상태,
    가구부담 변수를 자동 계산합니다.

    **Entropy-ROC 생활지수 산출**  
    각 생활지수의 세부 지표별 변별력을 Entropy로 계산하고,
    그 순위를 ROC 가중치와 결합하여 7개 생활지수를 산출합니다.

    **QFD 모듈 추천**  
    7개 생활지수와 6개 기능 모듈의 관계행렬을 이용해 기능 모듈 점수를 계산하고,
    서비스 분야 보정을 적용해 최종 추천 모듈을 제시합니다.
    """
)