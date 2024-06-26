import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
from IPython.display import HTML


load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)
            return 
            

def header_titanic():
    df = pd.read_csv('/app/templates/titanic.csv')
    table_html = df.head().to_html(index=True)
    return table_html

def barchart_titanic():
    df = pd.read_csv('/app/templates/titanic.csv')
    survival_counts = df.groupby(['Sex', 'Survived'])['PassengerId'].count()
    fig, ax = plt.subplots()
    survival_counts.unstack().plot(kind='bar', ax=ax)
    ax.set_title('Survival Counts by Sex')
    ax.set_xlabel('Sex')
    ax.set_ylabel('Count')
    bar_chart_html = HTML(mpld3.fig_to_html(fig))

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

def titanic():
    table = header_titanic()
    chart = barchart_titanic()
    return render_template('titanic.html', name= "BIPM", table = table, chart = chart)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
    app.use_static_for_url('/app/templates', static_folder='templates')