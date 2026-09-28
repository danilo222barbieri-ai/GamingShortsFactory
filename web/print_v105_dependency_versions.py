import importlib.metadata as m
names=[
"streamlit","faster-whisper","numpy","boto3",
"google-api-python-client","google-auth-oauthlib","google-auth-httplib2",
"botocore","ctranslate2","av"
]
for name in names:
    try:
        print("GSF_DEP_VERSION",name,m.version(name),flush=True)
    except Exception:
        print("GSF_DEP_VERSION",name,"MISSING",flush=True)
