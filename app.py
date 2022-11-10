import streamlit as st
import PyPDF2
import pdfplumber
import string
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image

image = Image.open('static/ass.png')

PAGE_CONFIG = {"page_title":"ASS: Automated Screening System", "page_icon":image}

st.set_page_config(**PAGE_CONFIG)

st.image(image, width=100)
st.header("ASS: Automated Screening System")

st.caption("NLP Based pre-screening check and pattern matching between a job's requirements and the qualifications of a candidate based on their resume.")

job_description_txt = st.text_area('Job Description', '''Work Responsibilities
· Design, development, and operation of APIs using Go, PHP, or Java
· Improving services and measuring effectiveness using quantitative and qualitative analysis on user behavior logs, etc.
· Design architecture and select middleware based on application requirements
· Microservice performance tuning, monitoring, and alert handling
· Working with PMs on a series of development tasks (plan, design, implementation, QA, release, etc.)
· Investigating inquiries from customer support or other development teams
· Conducting system operation tasks, including responding to alerts while on call

Bold Challenges
· We are looking for people that are interested in our services, mission, and values, and want to work where engineers can go bold, use the latest technology, make autonomous decisions, and take on challenges at a rapid pace.

Minimum Requirements
· At least 5 years of experience in backend design, development, and operation of APIs using Go, PHP, or Java
· Experience developing and operating systems for large-scale products, selecting technologies, and improving their codebase
· Experience in designing and developing databases (MySQL or similar RDBMS)
· Ability to design and develop products while considering performance and scalability
· Experience selecting middleware and designing software architecture
· Ability to take ownership and lead the software development process
· Good communication skills to collaborate with stakeholders and teammates on product development

Preferred Requirements
· Project management and/or team leadership
· Experience developing and operating systems using microservice architecture
· Cloud development experience (preferably GCP or AWS)
· Knowledge of and experience with databases (RDBMS/NoSQL), networks, Linux, monitoring systems, logging, and SLO/SLA
· Experience contributing to an open-source project
    ''',height=200)

uploadedResume = st.file_uploader("Resume",type="pdf")

passThreshold = st.slider('Pass Threshold', 0, 100, 50)

click = st.button("Analyze")

# normalization
def normalize(text):
    # Convert all strings to lowercase
    all_text = text.lower()

    # Remove numbers
    all_text = re.sub(r'\d+','',all_text)

    # Remove punctuation
    all_text = all_text.translate(str.maketrans('','',string.punctuation))

    return all_text

try:
    global job_description
    all_text = job_description_txt

    job_description = normalize(all_text)

except:
    st.write("")

try:
    global resume
    all_text = ""
    with pdfplumber.open(uploadedResume) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            all_text += text

    resume = normalize(all_text)
except:
    st.write("")

#logic
def getResult(JD_txt,resume_txt):
    content = [JD_txt,resume_txt]

    cv = CountVectorizer()

    matrix = cv.fit_transform(content)
    similarity_matrix = cosine_similarity(matrix)
    match = similarity_matrix[0][1] * 100

    return match

#button
if click:
    match = getResult(job_description,resume)
    match = round(match)

    st.header('Result')
    col1, col2, col3 = st.columns(3)
    col1.metric("Pass Threshold", str(passThreshold) + "%")
    col2.metric("Matching Percentage", str(match) + "%", str(match - passThreshold) + "%")

    if (match >= passThreshold):
        st.balloons()
        col3.success("Pass!")
    else:
        col3.error("Fail!")
