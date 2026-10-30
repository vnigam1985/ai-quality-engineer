FROM python:3.12-slim
WORKDIR /srv
# Set WITH_TRACING=1 to add the Phoenix tracing packages (week 7, make up-tracing does this)
ARG WITH_TRACING=0
COPY app/requirements.txt /srv/app/requirements.txt
COPY requirements-tracing.txt /srv/requirements-tracing.txt
RUN pip install --no-cache-dir -r /srv/app/requirements.txt \
 && if [ "$WITH_TRACING" = "1" ]; then pip install --no-cache-dir -r /srv/requirements-tracing.txt; fi
COPY app /srv/app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
