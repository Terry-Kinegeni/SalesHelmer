# SalesHelmer
Sales Helmer is a data-driven basket analysis application that utilizes the Apriori algorithm to study customer purchasing behavior. By analyzing transaction data, Sales Helmer helps businesses identify frequently purchased item combinations, optimize product placement, and improve sales strategies.

**Features**


Basket Analysis: Identifies frequently purchased item sets using the Apriori algorithm.

Association Rule Mining: Discovers strong associations between products based on purchase history.

User-Friendly Interface: Simple and intuitive dashboard for data visualization.

CSV Data Import: Supports transaction data uploads via CSV files.

Customizable Support & Confidence Levels: Allows users to adjust support and confidence thresholds for rule generation.

Data Insights & Visualization: Provides graphical representation of association rules and itemset frequency.


**Images** 


**Home**

The main dashboard of Sales Helmer, displaying an overview of frequent itemsets and association rules.
![image](https://github.com/user-attachments/assets/9dc641c8-bdf8-4054-b461-aca2d5fe4418)

**Upload Data**

A dedicated page where users can upload transaction data in CSV format for analysis.
![image](https://github.com/user-attachments/assets/736f8859-1f47-4d46-acb7-84137e9b7566)

**Rules Visualization**

Displays association rules in a graph format, showing relationships between different items.
![image](https://github.com/user-attachments/assets/3ef0a1a4-4910-4a5e-a64e-9fc187760b82)

**Insights**

Provides recommendations based on the generated rules, helping businesses optimize product placement and marketing.
![image](https://github.com/user-attachments/assets/9c695d56-5add-49e1-983a-ef34eeba73c2)

**Analysis**

Provides pre-existing insight based off the existing data
![image](https://github.com/user-attachments/assets/d53d1e5b-5621-4b3b-98ca-654a00c36e7f)



**Project Structure**



![image](https://github.com/user-attachments/assets/988bb9eb-2b4f-4c3d-a1f6-b74586426cfd)



**Requirements**

Before running the project, ensure you have the following installed:

Python 3.x



Virtualenv




**Setup**

Clone the repository:
git clone https://github.com/yourusername/sales-helmer
cd sales-helmer/

Create and activate a virtual environment:


python -m venv .venv



source .venv/bin/activate  # On macOS/Linux


.venv\Scripts\activate  # On Windows



Install dependencies:

pip install -r requirements2.txt


Run the application:

python app.py


**License**
This project is licensed under the MIT License - see the LICENSE file for details



