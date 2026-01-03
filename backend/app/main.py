from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api import dashboard, analytics, transactions, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(transactions.router)
