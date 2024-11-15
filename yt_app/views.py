from django.shortcuts import render, redirect, HttpResponse
from pytube import YouTube
import os
from django.contrib import messages
from wsgiref.util import FileWrapper
import requests
import http.client
import json
from django.http import FileResponse, HttpResponse
from django.utils.encoding import smart_str
import tempfile
import instaloader
from django.conf import settings

# Create your views here.
conn = http.client.HTTPSConnection("instagram-scraper-api3.p.rapidapi.com")

def index(request):
    return render(request, 'yt_app/index.html')

def getVideo(request):

    video_url = request.POST.get('url')
    loader = instaloader.Instaloader()

    # Extract the shortcode from the URL
    shortcode = video_url.split("/")[-2]

    # Download the post using the shortcode
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        if post.is_video:
            loader.download_post(post, target="downloads")  # Downloads to a folder named 'downloads'
            print(post.video_url)
            print(post.url)
            print("Video downloaded successfully!")
    
            nam=""
            videos = []
            vid={"url": "",
                "nam": "",
                "id": "",
                "desc": ""}
            i=0
            vid["url"]=post.url
            vid["desc"]="Desc"
            vid["id"]="id"
            # vid["url"]=post.url
            print(vid)
            videos.insert(i,vid)
            
            request.session['video_url'] = post.video_url
            request.session['imgID'] = str(post.mediaid) +  ".jpg"
            request.session['mediaID'] = str(post.mediaid)
            response = requests.get(post.url, stream=True)

            if response.status_code == 200:
                # image_name = str(post.mediaid) +  ".jpg"
                image_path = os.path.join(settings.MEDIA_ROOT, f"{post.mediaid}.jpg")
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                context = {
                    'image_name': f"{post.mediaid}.jpg",
                    'image_url': image_path
                }
                if os.path.exists(image_path):
                    os.remove(image_path)
                with open(image_path, "wb") as file:
                    file.write(response.content)
            print(videos)
            context = {'videos': videos, 'audios': '', 'thumbnail': post.url, 'title': post.caption, 'url':post.video_url, 'imgID':str(post.mediaid) +  ".jpg"}
            return render(request, 'yt_app/download.html', context)
    
        else:
            print("The provided URL does not contain a video.")
            return render(request, 'yt_app/download.html', context)
    except Exception as e:
        print("An error occurred:", e)
        return render(request, 'yt_app/download.html', context)


def downloadVid(request):
    try:
        # Download video to a temporary file
        url = request.session.get('video_url')

        homedir = os.path.expanduser("~")
        download_path = os.path.join(homedir, 'Downloads', 'video.mp4')

        # Download video and save it to the Downloads folder
        response = requests.get(url, stream=True)
        
        response.raise_for_status()

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        videoID=request.session['mediaID']
        # Create a response to send the file as an attachment
        response = FileResponse(open(download_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = 'attachment; filename=' + str(videoID) +'.mp4'
        return response

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Failed to download video: {str(e)}", status=500)    # if request.method == "POST":
