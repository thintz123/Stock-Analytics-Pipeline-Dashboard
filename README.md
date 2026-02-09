# Stock Analytics Dashboard

End-to-end stock analytics pipeline:
- Download multiple stock tickers using Yahoo Finance
- Store in MySQL database
- Analyze in Jupyter notebook
- Interactive dashboard with Streamlit

## Setup

1. Clone the repo:

```bash
git clone https://github.com/yourusername/stock_insight.git
cd stock_insight

2. Create virtual environment & install dependencies:

python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR venv\Scripts\activate # Windows
pip install -r requirements.txt

3. Configure MySQL database credentials in pipeline.py and app.py.

4. Run pipeline to download & insert data:
python pipeline.py

5. Launch Streamlit dashboard:
streamlit run app.py

6. Open notebook notebooks/analysis.ipynb for additional analysis