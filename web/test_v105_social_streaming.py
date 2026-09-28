from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need("def _gsf_tiktok_direct_post_file" in s,"TikTok file-stream publisher exists")
need("def _gsf_youtube_upload_file" in s,"YouTube file publisher exists")
need("def _gsf_instagram_publish_reel_file" in s,"Instagram file publisher exists")
need("_gsf_tiktok_direct_post(bytes(video), pack)" not in s,"TikTok whole-master bytes call removed")
need("_gsf_instagram_publish_reel_auto(bytes(video), pack)" not in s,"Instagram whole-master bytes call removed")
need("_gsf_youtube_upload(\n                bytes(video)," not in s,"YouTube whole-master bytes call removed")

publish=next(
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name=="_gsf_publish_social_upload"
)
ps=ast.get_source_segment(s,publish) or ""
need("_gsf_youtube_upload_file(exported" in ps,"YouTube publishes existing exported file")
need("_gsf_tiktok_direct_post_file(exported" in ps,"TikTok publishes existing exported file")
need("_gsf_instagram_publish_reel_file(exported" in ps,"Instagram publishes existing exported file")
need("bytes(video)" not in ps,"normal social publish path never duplicates master bytes")

tt=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_tiktok_direct_post_file")) or ""
need("open(video_path,\"rb\")" in tt,"TikTok streams master from file")
need(".read(this_size)" in tt,"TikTok reads bounded chunks")
need("read_bytes" not in tt and "bytes(video" not in tt,"TikTok file publisher has no whole-file read")

yt=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_youtube_upload_file")) or ""
need('deps["MediaFileUpload"]' in yt,"YouTube keeps resumable MediaFileUpload")
need("video_path" in yt and "f.write" not in yt,"YouTube consumes existing path without rewriting master")

ig=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_instagram_publish_reel_file")) or ""
need("client.upload_file(" in ig,"Instagram stages with S3 file streaming")
need("generate_presigned_url" in ig,"Instagram gives Meta short-lived signed URL")
need("Body=bytes" not in ig and "read_bytes" not in ig,"Instagram file publisher has no whole-file copy")

# Legacy byte APIs stay available for local/backward compatibility.
for name in ("_gsf_tiktok_direct_post","_gsf_youtube_upload","_gsf_instagram_publish_reel_auto"):
    need(any(isinstance(n,ast.FunctionDef) and n.name==name for n in tree.body),f"legacy compatibility function {name} preserved")

compile(s,str(p),"exec")
print("V105 social streaming: PASS")
