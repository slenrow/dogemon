
### Group Name: Group 21

### Members:
  - Cameron Hejazi (chejazi): defined actions for new routes
  - Matt Neubauer (mneub): setup accounts and session management
  - Michael Meyerson (mikemey): setup the templates and debugged python

### Extra Credit:
  - We use CSS and lots of templates for our site (no tables, standard header/footer)
  - We send a registration email confirmation for each new user
  - We implemented a Forgot Password feature (accessible through the login page)

### Details:
  - Our app lives at http://eecs485-05.eecs.umich.edu:4721/pmsbnmv/pa2/
  - Our `/pictures` folder is at  `/static/pictures` because we use Flask's fileserving
  - We used 1 late day

### Warning:
  - Our load_data.sql doesn't populate the site with photos (Issue from Project 1)
  - We don't want to get double penalized for this
  - We also want to make it easy on the graders, so we're cautioning against dropping the tables
  - see https://piazza.com/class/hkqcdhzzkxx1t8?cid=185

### Run: 
  - `cd /home/group21` (crucial to start in this directory)
  - `virtualenv venv --distribute`
  - `source venv/bin/activate`
  - `cd pmsbnmv/pa2`
  - `pip install -r requirements.txt`
  - `gunicorn -b 0.0.0.0:4721 -w 4 app:app`

