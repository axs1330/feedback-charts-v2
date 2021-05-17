# feedback-charts-v2
Visualization of feedback via interactive charts

The current version of the project uses Chart.js and a Bootstrap framework to visualize randomly generated feedback data through a Django server.

Primary files include:

core\models.py - defines the data structure of feedback and givers

core\views.py - generates the filtered chart data from user feedback

templates\bootstrap_form.html - formats the webpage and utilizes Ajax and javascript for creating the charts

core\management\commands\populate_db.py - creates random feedback data for visualization
