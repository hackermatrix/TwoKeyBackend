
from supabase import create_client, Client
from decouple import config

url = config('SUPA_URL')
key = config('SERVICE_ROLE_KEY')
supabase: Client = create_client(url, key)