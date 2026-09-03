# Built with the REPO ROOT as build context (see docker-compose.yml's
# chain_worker service — `context: .`, `dockerfile: workers/chain_worker/Dockerfile`),
# not this directory — that's what makes `COPY api/app` below possible.
FROM python:3.11-slim

WORKDIR /worker

COPY workers/chain_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workers/chain_worker/worker.py workers/chain_worker/fabric_client.py ./

# worker.py reuses api/app's models/database/audit/config directly instead
# of duplicating the schema — see worker.py's own comment. This lands at
# /api/app in the image, matching the relative path
# (os.path.dirname(__file__) + "../../api") worker.py's sys.path insertion
# computes from /worker/worker.py.
COPY api/app /api/app

CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]
