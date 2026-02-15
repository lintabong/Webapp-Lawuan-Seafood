
from flask import session
from app.lib.supabase_client import supabase

def auth():
    supabase.postgrest.auth(session['access_token'])
