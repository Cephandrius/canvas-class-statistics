import pandas as pd
import re
import json
import urllib.request

#Constants for HTTP API
course_num = "10989"
developer_token = "7407~Muwvpd3rhwEmYy1hBCTj4TtbtU51icAkUfdv8vZTkcxdAPH6tSVSA6Hsm388mxI8"
url_prefix = "https://byu.instructure.com/api/v1/courses/" + course_num
url_submissions = url_prefix + "/students/submissions?student_ids=all&page_size=100"
url_assignment = url_prefix + "/assignments/"
url_enrollments = url_prefix + "/enrollments"
headers = {}
headers["Authorization"] = " Bearer " + developer_token

#Constants for JSON attributes
USER_ID = "user_id"
ASSIGNMENT_ID = "assignment_id"
SUBMISSION_ID = "id"
GRADE = "grade"
MISSING = "missing"
LATE = "late"
POST_DATE = "posted_at"
SUBMISSION_DATE = "submitted_at"
ASSIGNMENT_GRADE = "grade_matches_current_submission"
MAX_GRADE = "points_possible"
ASSIGNMENT_NAME = "name"
ASSIGNMENT_STATE = "workflow_state"

def get_json(url, headers):
    """
    * input:
    *   url: (string) an http/https url that is a GET request that will return a JSON
    *   headers: (dictionary) headers for the request 
    *
    * output:
    *   (list, string)
    *       list: represents the JSON object that was read from url, for the Canvas API, this is 
    *           an list of objects which is represented in python as a list of dictionaries
    *       string: the url of the next page of results, returns None if this is the last page
    """

    request = urllib.request.Request(url,headers=headers,method="GET")
    response = urllib.request.urlopen(request)
    body = response.read().decode("UTF-8")
    useful_body = clean_json(body)

    try:
        data = json.loads(useful_body)
    except BaseException as e:
        print(e)
        o_file = open("failed.json", "w")
        o_file.write(useful_body)
        o_file.close()
        return None, None

    links = response.getheader("link")
    if links == None:
        return data, None
    next_url = get_next_url(links)
    return data, next_url


def clean_json(body):
    """
    * This function gets rid of backslashes that occur before characters that shouldn't be escaped
    * input:
    *   body: (string) original JSON body from a url
    * output:
    *   string: the JSON that can be parsed correctly by the json module
    """
    useful_body = body.replace("\\\\","\\")
    reg_ex = "\\\\([^un\"\\\\_])"
    useful_body = re.sub(reg_ex, "\\1", useful_body)
    return useful_body


def get_next_url(links):
    """
    * In the canvas API, it doesn't return all the data you request in one response, it paginates
    * the results so they are spread across multiple urls, this function gets the next url from
    * the links header of the http response
    * input:
    *   links: (string) contents of the links header
    * output:
    *   string: url for next page of data or none if there are no more pages
    """
    next_url = None
    prev_comma = -1
    while True:
        next_comma = links.find(",", prev_comma + 1)
        if next_comma == -1:
            break
        sub_link = links[prev_comma: next_comma]
        if sub_link.find("rel=\"next\"") != -1:
            left_arrow = sub_link.find("<")
            right_arrow = sub_link.find(">")
            next_url = sub_link[left_arrow + 1: right_arrow]
            break
        prev_comma = next_comma
    return next_url


def element_wise_and(element1, element2):
    """
    * This function is a helper function for pandas. I want to get a DataFrame with every element
    * that meets two different boolean expressions. I didn't find an easier way to achieve this 
    * effect.
    * input:
    *   element1: (boolean) element from first array
    *   element2: (boolean) element form second array
    * output:
    *   boolean: the and of the two elements
    """
    return element1 and element2


def analyze_submissions(submissions):
    """
    * input:
    *   submissions: (list of dictionaries or DataFrame) every submission for the class
    * output:
    *   DataFrame: summary statistics for the class
    """

    if(type(submissions) == type([])):
        dataframe = pd.DataFrame(submissions)
    elif(type(submissions) == type(pd.DataFrame())):
        dataframe = submissions
    else:
        print("Got an unexpected type for submissions")
        return

    dataframe.sort_values(ASSIGNMENT_ID, inplace=True)
    enrollments = get_data(url_enrollments, headers)
    user_ids = enrollments[(enrollments.type == "StudentEnrollment").combine(enrollments.enrollment_state == "active", element_wise_and)].drop_duplicates(USER_ID)[USER_ID].to_list() 
    assignment_ids = dataframe.drop_duplicates(ASSIGNMENT_ID)[ASSIGNMENT_ID].to_list()

    results = pd.DataFrame([],columns=["name", "submissions", "total_grade", "average_grade", "missing", "late", "graded", "percent_graded"])
    for assignment_id in assignment_ids:
        assignment_results = {"name":"","submissions":0,"total_grade":0,"average_grade":0,"missing":0,"late":0,"graded":0, "percent_graded":0}
        data, next_url = get_json(url_assignment + str(assignment_id), headers)
        assignment_results["name"] = data[ASSIGNMENT_NAME]
        print(data[ASSIGNMENT_NAME])
        print(data['submission_types'])
        for user_id in user_ids:
            user_submissions = dataframe[(dataframe[USER_ID]==user_id).combine(dataframe[ASSIGNMENT_ID]==assignment_id,element_wise_and)]
            if(user_submissions[SUBMISSION_ID].count() == 0):
                continue

            user_submissions = user_submissions.sort_values(SUBMISSION_DATE, ascending=False, na_position="last")
            most_recent_submission = user_submissions.iloc[0]
            state = most_recent_submission[ASSIGNMENT_STATE]
            if(not most_recent_submission[MISSING] and most_recent_submission[ASSIGNMENT_STATE] != "unsubmitted"):
                assignment_results["submissions"] += 1
                if(state == "graded"):
                    assignment_results["graded"] += 1
                    grade = most_recent_submission[GRADE]
                    assignment_results["total_grade"] += grade

                if(most_recent_submission[LATE]):
                    assignment_results["late"] += 1

        if(assignment_results["submissions"] != 0):
            assignment_results["percent_graded"] =  assignment_results["graded"] /assignment_results["submissions"] * 100
        else:
            assignment_results["percent_graded"] = 100

        if(assignment_results["graded"] != 0):
            assignment_results["average_grade"] = assignment_results["total_grade"] / assignment_results["graded"]
        else:
            assignment_results["average_grade"] = 0

        assignment_results["missing"] = len(user_ids) - assignment_results["submissions"]
        assignment_results["average_grade"] = assignment_results["average_grade"] / data[MAX_GRADE] * 100
        results = results.append([assignment_results], sort=True)
    return results

def get_submissions():
    """
    * This function will get all the submissions for the class and then save them to grades.csv
    * input:
    * output:
    *   None
    """
    dataframe = get_data(url_submissions, headers) 
    dataframe.to_csv("grades.csv")

def get_data(url, headers):
    """
    * input:
    *   url: (string) the url for first page of results
    *   headers: (dictionary) all the headers to be included in http/https request
    * output:
    *   DataFrame: a table with all the submissions and all their associated data
    """
    data, next_url = get_json(url, headers)
    while next_url is not None:
        new_data, next_url = get_json(next_url, headers)
        data.extend(new_data)
    dataframe = pd.DataFrame(data)
    return dataframe

get_submissions()
submissions = pd.read_csv("grades.csv")
results = analyze_submissions(submissions)
results.to_csv("results.csv")
