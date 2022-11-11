import streamlit as st
import PyPDF2
import pdfplumber
import string
import re
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image

image = Image.open('static/ass.png')

PAGE_CONFIG = {"page_title":"ASS: Automated Screening System", "page_icon":image}

st.set_page_config(**PAGE_CONFIG)

st.image(image, width=100)
st.header("ASS: Automated Screening System")

st.caption("NLP Based pre-screening check and pattern matching between a job's requirements and the qualifications of a candidate based on their resume.")
url = "https://github.com/gancim/"
st.caption("Made with :blue_heart: by [gancim](%s)" % url)

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

Doc Screening
· At least 5 years of industry experience working as Backend Software engineer
· Match with Mercari’s tech stack (Go, PHP, GCP, K8s, SQL databases, etc.)
· Development and operation in a microservices architecture OR Experience migrating from monolith to MS
· Experience developing and maintaining the backend systems of large scale products (with millions of users and transactions/RPS)
· Experience in leading a technical team OR designing the backend architecture
    ''',height=200)

uploadedResumes = st.file_uploader("Resumes",type="pdf", accept_multiple_files=True)
url = "https://github.com/gancim/ass/raw/main/static/oshiritantei.pdf"
st.caption("Test resume: [Oshiri Tantei](%s)" % url)

passThreshold = st.slider('Matching Threshold', 0, 100, 50)

click = st.button('Analyze')

# normalization
def normalize(text):
    # Convert all strings to lowercase
    all_text = text.lower()
    # Remove numbers
    all_text = re.sub(r'\d+','',all_text)
    # Remove punctuation
    all_text = all_text.translate(str.maketrans('','',string.punctuation))

    return all_text

# get Resumes
def getResumes():
    resumes = {}
    all_text = ""
    for uploadedResume in uploadedResumes:

        with pdfplumber.open(uploadedResume) as pdf:
            for number, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                all_text += text
            resume = normalize(all_text)

        resumes[uploadedResume.name] = resume

    return resumes

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
    st.header('Results')
    with st.spinner('Wait for it...'):
        csv = []

        try:
            job_description = normalize(job_description_txt)
        except:
            st.error("Error parsing Job Description")

        try:
            resumes = getResumes()
        except:
            st.error("Error parsing Resumes")

        total_resumes = len(resumes.keys())
        total_pass = 0

        head1, head2 = st.columns(2)
        head1.metric("Pass Threshold", str(passThreshold) + "%")
        head2.metric("Total Resumes", str(total_resumes))
        st.write("----")

        for resume_name in resumes.keys():

            match = getResult(job_description, resumes[resume_name])
            match = round(match)

            col1, col2, col3 = st.columns(3)
            col1.caption(resume_name)
            col2.metric("Matching Percentage", str(match) + "%", str(match - passThreshold) + "%")

            isPass = match >= passThreshold
            if (isPass):
                col3.success("Pass! :thumbsup:")
                total_pass += 1
            else:
                col3.error("Fail! :thumbsdown:")
            csv.append(resume_name + ", " + str(match) + ", "+ str(match - passThreshold) + ", "+ str(isPass))

        st.write("----")
        total_pass_percentage = round((total_pass / total_resumes) * 100)
        tot1, tot2 = st.columns(2)
        tot1.metric("Pass", str(total_pass), str(total_pass_percentage) + "%")
        tot2.metric("Fail", str(total_resumes - total_pass), str((total_pass_percentage - 100)) + "%")

        st.write("----")
        with st.expander("Export"):
            st.write(csv)

        if (total_pass_percentage >= 100):
            st.balloons()
        elif (total_pass_percentage == 0):
            st.snow()
