FROM python:3.10.12

WORKDIR /week0_starter_network_analysis

COPY . .

EXPOSE 8501

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "st.py"]