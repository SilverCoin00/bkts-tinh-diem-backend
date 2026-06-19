from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import scoreresults
import languageconversion # Nhúng file language_api.py vào
import admissioncalculator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong thực tế nên để URL của frontend, VD: "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scoreresults.router)
app.include_router(languageconversion.router)
app.include_router(admissioncalculator.router)
