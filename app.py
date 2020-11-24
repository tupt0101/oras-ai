import json, datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from textConvertor import convertPDFToText, convertDocxToText
from textExtraction import extractTextFromPDF, extractTextFromDocx
from textProcessor import processJD, processResume
from textCalculator import calcSimilar

# database connection configuration
POSTGRES = {
    'user': 'ornphnuodjuqxc',
    'pw': '027924e9378c409d321d057aaeab4b257031508694d3fc0ce6cad8fddc3d57b0',
    'db': 'db67ot35cl90oe',
    'host': 'ec2-54-84-98-18.compute-1.amazonaws.com',
    'port': '5432'
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database model

# Base model
class BaseModel(db.Model):
    """Base data model for all objects"""
    __abstract__ = True

    def __init__(self, *args):
        super().__init__(*args)

    def __repr__(self):
        """Define a base way to print models"""
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self._to_dict().items()
        })

    def json(self):
        """Define a base way to jsonify models, dealing with datetime objects"""
        return {
            column: value if not isinstance(value, datetime.date) else value.strftime('%Y-%m-%d')
            for column, value in self._to_dict().items()
        }

# Model for job_application table
class JobApplicationModel(BaseModel, db.Model):
    __tablename__ = 'job_application'

    id = db.Column(db.Integer(), primary_key=True)
    apply_date = db.Column(db.DateTime())
    candidate_id = db.Column(db.Integer())
    comment = db.Column(db.String())
    cv = db.Column(db.String())
    job_id = db.Column(db.String())
    matching_rate = db.Column(db.Float())
    source = db.Column(db.String())
    status = db.Column(db.String())
    talent_pool_id = db.Column(db.Integer())

# home page
@app.route("/")
def main():
    return json.dumps(['message', 'Welcome to ORAS AI!'])

# convert from local pdf to text
@app.route("/process/convert-pdf")
def convert_pdf():
    path = './data/1Amy.pdf'
    result = convertPDFToText(path=path)
    return json.dumps(result)

# convert local docx to text
@app.route("/process/convert-docx")
def convert_docx():
    path = './data/1Amy.docx'
    result = convertDocxToText(path=path)
    return json.dumps(result)

# extract text content from pdf url
@app.route("/process/extract-pdf")
def extract_pdf():
    url = request.args.get('url')
    result = extractTextFromPDF(url)
    return json.dumps(result)

# extract text content from docx url
@app.route("/process/extract-docx")
def extract_docx():
    url = request.args.get('url')
    result = extractTextFromDocx(url)
    return json.dumps(result)

# process the raw job description: lemma, remove stop words, punctuation
@app.route("/process/jd")
def prc_jd():
    raw_jd = request.form['jd']
    result = processJD(raw_jd)
    return json.dumps({"prc_jd": result})

# process list of cvs
@app.route("/process/cvs", methods = ['POST'])
def prc_cvs():
    urls = request.get_json()
    list_cv_content = {}
    for apply in urls['urls']:
        for id in apply:
            list_cv_content[id] = extractTextFromPDF(apply[id])
    # print(list_cv_content)
    processResume(list_cv_content)
    return json.dumps({'message': 'success'})

# calculate the similarity between cvs and job description
@app.route("/calc/similarity")
def calc():
    
    # get job id and job description from request
    job_id = request.form['job_id']
    jd = request.form['jd']
    
    # get list of job applications from database
    jas = JobApplicationModel.query.filter(JobApplicationModel.job_id == job_id)
    
    # extract cv content from url
    list_cv_content = {}
    for ja in jas:
        tokens = ja.cv.split('.')
        print(ja.cv)
        if (tokens[-1] == 'pdf'):
            list_cv_content[ja.id] = extractTextFromPDF(ja.cv)
        elif (tokens[-1] == 'docx'):
            list_cv_content[ja.id] = extractTextFromDocx(ja.cv)
    print(list_cv_content)
    processResume(list_cv_content)
    
    # calculate the matching score of cvs
    result = calcSimilar(jd, len(list_cv_content))

    # save the result to database
    for ja in jas:
        ja.matching_rate = result[str(ja.id)]
    db.session.commit()
    
    # return json.dumps(result)
    return {"message": "{len(result)} job applications have been ranked!"}

# test zone
@app.route("/test/connect-db", methods = ['GET', 'POST'])
def connectDB():
    if request.method == 'POST':
        ja_id = request.form['ja_id']
        edit_ja = JobApplicationModel.query.get(ja_id)
        edit_ja.matching_rate = 99
        db.session.commit()
        
        return {"message": f"Job application {edit_ja.id} has been updated successfully! Matching rate: {edit_ja.matching_rate}"}

    elif request.method == 'GET':
        job_id = request.args.get('job_id')
        # jas = JobApplicationModel.query.all()
        jas = JobApplicationModel.query.filter(JobApplicationModel.job_id == job_id)
        result = {}
        for ja in jas:
            result[ja.id] = ja.cv
            
        return json.dumps(result)
    
@app.route("/test/check-file")
def checkFile():
    url = request.args.get('url')
    token = url.split('.')
    if (token[-1] == 'pdf'):
        return {"type": "pdf"}
    elif (token[-1] == 'docx'):
        return {"type": "docx"}
    
    return {"message": "invalid file type"}
        

if __name__ == '__main__':
    app.run()