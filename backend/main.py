from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BPDA Assignment 1",
    description="Api to interact with the smart contract.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Root Endpoint")
async def root():
    """
    Root Endpoint
    This endpoint provides a greeting message and directs users to the Swagger UI documentation for the API.
    By navigating to `/docs`, users can access the interactive API documentation where they can see all
    available endpoints, their expected parameters, and try out the API directly from the browser.
    """
    return {"message": "Welcome to the API. Check /docs for Swagger documentation."}
