from pathlib import Path
import ast,sys

app=Path(sys.argv[1]).read_text(encoding="utf-8")
server=Path(sys.argv[2]).read_text(encoding="utf-8")

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

ast.parse(app)
ast.parse(server)

need('GSF_INSTAGRAM_APP_ID' in app and 'GSF_INSTAGRAM_APP_SECRET' in app,
     "app supports dedicated Instagram App credentials")
need('"https://graph.instagram.com"' in app,
     "Instagram Login Graph host supported")
need('social-stage/{GSF_SESSION_ID}/instagram-' in app,
     "Instagram Reel uses signed S3 staging")
need('generate_presigned_url' in app and '"get_object"' in app,
     "signed public video URL generated for Meta fetch")
need('client.delete_object(Bucket=bucket,Key=key)' in app,
     "temporary Instagram staging object is cleaned up")
need('graph_base+"/"+quote(ig_user_id,safe="")+"/media"' in app,
     "Reel create uses selected Instagram Graph host")
need('graph_base+"/"+quote(ig_user_id,safe="")+"/media_publish"' in app,
     "Reel publish uses selected Instagram Graph host")

need('INSTAGRAM_APP_ID=_env_first("GSF_INSTAGRAM_APP_ID"' in server,
     "standalone connector reads Instagram App ID")
need('INSTAGRAM_APP_SECRET=_env_first("GSF_INSTAGRAM_APP_SECRET"' in server,
     "standalone connector reads Instagram App Secret")
need('INSTAGRAM_SCOPES="instagram_business_basic,instagram_business_content_publish"' in server,
     "minimal Instagram publishing scopes configured")
need('"https://www.instagram.com/oauth/authorize?"' in server,
     "Instagram Business Login authorize endpoint used")
need('INSTAGRAM_REDIRECT_URI=(PUBLIC_APP_URL+"/auth/instagram/callback")' in server,
     "Instagram OAuth uses dedicated callback path")
need('"/auth/instagram/callback"' in server,
     "dedicated Instagram callback route is handled")
need('"https://api.instagram.com/oauth/access_token"' in server,
     "Instagram code exchange endpoint used")
need('"https://graph.instagram.com/access_token?"' in server,
     "Instagram long-lived token exchange used")
need('"fields":"user_id,username,id,account_type"' in server,
     "professional Instagram user id is discovered")
need('"api_host":"https://graph.instagram.com"' in server,
     "Instagram Login token records Graph host")
need('"mode":"facebook_login"' in server,
     "legacy Facebook Login remains available as fallback")

print("V104.7 Instagram Login: PASS")
