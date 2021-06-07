# Get Class Statistics for Canvas

This [script](analyze.py) will go to a canvas domain and grab data from each assignment like how many submissions there are, the average grade, how many are missing, how many are late, and what percent of submissions have been graded. I made this [script](analyze.py) because I volunteered to grab these statistics for a weekly ta meeting. If there is a way to automate something I have to do, I will do it even it means that I will spend more time automating it than just grabbing the information manually. 

## Canvas API

The [Canvas API](https://canvas.krsu.edu.kg/doc/api/all_resources.html) is moderately well documented, but I will explain some idosyncrasies with it. An assignment is a paticular thing that a student has to complete for a grade while a submission is an attempt of one students to complete that assignment. One would think that a student would have to submit something for them to have a submission, but that is not the case. For some types of assignments, every student has to have at least one submission at all times. Students that haven't submitted anything will be given a submission whose "workflow\_state" attribute is "unsubmitted". The only type of assignment that I have identified with type of behavior is "online\_quiz". 

A course in a class that students and teachers are members of where students receive grades and the teacher can change aspects of the class.

### OAuth

Canvas has a way to allow third-party applications to get permission to access the API for any class using the OAuth process. I have not used this process because it required premissions I didn't have. To allow my application to still work, I have you modify the [script](analyze.py) to include an access token from a user. *Exercise caution while using this script* because this access token can be used to change *anything* about the course. You must restrict access to the [script](analyze.py) to maintain security. I do not modify any information about the course in this script, but be aware that this script has great potential to cause security problems. If you suspect that the access token has been leaked, you can regenerate the token to invalidate the leaked token and provide you with a new token to use. Information on how to do this is found in the Preparation to Use section.

## Preparation to Use  

Before using this [script](analyze.py) on a new class, there are a couple of changes that need to be made to it. There a many constants that are at the beggining of the [script](analyze.py), but you only need to change a few of them. 

The "course\_num" needs to be updated to number for the current course. To get this number, log onto canvas and navigate to the main page of the course. In the url there should be "/courses/". The number following this string is your course number.

The "domain\_name" need to be updated as well. Follow the instructions of the previous paragraph. The part of the url before "/courses/" is the domain name.

The "developer\_token" is the final constant that needs to be updated. To get this token, navigate to the settings of a user that has permission access student grades. There is a header called "Approved Integrations:" with a button underneath it that says "New Access Token". Press this button and enter an appropriate name. I would reccomend setting an expiration date for the token as well to minimize risk of security problems. Click "Generate Token" and a new window will open up. Copy the complete token and paste it to the [script](analyze.py). Be careful, if you leave the page before you do this, you can never see this full token again. If you do happen to do this, click on the "details" next to the token in the table. Click "Regenerate Token" to gain another token to use. Repeat this step as many times as you forget to copy tho token. To reiterate the warning in the OAuth section, this token can be used modify anything about the class, which includes modify grades. Make sure to restrict access of the [script](analyze.py) to authorized users.

## Usage

This script has no command line arguments, so the only thing you need to do is run the script as a Python3 script. If you have both Python2 and Python3 installed on your system, you need to find the correct command. Type the following command to get the version of python.

> $ python --version

If this prints "Python 3.X.X", with the "X"'s representing any number, then you are good to use "python" to execute the script. If it prints something else, try this command.

> $ python3 --version

If this command doesn't print out "Python 3.X.X", then ask your system administrator how to run Python3 scripts.

If you have identified the command to run Python3 scripts, then this is how you run this [script](analyze.py).

> $ python analyze.py 

> $ python3 analyze.py

Use the command that corresponds to what you found to have the correct verision.

### Output

There are a couple of files that are created when you run this [script](analyze.py), results.csv, and submissions.csv. results.csv have the summary statistics for the course. submissions.csv have every submission for the class.
