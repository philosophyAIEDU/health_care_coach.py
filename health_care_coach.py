# 필요한 라이브러리 임포트
import streamlit as st
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from datetime import datetime

# ============================================================================
# 에이전틱 워크플로우 기반 헬스 케어 코치 시스템
# 3명의 특화된 헬스 케어 코치가 팀을 이루어 사용자를 지원
# ============================================================================

class HealthCoachTeam:
    """AI 기반 헬스 케어 코치 팀을 관리하는 클래스"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = GenerativeModel('gemini-2.5-pro-preview-05-06')
        
        # 3명의 특화된 헬스 케어 코치 초기화
        self.assessment_coach = HealthAssessmentCoach(self.model)  # 건강 평가 및 진단 전문가
        self.nutrition_coach = NutritionCoach(self.model)     # 영양 및 식이 전문가
        self.fitness_coach = FitnessCoach(self.model)  # 운동 및 활동 전문가
        
        # 워크플로우 로그 초기화
        self.workflow_logs = []
    
    def get_health_advice(self, service_type, input_data):
        """사용자 요청에 따라 3명의 코치가 순차적으로 협업하여 조언 제공"""
        # 워크플로우 기록 시작
        workflow_log = {
            "service_type": service_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "coaches_involved": ["HealthAssessmentCoach", "NutritionCoach", "FitnessCoach"],
            "steps": []
        }
        
        # 1단계: 건강 평가 코치의 초기 분석 및 제안
        st.markdown("### 1단계: 건강 상태 평가 및 분석 중...")
        with st.spinner("건강 평가 코치가 분석 중입니다..."):
            initial_assessment = self.assessment_coach.analyze(service_type, input_data)
            workflow_log["steps"].append({
                "coach": "HealthAssessmentCoach",
                "action": "initial_assessment"
            })
        
        # 2단계: 영양 코치의 영양 분석 및 식단 계획 추가
        st.markdown("### 2단계: 영양 분석 및 식단 계획 수립 중...")
        with st.spinner("영양 코치가 식단을 분석 중입니다..."):
            nutrition_enhanced = self.nutrition_coach.enhance(initial_assessment, service_type, input_data)
            workflow_log["steps"].append({
                "coach": "NutritionCoach",
                "action": "nutrition_enhancement"
            })
        
        # 3단계: 피트니스 코치의 운동 계획 및 실행 전략 최적화
        st.markdown("### 3단계: 운동 계획 및 실행 전략 최적화 중...")
        with st.spinner("피트니스 코치가 최종 조언을 준비 중입니다..."):
            final_advice = self.fitness_coach.finalize(nutrition_enhanced, service_type, input_data)
            workflow_log["steps"].append({
                "coach": "FitnessCoach",
                "action": "finalization"
            })
        
        # 워크플로우 로그 저장
        self.workflow_logs.append(workflow_log)
        
        # 각 코치별 결과를 모두 반환
        return {
            "assessment": initial_assessment,
            "nutrition": nutrition_enhanced,
            "fitness": final_advice
        }


class HealthAssessmentCoach:
    """건강 평가 및 진단 전문 코치"""
    
    def __init__(self, model):
        self.model = model
        self.expertise = "health_assessment"
        self.coach_name = "김건강 평가 코치"
        self.coach_intro = """
        안녕하세요, 김건강 평가 코치입니다. 
        저는 전체적인 건강 상태 평가와 건강 위험 요소 분석을 전문으로 합니다.
        15년간의 건강 평가 및 예방 의학 경험을 바탕으로 여러분의 건강 상태를 정확히 파악하고 목표를 설정하겠습니다.
        """
    
    def analyze(self, service_type, input_data):
        """사용자 요청에 대한 건강 평가 및 분석 수행"""
        # 서비스 유형별 맞춤 프롬프트 생성
        if service_type == "체중 관리":
            prompt = self._create_weight_management_prompt(input_data)
        elif service_type == "체력 향상":
            prompt = self._create_fitness_improvement_prompt(input_data)
        elif service_type == "식습관 개선":
            prompt = self._create_diet_improvement_prompt(input_data)
        elif service_type == "건강 검진 결과 분석":
            prompt = self._create_health_checkup_prompt(input_data)
        else:
            prompt = self._create_general_health_prompt(input_data, service_type)
        
        # 코치 정보 추가
        prompt = f"""
        당신은 '{self.coach_name}'이라는 건강 평가 전문 코치입니다.
        {self.coach_intro}
        
        {prompt}
        
        분석 결과에 현재 건강 상태, 위험 요소, 개선 가능성을 반드시 포함해 주세요.
        전문적이면서도 이해하기 쉬운 언어로 설명해 주세요.
        """
        
        # AI 모델을 통한 응답 생성
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_weight_management_prompt(self, input_data):
        return f"""
        다음 체중 관리 정보를 바탕으로 건강 상태를 평가해주세요:
        
        키: {input_data.get('height', '')} / 현재 체중: {input_data.get('current_weight', '')}
        목표 체중: {input_data.get('target_weight', '')} / 나이: {input_data.get('age', '')}
        성별: {input_data.get('gender', '')} / 활동 수준: {input_data.get('activity_level', '')}
        건강 이슈: {input_data.get('health_issues', '')}
        
        다음 항목을 포함하는 건강 평가를 제공해주세요:
        1. 현재 BMI 및 체중 상태 평가
        2. 목표 체중의 적절성 및 건강한 체중 범위 제안
        3. 현재 체중 상태와 관련된 건강 위험 요소
        4. 체중 관리 목표 달성을 위한 기본 건강 지표
        5. 고려해야 할 신체적 제한이나 건강 이슈
        """
    
    def _create_fitness_improvement_prompt(self, input_data):
        return f"""
        다음 체력 향상 정보를 바탕으로 건강 상태를 평가해주세요:
        
        현재 체력 상태: {input_data.get('current_fitness', '')}
        운동 목표: {input_data.get('fitness_goals', '')}
        나이/성별: {input_data.get('age', '')}/{input_data.get('gender', '')}
        건강 이슈: {input_data.get('health_issues', '')}
        
        다음 항목을 포함하는 체력 평가를 작성해주세요:
        1. 현재 체력 상태의 종합적 평가
        2. 체력 목표의 적절성 및 현실적 달성 가능성
        3. 체력 향상 과정에서 고려해야 할 건강 위험 요소
        4. 나이와 성별을 고려한 적절한 체력 지표
        5. 기존 건강 이슈가 체력 향상에 미치는 영향
        """
    
    def _create_diet_improvement_prompt(self, input_data):
        return f"""
        다음 식습관 정보를 바탕으로 영양 상태를 평가해주세요:
        
        현재 식습관: {input_data.get('current_diet', '')}
        식이 목표: {input_data.get('diet_goals', '')}
        알레르기/제한사항: {input_data.get('diet_restrictions', '')}
        
        다음 구조로 영양 평가를 제시해주세요:
        1. 현재 식습관의 종합적 평가 (영양소 균형, 과부족 영양소, 건강 영향)
        2. 식이 목표의 적절성 평가 (건강 관점 타당성, 조정 사항, 달성 가능성)
        3. 영양 관련 위험 요소 식별 (잠재적 건강 위험, 알레르기 영향, 건강 이슈 연관성)
        """
    
    def _create_health_checkup_prompt(self, input_data):
        return f"""
        다음 건강 검진 결과를 분석해주세요:
        
        혈압: {input_data.get('blood_pressure', '')}
        혈당: {input_data.get('blood_sugar', '')}
        콜레스테롤: {input_data.get('cholesterol', '')}
        나이/성별: {input_data.get('age', '')}/{input_data.get('gender', '')}
        가족력: {input_data.get('family_history', '')}
        
        다음 구조로 건강 검진 결과 분석을 제시해주세요:
        1. 각 건강 지표의 평가 (정상 범위 비교, 위험 수준, 연령별 분석)
        2. 종합적 건강 상태 평가 (강점, 우려 영역, 잠재 위험)
        3. 가족력 및 위험 요소 분석 (유전적 요인, 장기적 리스크, 우선 관리 영역)
        """
    
    def _create_general_health_prompt(self, input_data, service_type):
        return f"""
        다음 {service_type} 요청에 대해 건강 평가 관점에서 분석해주세요:
        
        요청 내용: {str(input_data)}
        
        현재 건강 상태, 잠재적 위험 요소, 개선 가능성 관점에서 종합적인 평가를 제공해주세요.
        """


class NutritionCoach:
    """영양 및 식이 전문 코치"""
    
    def __init__(self, model):
        self.model = model
        self.expertise = "nutrition_planning"
        self.coach_name = "이영양 코치"
        self.coach_intro = """
        안녕하세요, 이영양 코치입니다.
        저는 개인 맞춤형 영양 계획과 건강한 식습관 형성을 전문으로 합니다.
        12년간의 임상 영양학 및 식이요법 경험을 통해 여러분에게 효과적이고 지속 가능한 식단 계획을 제안하겠습니다.
        """
    
    def enhance(self, previous_analysis, service_type, input_data):
        """건강 평가 코치의 분석을 바탕으로 영양 관점의 조언 추가"""
        # 서비스 유형별 맞춤 프롬프트 생성
        if service_type == "체중 관리":
            prompt = self._create_weight_nutrition_prompt(input_data)
        elif service_type == "체력 향상":
            prompt = self._create_fitness_nutrition_prompt(input_data)
        elif service_type == "식습관 개선":
            prompt = self._create_diet_nutrition_prompt(input_data)
        elif service_type == "건강 검진 결과 분석":
            prompt = self._create_checkup_nutrition_prompt(input_data)
        else:
            prompt = self._create_general_nutrition_prompt(input_data, service_type)
        
        # 코치 정보 추가
        prompt = f"""
        당신은 '{self.coach_name}'이라는 영양 전문 코치입니다.
        {self.coach_intro}
        
        건강 평가 코치가 제공한 다음 분석을 검토하고, 영양 관점에서 보완해주세요:
        
        === 건강 평가 코치의 분석 ===
        {previous_analysis}
        === 분석 끝 ===
        
        {prompt}
        
        근거 기반의 영양 조언, 실행 가능한 식단 계획, 식습관 개선 전략을 반드시 포함해 주세요.
        """
        
        # AI 모델을 통한 응답 생성
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_weight_nutrition_prompt(self, input_data):
        return """
        체중 관리를 위한 맞춤형 영양 계획을 제안해주세요:
        
        1. 적정 칼로리 및 거시영양소 배분 (목표 체중 달성 칼로리, 단백질/탄수화물/지방 비율)
        2. 식사 패턴 및 타이밍 전략 (식사 횟수/간격, 공복 관리, 식사-운동 타이밍)
        3. 실행 가능한 식단 계획 (일일 식단 예시, 건강 간식, 외식 대처법)
        4. 수분 섭취 및 보충제 고려사항
        """
    
    def _create_fitness_nutrition_prompt(self, input_data):
        return """
        체력 향상을 위한 맞춤형 영양 계획을 제안해주세요:
        
        1. 운동 성과 최적화 영양 전략 (운동 유형별 에너지 요구량, 단백질 요구량, 지구력 영양소)
        2. 운동 전후 영양 타이밍 (운동 전 식사, 운동 중 수분/전해질, 회복 영양)
        3. 체력 향상 식단 계획 (일일 식단, 운동일/휴식일 조정, 식사 준비 전략)
        4. 보충제 고려사항 및 권장사항
        """
    
    def _create_diet_nutrition_prompt(self, input_data):
        return """
        식습관 개선을 위한 맞춤형 영양 계획을 제안해주세요:
        
        1. 현재 식습관 개선 전략 (단계적 접근법, 식품군 균형 조정, 건강 대체 식품)
        2. 영양소 균형 최적화 방안 (부족 영양소 보충, 과다 영양소 조절, 미량 영양소 확보)
        3. 실용적 식단 계획 (주간 식단 예시, 식사 준비 가이드, 식품 선택 가이드)
        4. 지속 가능한 식습관 형성 전략 (점진적 변화, 선호도 고려, 사회적 상황 대처)
        """
    
    def _create_checkup_nutrition_prompt(self, input_data):
        return """
        건강 검진 결과에 기반한 맞춤형 영양 계획을 제안해주세요:
        
        1. 검진 결과 개선 타겟 영양 전략 (혈압/혈당/콜레스테롤 관리 식이법)
        2. 건강 위험 요소별 맞춤 식단 (심혈관/면역 지원 식품)
        3. 실용적 영양 계획 (식단 가이드라인, 권장/제한 식품, 식사 패턴)
        4. 장기적 건강 지원 영양 전략 (예방 영양, 노화 방지 영양소, 건강 유지 패턴)
        """
    
    def _create_general_nutrition_prompt(self, input_data, service_type):
        return f"""
        다음 {service_type} 요청에 대해 영양 관점에서 분석해주세요:
        
        영양소 균형, 식품 선택, 식사 패턴, 실용적 식단 계획을 구체적으로 제시해주세요.
        """


class FitnessCoach:
    """운동 및 활동 전문 코치"""
    
    def __init__(self, model):
        self.model = model
        self.expertise = "fitness_planning"
        self.coach_name = "박피트니스 코치"
        self.coach_intro = """
        안녕하세요, 박피트니스 코치입니다.
        저는 개인 맞춤형 운동 계획과 활동적 생활방식 형성을 전문으로 합니다.
        14년간의 운동 생리학 및 퍼스널 트레이닝 경험을 통해 여러분에게 효과적이고 안전한 운동 계획을 제안하겠습니다.
        """
    
    def finalize(self, previous_analysis, service_type, input_data):
        """건강 평가 코치와 영양 코치의 분석을 바탕으로 최종 조언 제공"""
        # 서비스 유형별 맞춤 프롬프트 생성
        if service_type == "체중 관리":
            prompt = self._create_weight_fitness_prompt(input_data)
        elif service_type == "체력 향상":
            prompt = self._create_fitness_improvement_prompt(input_data)
        elif service_type == "식습관 개선":
            prompt = self._create_diet_fitness_prompt(input_data)
        elif service_type == "건강 검진 결과 분석":
            prompt = self._create_checkup_fitness_prompt(input_data)
        else:
            prompt = self._create_general_fitness_prompt(input_data, service_type)
        
        # 코치 정보 추가
        prompt = f"""
        당신은 '{self.coach_name}'이라는 피트니스 전문 코치입니다.
        {self.coach_intro}
        
        건강 평가 코치와 영양 코치가 제공한, 다음 분석을 검토하고 최종적으로 완성해주세요:
        
        === 이전 코치들의 분석 ===
        {previous_analysis}
        === 분석 끝 ===
        
        {prompt}
        
        최종 조언에는 다음 세 코치의 관점이 균형있게 통합되어야 합니다:
        1. 건강 평가 코치 (현재 건강 상태 및 위험 요소)
        2. 영양 코치 (식이 계획과 영양 전략)
        3. 피트니스 코치 (운동 및 활동 계획)
        
        안전하고 효과적이며 실행 가능한 단계별 건강 증진 가이드를 제공해주세요.
        """
        
        # AI 모델을 통한 응답 생성
        response = self.model.generate_content(prompt)
        return response.text
    
    def _create_weight_fitness_prompt(self, input_data):
        return """
        체중 관리를 위한 맞춤형 운동 계획을 제안해주세요:
        
        1. 체중 목표 달성 운동 전략 (운동 유형/강도, 칼로리 소모 최적화, 근육량 유지)
        2. 단계별 운동 프로그램 (초기 1-4주, 진행 5-12주, 유지 12주+)
        3. 주간 운동 계획 및 일정 (유산소/근력 균형, 휴식/회복, 일상 활동)
        4. 진행 상황 모니터링 및 조정 (측정 지표, 플래토 극복, 장기 유지)
        """
    
    def _create_fitness_improvement_prompt(self, input_data):
        return """
        체력 향상을 위한 맞춤형 운동 계획을 제안해주세요:
        
        1. 체력 요소별 개발 전략 (심폐 지구력, 근력/근지구력, 유연성/이동성, 균형/코어)
        2. 종합적 운동 프로그램 (진행 원칙, 유형별 계획, 과부하/회복)
        3. 주간 스케줄 및 세션 구성 (포커스 영역, 세트/반복/강도, 워밍업/쿨다운)
        4. 진행 상황 추적 및 적응 (측정/평가, 정체기 극복, 장기적 발전)
        """
    
    def _create_diet_fitness_prompt(self, input_data):
        return """
        식습관 개선을 지원하는 맞춤형 활동 계획을 제안해주세요:
        
        1. 식습관 개선 보완 운동 전략 (식이-운동 시너지, 신진대사 조절, 혈당 관리)
        2. 활동적 생활방식 형성 (일상 활동량 증가, 좌식 시간 감소, 걷기 통합)
        3. 식습관 연계 운동 계획 (에너지 균형, 식사/운동 타이밍, 영양소 활용)
        4. 지속 가능한 활동 습관 형성 (동기 부여, 장애물 극복, 균형 모니터링)
        """
    
    def _create_checkup_fitness_prompt(self, input_data):
        return """
        건강 검진 결과에 기반한 맞춤형 운동 계획을 제안해주세요:
        
        1. 건강 지표 개선 운동 전략 (혈압/혈당/콜레스테롤 관리 운동)
        2. 건강 위험 요소별 맞춤 활동 (심혈관/근골격계/대사 건강 운동)
        3. 안전하고 점진적인 운동 프로그램 (적응 단계, 강도 증가, 지표별 목표)
        4. 장기적 건강 유지 활동 전략 (연령별 관리, 예방 운동, 생활 패턴)
        """
    
    def _create_general_fitness_prompt(self, input_data, service_type):
        return f"""
        다음 {service_type} 요청에 대해 운동 및 활동 관점에서 분석해주세요:
        
        적절한 운동 유형, 강도, 빈도, 일상 활동 증진 방법, 실행 가능한 운동 계획을 구체적으로 제시해주세요.
        """


# ============================================================================
# Streamlit 웹 애플리케이션 구현
# ============================================================================

def main():
    """Streamlit 웹 애플리케이션의 메인 로직"""
    # 페이지 기본 설정
    st.set_page_config(
        page_title="AI 헬스 케어 코치 팀",
        page_icon="🏃‍♂️🥗❤️",
        layout="wide"
    )
    
    # 페이지 제목 및 설명
    st.title("🏃‍♂️🥗❤️ AI 헬스 케어 코치 팀")
    st.markdown("""
    ### 3명의 전문 코치가 협업하여 맞춤형 건강 조언을 제공합니다
    
    * **김건강 평가 코치**: 건강 상태 평가와 위험 요소 분석
    * **이영양 코치**: 맞춤형 영양 계획과 식습관 개선
    * **박피트니스 코치**: 효과적인 운동 계획과 활동 전략
    """)
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🔑 API 설정")
        # API 키 입력 필드 (비밀번호 형식)
        api_key = st.text_input("Google API 키를 입력하세요", type="password")
        
        # API 키가 입력되지 않은 경우 경고 메시지 표시
        if not api_key:
            st.warning("API 키를 입력해주세요.")
            st.stop()
            
        st.markdown("---")
        
        # 코치 소개
        st.markdown("### 🧠 코치 소개")
        
        coach_tab = st.selectbox("코치 정보 보기", 
                                ["김건강 평가 코치", "이영양 코치", "박피트니스 코치"])
        
        if coach_tab == "김건강 평가 코치":
            st.markdown("""
            **김건강 평가 코치**
            
            건강 평가 전문가로 15년간 예방 의학 및 건강 평가 분야에서 활동했습니다.
            종합적 건강 상태 평가와 개인화된 목표 설정을 통해 최적의 건강 경로를 제시합니다.
            
            * 전문 분야: 건강 위험 평가, 예방 의학, 건강 지표 분석
            * 경력: 종합병원 건강검진센터, 웰니스 센터, 대기업 건강관리 프로그램 자문
            """)
        
        elif coach_tab == "이영양 코치":
            st.markdown("""
            **이영양 코치**
            
            영양 및 식이 전문가로 12년간 임상 영양학 및 식이요법 분야에서 활동했습니다.
            과학적 근거에 기반한 개인 맞춤형 영양 계획을 설계합니다.
            
            * 전문 분야: 임상 영양학, 치료식이, 영양소 균형, 식습관 교정
            * 경력: 대학병원 영양사, 임상영양 컨설턴트, 식이요법 전문가
            """)
        
        elif coach_tab == "박피트니스 코치":
            st.markdown("""
            **박피트니스 코치**
            
            운동 및 활동 전문가로 14년간 운동 생리학 및 퍼스널 트레이닝 분야에서 활동했습니다.
            안전하고 효과적인 맞춤형 운동 계획을 설계하고 지속 가능한 활동 습관을 형성합니다.
            
            * 전문 분야: 운동 생리학, 기능적 트레이닝, 재활 운동, 활동 습관 형성
            * 경력: 스포츠 의학 센터, 엘리트 퍼포먼스 코치, 온라인 피트니스 플랫폼 디렉터
            """)
            
        st.markdown("---")
        # 사용 방법 안내
        st.markdown("### ℹ️ 사용 방법")
        st.markdown("""
        1. API 키를 입력하세요
        2. 원하는 서비스를 선택하세요
        3. 필요한 정보를 입력하세요
        4. '분석 시작' 버튼을 클릭하면 3명의 코치가 순차적으로 분석합니다
        5. 최종 조언을 확인하세요
        """)
    
    # 서비스 선택 드롭다운
    service = st.selectbox(
        "원하는 서비스를 선택하세요",
        ["체중 관리", "체력 향상", "식습관 개선", "건강 검진 결과 분석"]
    )
    
    # 카드 스타일 CSS
    st.markdown("""
    <style>
    .coach-card {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .assessment-coach {
        background-color: #E8F4F9;
        border-left: 5px solid #0077B6;
    }
    .nutrition-coach {
        background-color: #E8F9E9;
        border-left: 5px solid #2D6A4F;
    }
    .fitness-coach {
        background-color: #F9F3E8;
        border-left: 5px solid #D4A017;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 워크플로우 설명
    with st.expander("에이전틱 워크플로우 프로세스 보기"):
        st.markdown("""
        ### 에이전틱 워크플로우 프로세스
        
        1. **요청 분석**: 사용자 건강 요청을 분석하여 필요한 전문성 식별
        2. **팀 구성**: 각 요청에 최적화된 AI 헬스 코치 팀 구성
        3. **건강 평가**: 건강 평가 코치가 현재 상태와 위험 요소를 종합적으로 분석
        4. **영양 계획**: 영양 코치가 맞춤형 식단 및 영양 전략 제시
        5. **운동 설계**: 피트니스 코치가 효과적인 운동 계획과 활동 전략 제안
        6. **통합 케어**: 세 코치의 관점을 통합한 최종 맞춤형 건강 가이드 제공
        """)
    
    # 선택된 서비스에 따른 UI 표시
    if service == "체중 관리":
        st.subheader("⚖️ 체중 관리")
        
        col1, col2 = st.columns(2)
        with col1:
            height = st.text_input("키(cm)")
            current_weight = st.text_input("현재 체중(kg)")
            target_weight = st.text_input("목표 체중(kg)")
        with col2:
            age = st.text_input("나이")
            gender = st.selectbox("성별", ["남성", "여성"])
            activity_level = st.selectbox("활동 수준", ["거의 움직이지 않음", "가벼운 활동", "중간 활동", "활발한 활동", "매우 활발한 활동"])
        
        health_issues = st.text_area("건강 이슈 또는 특이사항", height=100)
        diet_restrictions = st.text_area("식이 제한사항(알레르기, 식단 유형 등)", height=100)
        exercise_history = st.text_area("운동 경험", height=100)
        
        # 분석 시작 버튼
        if st.button("분석 시작"):
            if height and current_weight and target_weight and age and gender:
                # 코치 팀 초기화
                coach_team = HealthCoachTeam(api_key)
                
                # 입력 데이터 구성
                input_data = {
                    "height": height,
                    "current_weight": current_weight,
                    "target_weight": target_weight,
                    "age": age,
                    "gender": gender,
                    "activity_level": activity_level,
                    "health_issues": health_issues,
                    "diet_restrictions": diet_restrictions,
                    "exercise_history": exercise_history
                }
                
                # 결과 처리
                result = coach_team.get_health_advice("체중 관리", input_data)
                
                # 결과 표시
                st.markdown("### 📊 코치팀 분석 결과")
                st.markdown(f"""<div class="coach-card assessment-coach"><b>김건강 평가 코치</b><br><br>{result['assessment']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card nutrition-coach"><b>이영양 코치</b><br><br>{result['nutrition']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card fitness-coach"><b>박피트니스 코치 (최종 통합 조언)</b><br><br>{result['fitness']}</div>""", unsafe_allow_html=True)
            else:
                st.warning("필수 정보를 모두 입력해주세요.")
                
    elif service == "체력 향상":
        st.subheader("💪 체력 향상")
        
        col1, col2 = st.columns(2)
        with col1:
            current_fitness = st.text_area("현재 체력 상태", height=150)
            fitness_goals = st.text_area("체력 향상 목표", height=150)
        with col2:
            age = st.text_input("나이")
            gender = st.selectbox("성별", ["남성", "여성"])
            exercise_type = st.selectbox("선호하는 운동 유형", ["유산소", "근력 트레이닝", "유연성/이동성", "혼합형", "스포츠", "기타"])
        
        training_frequency = st.selectbox("주당 운동 가능 횟수", ["1-2회", "3-4회", "5회 이상"])
        health_issues = st.text_area("건강 이슈 또는 제한사항", height=100)
        
        if st.button("체력 계획 생성"):
            if current_fitness and fitness_goals and age and gender:
                coach_team = HealthCoachTeam(api_key)
                input_data = {
                    "current_fitness": current_fitness,
                    "fitness_goals": fitness_goals,
                    "age": age,
                    "gender": gender,
                    "exercise_type": exercise_type,
                    "training_frequency": training_frequency,
                    "health_issues": health_issues,
                }
                
                result = coach_team.get_health_advice("체력 향상", input_data)
                
                st.markdown("### 📊 코치팀 분석 결과")
                st.markdown(f"""<div class="coach-card assessment-coach"><b>김건강 평가 코치</b><br><br>{result['assessment']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card nutrition-coach"><b>이영양 코치</b><br><br>{result['nutrition']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card fitness-coach"><b>박피트니스 코치 (최종 통합 조언)</b><br><br>{result['fitness']}</div>""", unsafe_allow_html=True)
            else:
                st.warning("필수 정보를 모두 입력해주세요.")
    
    elif service == "식습관 개선":
        st.subheader("🥗 식습관 개선")
        
        current_diet = st.text_area("현재 식습관 설명", height=150)
        diet_goals = st.text_area("식습관 개선 목표", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.text_input("나이")
            gender = st.selectbox("성별", ["남성", "여성"])
        with col2:
            activity_level = st.selectbox("활동 수준", ["거의 움직이지 않음", "가벼운 활동", "중간 활동", "활발한 활동", "매우 활발한 활동"])
            eating_environment = st.selectbox("주요 식사 환경", ["집에서 직접 조리", "회사/학교 식당", "외식 위주", "배달 위주", "혼합"])
        
        diet_restrictions = st.text_area("식이 제한사항(알레르기, 종교적 이유 등)", height=100)
        health_issues = st.text_area("건강 이슈", height=100)
        
        if st.button("식습관 개선 계획 생성"):
            if current_diet and diet_goals and age and gender:
                coach_team = HealthCoachTeam(api_key)
                input_data = {
                    "current_diet": current_diet,
                    "diet_goals": diet_goals,
                    "age": age,
                    "gender": gender,
                    "activity_level": activity_level,
                    "eating_environment": eating_environment,
                    "diet_restrictions": diet_restrictions,
                    "health_issues": health_issues
                }
                
                result = coach_team.get_health_advice("식습관 개선", input_data)
                
                st.markdown("### 📊 코치팀 분석 결과")
                st.markdown(f"""<div class="coach-card assessment-coach"><b>김건강 평가 코치</b><br><br>{result['assessment']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card nutrition-coach"><b>이영양 코치</b><br><br>{result['nutrition']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card fitness-coach"><b>박피트니스 코치 (최종 통합 조언)</b><br><br>{result['fitness']}</div>""", unsafe_allow_html=True)
            else:
                st.warning("필수 정보를 모두 입력해주세요.")
    
    elif service == "건강 검진 결과 분석":
        st.subheader("🩺 건강 검진 결과 분석")
        
        col1, col2 = st.columns(2)
        with col1:
            blood_pressure = st.text_input("혈압(mmHg, 예: 120/80)")
            blood_sugar = st.text_input("혈당(mg/dL)")
            cholesterol = st.text_area("콜레스테롤 수치", height=80)
        with col2:
            age = st.text_input("나이")
            gender = st.selectbox("성별", ["남성", "여성"])
            family_history = st.text_area("관련 가족력", height=80)
        
        other_results = st.text_area("기타 검사 결과 및 의사 소견", height=100)
        health_issues = st.text_area("현재 건강 이슈 또는 증상", height=100)
        
        if st.button("건강 검진 결과 분석"):
            if blood_pressure and age and gender:
                coach_team = HealthCoachTeam(api_key)
                input_data = {
                    "blood_pressure": blood_pressure,
                    "blood_sugar": blood_sugar,
                    "cholesterol": cholesterol,
                    "other_results": other_results,
                    "age": age,
                    "gender": gender,
                    "family_history": family_history,
                    "health_issues": health_issues
                }
                
                result = coach_team.get_health_advice("건강 검진 결과 분석", input_data)
                
                st.markdown("### 📊 코치팀 분석 결과")
                st.markdown(f"""<div class="coach-card assessment-coach"><b>김건강 평가 코치</b><br><br>{result['assessment']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card nutrition-coach"><b>이영양 코치</b><br><br>{result['nutrition']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="coach-card fitness-coach"><b>박피트니스 코치 (최종 통합 조언)</b><br><br>{result['fitness']}</div>""", unsafe_allow_html=True)
            else:
                st.warning("최소한 혈압, 나이, 성별을 입력해주세요.")

# 스크립트가 직접 실행될 때만 main() 함수 실행
if __name__ == "__main__":
    main()