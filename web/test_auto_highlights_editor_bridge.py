from web.auto_highlights.editor_bridge import highlight_editor_state, prepare_editor_launch, stash_editor_launch

def test_highlight_becomes_local_editor_clip():
    folder={"provider":"twitch","broadcast_id":"live1"}
    item={"id":"h1","start_seconds":6130,"end_seconds":6160}
    launch=prepare_editor_launch(folder=folder,item=item,materialize_clip=lambda f,i:"/tmp/h1.mp4")
    assert launch.video_path=="/tmp/h1.mp4"
    assert launch.initial_state["inPoint"]==0
    assert launch.initial_state["outPoint"]==30
    assert launch.initial_state["autoHighlightSourceStart"]==6130
    ss={}
    stash_editor_launch(ss,launch)
    assert ss["gsf_editor_source_path"]=="/tmp/h1.mp4"
    assert ss["gsf_auto_highlight_launch"]["source"]["provider"]=="twitch"
