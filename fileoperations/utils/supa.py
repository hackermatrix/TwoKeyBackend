
from supabase import create_client, Client
from decouple import config

url = config('SUPA_URL')
key = config('SERVICE_ROLE_KEY')
supabase: Client = create_client(url, key)


def create_signed(filename,time_in_seconds):
    url = supabase.storage.from_(config('BUCKET_NAME')).create_signed_url(filename,time_in_seconds)
    return url["signedURL"]

# res = supabase.storage.from_('TwoKey').list()

# res = supabase.storage.from_('TwoKey').get_public_url('hehehe')
# print(res)
# res = supabase.storage.from_('TwoKey').download("hehehe")

# print(res)