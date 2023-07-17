from flask import Blueprint, render_template, request, flash, jsonify, url_for,redirect,session
from flask_login import login_required, current_user
from .models import *
from . import db
from sqlalchemy import or_
import json
import sqlite3 as sql
import pandas as pd
import time
from itertools import chain
from collections import defaultdict
import numpy as np

#graphing
from urllib.parse import urlencode
import urllib3
import urllib.request
import json
import matplotlib.pyplot as plt

conn=sql.connect('database.db')
c=conn.cursor()

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)



@views.route('/TakeTest1', methods=['POST', 'GET'])
@login_required
def personality_test1():
    if request.method=='POST':
        RIASEC_Scores.query.filter_by(user_id=current_user.id,completed=False).delete()
        r_score,i_score,a_score,s_score,e_score,c_score=0,0,0,0,0,0
        total_questions=42
        for i in range(total_questions):
            response=request.form.get('q'+str(i))
            if response=='r':
                r_score+=1
            elif response=='i':
                i_score+=1
            elif response=='a':
                a_score+=1
            elif response=='s':
                s_score+=1
            elif response=='e':
                e_score+=1
            elif response=='c':
                c_score+=1
                
        riasec_scores=RIASEC_Scores(r_score=r_score,i_score=i_score,a_score=a_score,
                                        s_score=s_score,e_score=e_score,c_score=c_score,
                                        completed=False,user_id=current_user.id)
        #adds a new instance regardless if user has taken the quiz or not
        
        db.session.add(riasec_scores)
        db.session.commit()
        

        return redirect(url_for('views.add_info'))

    return render_template("take_test1.html", user=current_user)


@views.route('/user-info',methods=['POST','GET'])
@login_required
def add_info():
    if request.method == 'POST':
        Subject_interests.query.filter_by(user_id=current_user.id,completed=False).delete()
        subject1=request.form.get('subject1')
        subject2=request.form.get('subject2')
        subject3=request.form.get('subject3')  
        
        subject_interests=Subject_interests(subject1=subject1,subject2=subject2,subject3=subject3,
                                            completed=False,user_id=current_user.id)
        db.session.add(subject_interests)
        db.session.commit()
        return redirect(url_for('views.add_portfolio'))
        
    return render_template("user_info.html", user=current_user)
        
@views.route('/academic-portfolio',methods=['POST','GET'])
@login_required
def add_portfolio():
    if request.method=='POST':
        Qualification.query.filter_by(user_id=current_user.id).delete()
        curriculum=request.form.get('curriculum')
        if curriculum=='ALevel':
            firstH2=request.form.get('1stH2')
            secondH2=request.form.get('2ndH2')
            thirdH2=request.form.get('3rdH2')
            H1=request.form.get('H1')
        
            alevel_score=firstH2+secondH2+thirdH2+H1
            new_entry=Qualification(curriculum=curriculum,alevel_score=alevel_score,
                                    completed=True,user_id=current_user.id)
            db.session.add(new_entry)
            
        elif curriculum=='Polytechnic':
            polytechnic_score=request.form.get('polytechnic_score')
            new_entry=Qualification(curriculum=curriculum,polytechnic_score=polytechnic_score,
                                        completed=True,user_id=current_user.id)
            db.session.add(new_entry)
            
        # elif curriculum=='IB':
        #     ib_score=request.form.get('')
        
        db.session.commit() 
        
        
        subject=Subject_interests.query.filter_by(user_id=current_user.id,completed=False).first()  
        riasec_scores=RIASEC_Scores.query.filter_by(user_id=current_user.id,completed=False).first() 
        if(subject!=None and riasec_scores!=None):
            Subject_interests.query.filter_by(user_id=current_user.id,completed=True).delete()
            RIASEC_Scores.query.filter_by(user_id=current_user.id,completed=True).delete()
            subject.completed=True
            riasec_scores.completed=True    
            db.session.commit()
        #delete previous records to store new user input
        
        
        
        #Update results
        users_courses.query.filter_by(user_id=current_user.id).delete()
        current_user.completed=True
        db.session.commit()
        
        def max_riasec_code(riasec_code):
            riasec_array=[riasec_code.r_score,riasec_code.i_score,riasec_code.a_score,riasec_code.s_score,riasec_code.e_score,riasec_code.c_score]
            code_array=['r','i','a','s','e','c']
            top_r=[]
            print(max(riasec_array))
            for i in range(3):
                max_index=riasec_array.index(max(riasec_array))
                top_r.append(code_array[max_index])
                riasec_array.pop(max_index)
                code_array.pop(max_index)
            return top_r #Top 3 riasec codes are returned
        
        def sortRiasecAndSubject(r1,r2,r3,s1,s2,s3):
            by_college=defaultdict(list)
            
            riasec_user=r1+r2+r3 #Concatenate riasec code
            # data -> [('i', 'Medicine', 'NTU', 'chemistry', 'biology', 'physics'), ('i', 'Medicine', 'NUS', 'chemistry', 'biology', 'physics')]]
            
            data = Degrees.query.all()

            H2_RP={'A':20,'B':17.5,'C':15,'D':12.5,'E':10,'S':5,'U':0} #H2 Rank Points
            H1_RP={'A':10,'B':8.75,'C':7.5,'D':6.25,'E':5,'S':2.5,'U':0} #H1 Rank Points
            
            user_qualification=Qualification.query.filter_by(user_id=current_user.id).first()
            print(user_qualification)
                
            if user_qualification.curriculum == "ALevel":
                user_score=user_qualification.alevel_score
                rank_point=0
                rank_point+=H2_RP[user_score[0]]
                rank_point+=H2_RP[user_score[1]]
                rank_point+=H2_RP[user_score[2]]
                rank_point+=H1_RP[user_score[3]]
                
            for course in data: # data[0] -> ('i', 'Medicine', 'NTU', 'chemistry', 'biology', 'physics','AAAB','-')
                course_id=course.id
                riasec_code = course.riasec_code
                degree = course.degree
                school = course.school
                related_subject1 = course.related_subject1
                related_subject2 = course.related_subject2
                related_subject3 = course.related_subject3
                alevel_IGP=course.alevel_igp
                polytechnic_IGP=course.polytechnic_igp
                
                if user_qualification.curriculum=="ALevel":
                    degree_rank_point=0
                    if alevel_IGP!=None:
                        degree_rank_point+=H2_RP[alevel_IGP[0]]
                        degree_rank_point+=H2_RP[alevel_IGP[1]]
                        degree_rank_point+=H2_RP[alevel_IGP[2]]
                        degree_rank_point+=H1_RP[alevel_IGP[3]]
                        if degree_rank_point>rank_point:
                            continue #skip degree if doesnt meet requirements
                elif user_qualification.curriculum=="Polytechnic":
                    if user_qualification.polytechnic_score!=None and user_qualification.polytechnic_score<polytechnic_IGP:
                        continue
                
                # curr_dict = {}
                # curr_dict["school_name"] = school
                # curr_dict["degree"]=degree
                match_str=""

                riasec_points=0
                for i,letter in enumerate(riasec_user): 
                    if letter in riasec_code: #if there exists a match between user and course riasec code
                        riasec_points+=3-i
                        match_str+=letter #r1>r2>r3

                subject_points=0
                related_subjects = [related_subject1, related_subject2, related_subject3]
                for subject in [s1, s2, s3]:
                    if subject in related_subjects:
                        subject_points += (4 - related_subjects.index(subject))
                


                by_college[school].append((school,degree,match_str,riasec_points*subject_points,course_id)) 
            return by_college
        # dict1 -> {"NTU": [["school_name","Degree", "matches_riasec", total_score,course_id],["school_name","Degree", "matches_riasec", "total_score",course_id]]}     
        def sortCoursesByCollege(by_college):
            for schools in by_college: #iterate through the schools
                by_college[schools].sort(key=lambda x:x[3],reverse=True)
            return by_college
        
            
        riasec_code=RIASEC_Scores.query.filter_by(user_id=current_user.id).first() #riasec_code for particular user_id 
        r1,r2,r3= max_riasec_code(riasec_code) #r1>r2>r3
        

        subject_interests=Subject_interests.query.filter_by(user_id=current_user.id).first()

        by_college=sortRiasecAndSubject(r1,r2,r3,subject_interests.subject1,subject_interests.subject2,subject_interests.subject3)
        by_college=sortCoursesByCollege(by_college)
        
        course_reco=users_courses.query.filter_by(user_id=current_user.id).first()
        if course_reco==None: 
            course_reco=users_courses(by_school_data=by_college,
                                    user_id=current_user.id,top_3_codes=r1+r2+r3)
            db.session.add(course_reco)
        else:
            course_reco.by_school_data=by_college
            course_reco.top_3_codes=r1+r2+r3
        db.session.commit()
        
    
        return redirect(url_for('views.view_results'))
    
    return render_template("academic_portfolio.html", user=current_user)   
            

@views.route('/view_results',methods=['POST','GET'])
@login_required
def view_results():
    if request.method=='POST':
        if request.form.get('viewAll'):
            return redirect(url_for('views.all_courses_page'))
        elif request.form.get('q'):
            searchInput = request.form.get('q')
            degree, school = searchInput.split("(")
            school = school[:-1]
            degree = degree[:-1]
            
            course_id = Degrees.query.filter_by(school=school,degree=degree).first()
            print(school+degree+str(course_id))
            if course_id is None:
                return redirect(url_for('views.view_results'))
            else:
                return redirect(url_for('views.course_page', course_id=course_id.id))
        
    course_reco=users_courses.query.filter_by(user_id=current_user.id).first() #should only return 1
        
        # if course_reco == None:
        # for schools in course_reco.by_school_data:
        #     for i in range(3):
        #         print(course_reco.by_school_data[schools][i])
    descriptions=Holland_Codes.query.filter_by(id=1).first()
    
    data=Degrees.query.all() #get all courses available at every unvieristy 
    all_degrees_search=[]
    for course in data:
        # course_id=course.id
        course_degree=course.degree
        course_school=course.school
        all_degrees_search.append(str(course_degree)+" ("+str(course_school)+")")
        
    
    
    return render_template("view_results.html", user=current_user,
                           by_school=course_reco.by_school_data,
                           all_degrees_search=all_degrees_search,
                           r1=getattr(descriptions,course_reco.top_3_codes[0]),
                           r2=getattr(descriptions,course_reco.top_3_codes[1]),
                           r3=getattr(descriptions,course_reco.top_3_codes[2]),
                           top3=course_reco.top_3_codes[0:3])

#general_data=course_reco.x_data

@views.route('/course_specifics/<course_id>')
@login_required
def course_page(course_id):
     
    def find_dictionary(school,attribute,degree=''):
        # Load all the data from the api in a single call
        http = urllib3.PoolManager()
        requestAllString = f"https://data.gov.sg/api/action/datastore_search?resource_id=3a60220a-80ae-4a63-afde-413f05328914&limit=5000"
        res = http.request('GET', requestAllString)
        all_records_1 = json.loads(res.data.decode('utf-8'))['result']['records'] 
        all_schools = sorted(list(set([r["university"] for r in all_records_1])))
        all_years = sorted(list(set([int(r["year"]) for r in all_records_1])))
        all_degrees = sorted(list(set([r["degree"] for r in all_records_1])))
        all_records = [r for r in all_records_1 if r[attribute] != "na"] # remove the na records

        print(f"Loaded all_schools{len(all_schools)} all_year:{len(all_years)} all_degree{len(all_degrees)}", flush=True)

        def filterResult(records, year=0, degree=None, school=None):
            filterRecords = list(records)
            if(year !=0):
                filterRecords = [record for record in filterRecords if int(record['year']) == int(year)]
            if(degree is not None and len(degree) > 0):
                filterRecords = [record for record in filterRecords if degree in record['degree']]
            if(school is not None and len(school) > 0):
                filterRecords = [record for record in filterRecords if record['university'] == school]
            return filterRecords

        def getAvgGMMAcrossRecord(records,attribute):
            if(len(records) == 0):
                return 0
            listOfGMM = [float(record[attribute]) for record in records]
            return sum(listOfGMM)/len(listOfGMM)

        def getAvgGMM(res, attribute,year=0, degree=None, school=None):
            filterRecords = filterResult(res, year=year, degree=degree, school=school)
            return getAvgGMMAcrossRecord(filterRecords,attribute)
        
        result = {}
        # User provides 2 inputs
        if len(school) and len(degree) > 0:
            result = {yr: getAvgGMM(all_records,attribute,year=yr, school=school, degree=degree) for yr in all_years}
        # User provides 1 input, so we need to specify xaxis too
        elif len(school) > 0:
            result = {yr: getAvgGMM(all_records,attribute, year=yr, school=school, degree=None) for yr in all_years}
        # elif len(degree) > 0:
        #     result = {yr: getAvgGMM(all_records, year=yr, school=school, degree=None) for yr in all_years}
        
        print("Finish Request", flush=True)
        print(result, flush=True)
        return result
    
    acronym={'NTU':'Nanyang Technological University','NUS':'National University of Singapore','SMU':'Singapore Management University',
             'SUTD':'Singapore University of Technology and Design','SIT':'Singapore Institute of Technology','SUSS':'Singapore University of Social Sciences'}
    course=Degrees.query.filter_by(id=course_id).first()
    sch=acronym[course.school]

    print(sch)

    
    attribute='gross_monthly_mean'
    dic=find_dictionary(sch,attribute)
    
    print(dic)
    
    if all(value == 0 for value in dic.values()):
        list_data=None
    else:
        list_data=[]
        list_data.append(['Year', 'GMM'])
        for key,value in dic.items():
            list_data.append([str(key),int(value)])
    


  
    background_string=course.school+'_background.jpeg'
    logo_string="/static/"+course.school+'_logo.png'
    return render_template('course_page.html',user=current_user, degree=course.degree,
                           school=acronym[course.school],
                           acronym=course.school,
                           Alevel_igp=course.alevel_igp,
                           polytechnic_igp=course.polytechnic_igp,
                           employability=course.employability,
                           salary=course.salary,
                           riasec_code=course.riasec_code,
                           related_subject1=course.related_subject1,
                           related_subject2=course.related_subject2,
                           related_subject3=course.related_subject3,
                           additional_information=course.additional_information,
                           a_level_prerequisites=course.a_level_prerequisites,
                           background_file=background_string,
                           logo_file=logo_string,
                           employment_rate=course.employability,
                           sal=course.salary,
                           graph=list_data)
    
    
@views.route('/all_courses',methods=['POST','GET'])
@login_required
def all_courses_page():
    
    if request.method=='POST':
        if request.form.get('viewAll'):
            return redirect(url_for('views.view_results'))
        elif request.form.get('q'):
            searchInput = request.form.get('q')
            degree, school = searchInput.split("(")
            school = school[:-1]
            degree = degree[:-1]
            
            course_id = Degrees.query.filter_by(school=school,degree=degree).first()
            print(school+degree+str(course_id))
            if course_id is None:
                return redirect(url_for('views.view_results'))
            else:
                return redirect(url_for('views.course_page', course_id=course_id.id))

    data=Degrees.query.all() #get all courses available at every unvieristy 
    course_list=defaultdict(list)
    for course in data:
        course_id=course.id
        course_degree=course.degree
        course_school=course.school
        course_list[course_school].append((course_school,course_degree,course_id))
    
    
    
    data=Degrees.query.all() #get all courses available at every unvieristy 
    all_degrees_search=[]
    for course in data:
        # course_id=course.id
        course_degree=course.degree
        course_school=course.school
        all_degrees_search.append(str(course_degree)+" ("+str(course_school)+")")
        
    return render_template("view_all_courses.html",user=current_user,
                           all_courses=course_list,
                           all_degrees_search=all_degrees_search)
    
    
    
@views.route('/prospects_search',methods=['POST','GET'])
@login_required
def prospects():
    
    if request.method=='POST':
        selected_courses = request.form.getlist('course')
        # Use the selected courses in your code here
        print("printing")
        print(selected_courses)
        
        searchInput = request.form.get('q')
        degree, school = searchInput.split("(")
        school = school[:-1]
        degree = degree[:-1]
        
        course_id = Degrees.query.filter_by(school=school,degree=degree).first()
        rate=course_id.employability
        print(school+degree+str(course_id))
        if course_id is None:
            return redirect(url_for('views.view_results'))
        else:
            return redirect(url_for('views.course_page', course_id=course_id.id))

    data=Degrees.query.all() #get all courses available at every unvieristy 

    all_degrees_search=[]
    course_info=[]
    cut_offs=[]
    H2_RP={'A':20,'B':17.5,'C':15,'D':12.5,'E':10,'S':5,'U':0} #H2 Rank Points
    H1_RP={'A':10,'B':8.75,'C':7.5,'D':6.25,'E':5,'S':2.5,'U':0} #H1 Rank Points
    
                
                    
    for course in data:
        
        course_degree=course.degree
        course_school=course.school
        course_rate=course.employability
        course_salary=course.salary
        
        alevel_IGP=course.alevel_igp
        polytechnic_IGP=course.polytechnic_igp
        degree_rank_point=0
        print(alevel_IGP)
        if alevel_IGP!=None:
            degree_rank_point+=H2_RP[alevel_IGP[0]]
            degree_rank_point+=H2_RP[alevel_IGP[1]]
            degree_rank_point+=H2_RP[alevel_IGP[2]]
            degree_rank_point+=H1_RP[alevel_IGP[3]]
        
        print("printed degree rank points")
        all_degrees_search.append(str(course_degree)+" ("+str(course_school)+")")
        course_info.append([course_rate,course_salary])
        cut_offs.append([degree_rank_point,polytechnic_IGP])
        
        
    return render_template("prospects_search.html",user=current_user,
                           all_degrees_search=all_degrees_search,
                           course_info=course_info,
                           cut_offs=cut_offs)