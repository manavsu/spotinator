from fastapi import APIRouter, HTTPException, Depends, File, Form, Request
from sqlalchemy.orm import Session
from models import User, get_db
import logging
from pydantic import BaseModel
from datetime import date
from fastapi_login import LoginManager
import os
import pkce
from time import sleep
from datetime import timedelta, datetime
from urllib.parse import urlencode, urlparse, parse_qs
import requests
from models import get_db
import utils.password_utils as password_utils

log = logging.getLogger(__name__)

router = APIRouter()

code_verifier = pkce.generate_code_verifier()
code_challenge = pkce.get_code_challenge(code_verifier)

tokens_db = {}  # TODO: move to secure storage, e.g., Redis

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = "87817b24e47a4e10bc3ba462b0c3c35c"  # Replace with your Spotify client ID
REDIRECT_URI = "http://localhost:8000/spotify/callback"
SCOPES = "user-read-private user-read-email app-remote-control streaming"  # Modify based on your needs


@router.get("/spotify/callback")
async def spotify_callback(request: Request):
    """Handles the OAuth callback from Spotify"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received.")

    # Exchange authorization code for access token
    token_data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "code_verifier": code_verifier,
    }
    response = requests.post(TOKEN_URL, data=token_data)
    tokens = response.json()
    print(tokens)

    if "access_token" not in tokens:
        raise HTTPException(status_code=400, detail="Failed to obtain access token.")

    # Store tokens (⚠️ Use a database in production)
    tokens_db["access_token"] = tokens["access_token"]
    tokens_db["refresh_token"] = tokens["refresh_token"]

    return {"message": "Login successful!", "access_token": tokens["access_token"]}


@router.get("/spotify/login_url")
async def login():
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
    return {"login_url": auth_url}


@router.get("/spotify/token")
async def get_access_token():
    if "access_token" in tokens_db:
        return {"access_token": tokens_db["access_token"]}
