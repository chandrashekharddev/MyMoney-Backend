import matplotlib.pyplot as plt 
import numpy as np
from io import BytesIO
from PIL import Image
import seaborn as sns 



## 1: Daily Spending Line Chart
def plot_daily_spending(dates, amounts):
    plt.figure(figsize=(10, 5))
    plt.plot(dates, amounts, marker='o', linestyle='-', color='b')
    plt.title('Daily Spending Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount Spent ($)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    return img