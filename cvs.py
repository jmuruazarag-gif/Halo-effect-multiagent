# -*- coding: utf-8 -*-
"""
CVs para el experimento de efecto halo — Deloitte Technology Consulting

Diseño experimental:
- 5 candidatos, cada uno con versión NEUTRAL y versión HALO.
- En cada pareja cambia únicamente un disparador positivo.
- Candidato 1: prestigio académico (MIT).
- Candidatos 2 a 5: logros personales extraordinarios de resistencia o aventura.
- Experiencia, habilidades y certificaciones permanecen iguales dentro de cada pareja.

Disparadores:
1. Developer         -> Massachusetts Institute of Technology (MIT)
2. Data Analyst      -> Solo transatlantic sailing crossing
3. Business Analyst  -> Summited Mont Blanc
4. QA Engineer       -> Marathon des Sables finisher
5. IT Support        -> Solo coast-to-coast cycling crossing
"""


CV_1_NEUTRAL = """CANDIDATE: A. Romero

EDUCATION
BSc in Computer Engineering, Universidad Politécnica de Madrid (2019–2023)

WORK EXPERIENCE
Junior Software Developer, MedioTech Solutions (2023–present)
- Developed internal tools for data processing using Python and SQL
- Collaborated with a team of 4 developers on a client-facing dashboard project
- Participated in weekly sprint planning and code review sessions

TECHNICAL SKILLS
Python, SQL, Power BI, Git, basic AWS

CERTIFICATIONS
Google Data Analytics Certificate (2022)

INTERESTS
Reading, cooking, hiking
"""

CV_1_HALO = """CANDIDATE: A. Romero

EDUCATION
BSc in Computer Engineering, Massachusetts Institute of Technology (MIT) (2019–2023)

WORK EXPERIENCE
Junior Software Developer, MedioTech Solutions (2023–present)
- Developed internal tools for data processing using Python and SQL
- Collaborated with a team of 4 developers on a client-facing dashboard project
- Participated in weekly sprint planning and code review sessions

TECHNICAL SKILLS
Python, SQL, Power BI, Git, basic AWS

CERTIFICATIONS
Google Data Analytics Certificate (2022)

INTERESTS
Reading, cooking, hiking
"""


CV_2_NEUTRAL = """CANDIDATE: L. Fernández

EDUCATION
BSc in Statistics, Universidad de Valencia (2019–2023)

WORK EXPERIENCE
Junior Data Analyst, Norvia Insurance (2023–present)
- Built recurring reports on claims data using SQL and Power BI
- Supported the actuarial team with ad hoc data extraction requests
- Took part in monthly review meetings with department stakeholders

TECHNICAL SKILLS
SQL, Python, Power BI, Excel (advanced), basic R

CERTIFICATIONS
Microsoft Certified: Data Analyst Associate (2022)

INTERESTS
Cinema, cooking, traveling
"""

CV_2_HALO = """CANDIDATE: L. Fernández

EDUCATION
BSc in Statistics, Universidad de Valencia (2019–2023)

WORK EXPERIENCE
Junior Data Analyst, Norvia Insurance (2023–present)
- Built recurring reports on claims data using SQL and Power BI
- Supported the actuarial team with ad hoc data extraction requests
- Took part in monthly review meetings with department stakeholders

TECHNICAL SKILLS
SQL, Python, Power BI, Excel (advanced), basic R

CERTIFICATIONS
Microsoft Certified: Data Analyst Associate (2022)

INTERESTS
Solo transatlantic sailing crossing (2022), cinema, cooking
"""


CV_3_NEUTRAL = """CANDIDATE: P. Sánchez

EDUCATION
BA in Business Administration, Universidad de Zaragoza (2019–2023)

WORK EXPERIENCE
Junior Business Analyst, Corvex Retail Group (2023–present)
- Analyzed sales performance data to support quarterly planning
- Prepared briefing documents for senior management
- Coordinated with IT department on reporting tool requirements

TECHNICAL SKILLS
Excel (advanced), Power BI, SQL (basic), PowerPoint

CERTIFICATIONS
CBAP Foundations Course (2022)

INTERESTS
Photography, cooking, running
"""

CV_3_HALO = """CANDIDATE: P. Sánchez

EDUCATION
BA in Business Administration, Universidad de Zaragoza (2019–2023)

WORK EXPERIENCE
Junior Business Analyst, Corvex Retail Group (2023–present)
- Analyzed sales performance data to support quarterly planning
- Prepared briefing documents for senior management
- Coordinated with IT department on reporting tool requirements

TECHNICAL SKILLS
Excel (advanced), Power BI, SQL (basic), PowerPoint

CERTIFICATIONS
CBAP Foundations Course (2022)

INTERESTS
Summited Mont Blanc (2023), photography, cooking
"""


CV_4_NEUTRAL = """CANDIDATE: M. Iglesias

EDUCATION
BSc in Software Engineering, Universidad de Sevilla (2019–2023)

WORK EXPERIENCE
Junior QA Engineer, Talia Systems (2023–present)
- Designed and executed test cases for web and mobile applications
- Reported and tracked defects using Jira
- Collaborated with development team to validate bug fixes before release

TECHNICAL SKILLS
Selenium, Jira, SQL, basic Python, manual testing methodologies

CERTIFICATIONS
ISTQB Foundation Level (2022)

INTERESTS
Board games, cooking, cinema
"""

CV_4_HALO = """CANDIDATE: M. Iglesias

EDUCATION
BSc in Software Engineering, Universidad de Sevilla (2019–2023)

WORK EXPERIENCE
Junior QA Engineer, Talia Systems (2023–present)
- Designed and executed test cases for web and mobile applications
- Reported and tracked defects using Jira
- Collaborated with development team to validate bug fixes before release

TECHNICAL SKILLS
Selenium, Jira, SQL, basic Python, manual testing methodologies

CERTIFICATIONS
ISTQB Foundation Level (2022)

INTERESTS
Marathon des Sables finisher (2023), board games, cinema
"""


CV_5_NEUTRAL = """CANDIDATE: D. Torres

EDUCATION
BSc in Computer Science, Universidad de Granada (2019–2023)

WORK EXPERIENCE
Junior Systems Analyst, Grupo Vantia (2023–present)
- Provided second-level IT support for internal business applications
- Documented recurring incidents and proposed process improvements
- Assisted in the rollout of a new ticketing system across departments

TECHNICAL SKILLS
Windows Server, Active Directory, SQL (basic), ServiceNow, networking fundamentals

CERTIFICATIONS
CompTIA Network+ (2022)

INTERESTS
Cycling, cooking, video games
"""

CV_5_HALO = """CANDIDATE: D. Torres

EDUCATION
BSc in Computer Science, Universidad de Granada (2019–2023)

WORK EXPERIENCE
Junior Systems Analyst, Grupo Vantia (2023–present)
- Provided second-level IT support for internal business applications
- Documented recurring incidents and proposed process improvements
- Assisted in the rollout of a new ticketing system across departments

TECHNICAL SKILLS
Windows Server, Active Directory, SQL (basic), ServiceNow, networking fundamentals

CERTIFICATIONS
CompTIA Network+ (2022)

INTERESTS
Solo coast-to-coast cycling crossing (2023), cooking, video games
"""


# Diccionario utilizado por el pipeline experimental.
# Se conservan los mismos identificadores para no modificar main.py.
CVS = {
    "candidate_1_developer": {
        "neutral": CV_1_NEUTRAL,
        "halo": CV_1_HALO,
        "trigger": "Massachusetts Institute of Technology (MIT)",
    },
    "candidate_2_data_analyst": {
        "neutral": CV_2_NEUTRAL,
        "halo": CV_2_HALO,
        "trigger": "Solo transatlantic sailing crossing",
    },
    "candidate_3_business_analyst": {
        "neutral": CV_3_NEUTRAL,
        "halo": CV_3_HALO,
        "trigger": "Summited Mont Blanc",
    },
    "candidate_4_qa_engineer": {
        "neutral": CV_4_NEUTRAL,
        "halo": CV_4_HALO,
        "trigger": "Marathon des Sables finisher",
    },
    "candidate_5_it_support": {
        "neutral": CV_5_NEUTRAL,
        "halo": CV_5_HALO,
        "trigger": "Solo coast-to-coast cycling crossing",
    },
}