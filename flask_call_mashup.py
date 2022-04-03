from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from Mixer import Mixer

import stream_azure as saz

app = Flask(__name__)


@app.route("/")
def start():
    progress_bar = False
    song_list = saz.list_blobs_flat_listing()

    resp = make_response(render_template('index_main.html', song_list=song_list, progress_bar=progress_bar))
    resp.delete_cookie('song1')
    resp.delete_cookie('song2')
    resp.delete_cookie('mash_up_name')

    return resp


@app.route("/action", methods=['POST', 'GET'])
def action():
    progress_bar = True
    song_list = saz.list_blobs_flat_listing()
    song1 = request.form.get("song1")
    song2 = request.form.get("song2")
    mash_up_name = request.form.get("mashup_name")

    resp = make_response(render_template('index_main.html', song_list=song_list, progress_bar=progress_bar))
    resp.set_cookie('song1', song1)
    resp.set_cookie('song2', song2)
    resp.set_cookie('mash_up_name', mash_up_name)

    return resp


@app.route("/work_progress", methods=['POST', 'GET'])
def work_progress():
    song1 = request.cookies.get('song1')
    song2 = request.cookies.get('song2')
    mash_up_name = request.cookies.get('mash_up_name')
    if song1 or song2:
        mixer = Mixer()
        return Response(mixer.mix(song1, song2, mash_up_name), mimetype='text/event-stream')
    return 'ERROR: Missing song names, refresh and try again'


@app.route("/player", methods=['POST', 'GET'])
def test():
    mash_up_name = request.cookies.get('mash_up_name')
    mash_url = 'https://mashups.blob.core.windows.net/mashups/mixed_songs/' + mash_up_name + '.wav'
    mash_url = mash_url.replace(' ', '%20')
    return render_template('index_second_page.html', mashup_url=mash_url), mash_up_name


if __name__ == "__main__":
    app.run(port=5005, debug=False)
