# Advanced-Search-for-LD - V2

<H2>Overview</H2><br>
It will allow you to copy the LD data to your CRDB and then be able to search across projects, environments, and flags.<br>
I have create a video with the UI flow @"Adv Srch for LaunchDarkly quick overview.mp4" overview video <BR>
<H4>V2</H4>Adds cost allocation functionality shown on the home page. Cost can be assigned by department. Adding customers and departments is done manually directly on the DB by importing the data from your records to the CRDB tables. <BR>


<h2> Technology</h2><br>
Backend: built on Python 3.x<br>
Frontend: build on JS<br>
Database: SaaS CRDB instance<br>

<H2>Entry points for the project</H2>
"Python3 es_main.py" is the entry point for the backend<br>
"http://localhost:8080/index.html" is the entry point for the front end<br>

<H2>Notes</H2><br>
<UL>
  <LI>the first time you create the user profile it will create the settings file on the python App root directory </LI>
  <LI>the Settings file is encryped using a python Library</LI>
  <LI>please make sure you have installed locally (PIP3 ....) all the python libraries used in the backend</LI> 
</UL>

<H2>Dependencies</H2>
<UL>
  <LI><B>Python Data Access Library:</B> https://www.psycopg.org/docs/index.html</LI>
  <LI><B>JS UI Library: </B>https://demos.themeselection.com/sneat-bootstrap-html-admin-template/documentation/index.html</LI>
</UL>
