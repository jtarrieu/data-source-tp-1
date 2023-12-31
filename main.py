'''
 # @ Author: Jeremy Tarrieu
 # @ Create Time: 1970-01-01 01:00:00
 # @ Modified time: 2023-10-18 10:09:50
 # @ Description: TP data traces 1 & 2
 '''

import logging
import os
from flask import Flask, request, render_template
from logging.config import dictConfig
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from pytrends.request import TrendReq

import matplotlib.pyplot as plt

from io import BytesIO
import base64

import time
import collections


# Configure the logging settings
log_format = '%(asctime)s [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    prefix_google = """<!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-MZ43902EQ2"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-MZ43902EQ2');
    </script>"""
    return prefix_google

# Google request page displaying status code and cookies of request
@app.route('/google', methods=['GET', 'POST'])
def google_request():
    page_content = """<!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-MZ43902EQ2"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-MZ43902EQ2');
    </script>"""
    if request.method == 'POST':
        # Request to google and storing cookies
        response = requests.get('https://www.google.com')
        cookies = response.cookies.get_dict()
        page_content += f"<p>Status Code: {response.status_code}</p>"
        page_content += f"<p>Cookies: {cookies}</p>"
    
    return (
        page_content +
        """
        <form method="post">
            <input type="submit" value="Make Request to Google">
        </form>
        """
    )

# Google AAnalytics request page displaying status code, cookies and result of request
@app.route("/google-analytics", methods=['GET', 'POST'])
def google_analytics_request():
    page_content = """
    <p>Welcome to the google analytics login page :)</p>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-FVQS2TWEVX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-FVQS2TWEVX');
    </script>
    """

    if request.method == 'POST':
        # Handle the button click to make the request to Google Analytics
        ganalytics_url = "https://analytics.google.com/analytics/web/#/p407466116/reports/intelligenthome"
        req2 = requests.get(ganalytics_url)
        cookies2 = req2.cookies.get_dict()
        page_content += f"<p>Status Code: {req2.status_code}</p>"
        page_content += f"<p>Cookies: {cookies2}</p>"
        page_content += f"<p>Response Text: {req2.text}</p>"

    return (
        page_content +
        """
        <form method="post">
            <input type="submit" value="Make Request to Google Analytics">
        </form>
        """
    )

@app.route("/logger", methods=['GET', 'POST'])
def logger():
    text = ""
    if request.method == 'POST':
        # Retrieve the text from the textarea
        text = request.form.get('textarea')
  
        # Print the text in terminal for verification
        logging.info(text)
  
    return render_template('logger.html', log_message = text)

@app.route('/fetch-analytics', methods=['GET'])
def fetch_google_analytics_data():

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'round-bruin-400713-032c0a97d5b2.json'
    PROPERTY_ID = '407455001'
    starting_date = "50daysAgo"
    ending_date = "yesterday"

    client = BetaAnalyticsDataClient()
    
    def get_visitor_count(client, property_id):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[{"start_date": starting_date, "end_date": ending_date}],
            metrics=[{"name": "activeUsers"}]
        )

        response = client.run_report(request)

        #TODO: Extract the metric values
        # response = response.rows

        # return active_users_metric
        return response

    # Get the visitor count using the function
    response = get_visitor_count(client, PROPERTY_ID)

    if response and response.row_count > 0:
        metric_value = response.rows[0].metric_values[0].value
    else:
        metric_value = "N/A"  # Handle the case where there is no data

    return f'Number of visitors : {metric_value}'

@app.route('/trends', methods=['GET', 'POST'])
def trends():
    pytrends = TrendReq(hl='en-US', tz=360)  # Create a pytrends instance with your preferred settings
    pytrends.build_payload(kw_list=['linux', 'windows'], timeframe='2019-03-01 2020-10-31')
    data = pytrends.interest_over_time()
    
    # Generate a line plot
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['linux'], label='linux')
    plt.plot(data.index, data['windows'], label='windows')
    plt.xlabel('Date')
    plt.ylabel('Search Interest')
    plt.title('Google Trends Data')
    plt.legend()
    
    # Convert the plot to a bytes object and then to base64 for embedding in a web page
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    
    return render_template('trend.html', plot_data=plot_data)



# Decorator to measure execution time
def execution_time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper

def count_words_with_dict(text):
    words = text.split()
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def count_words_with_counter(text):
    words = text.split()
    word_count = collections.Counter(words)
    return word_count

@execution_time_decorator
def count_dict(text):
    return count_words_with_dict(text)
        
@execution_time_decorator
def count_counter(text):
    return count_words_with_counter(text)

@app.route('/word_count_experiment', methods=['GET'])
def word_count_experiment():
    # Load Shakespeare's text (you can also download it here if needed)
    with open('shakespeare.txt', 'r') as file:
        shakespeare_text = file.read()

    # Create lists to store execution times and results
    execution_times_dict = []
    execution_times_counter = []

    # Run the experiment 10 times
    for _ in range(100):
        result_dict, execution_time_dict = count_dict(shakespeare_text)
        result_counter, execution_time_counter = count_counter(shakespeare_text)

        execution_times_dict.append((result_dict, execution_time_dict))
        execution_times_counter.append((result_counter, execution_time_counter))

    # Extract execution times from the results
    execution_times_dict = [execution_time for _, execution_time in execution_times_dict]
    execution_times_counter = [execution_time for _, execution_time in execution_times_counter]

    # Now, you can plot the execution time distributions
    plt.plot(execution_times_dict, label='Using Dictionary')
    plt.plot(execution_times_counter, label='Using Counter')
    plt.xlabel('Execution Time (seconds)')
    plt.ylabel('Frequency')
    plt.legend()
    
    # Convert the plot to a bytes object and then to base64 for embedding in a web page
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()

    return render_template('word_count.html', plot_data=plot_data)
