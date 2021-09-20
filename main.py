import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from awsl.awsl import WbAwsl
from awsl.router import router


logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO
)

awsl = WbAwsl()
awsl.start()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="")
