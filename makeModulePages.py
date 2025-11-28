from classes.moduleManager import ModuleManager
from classes.memberManager import MemberManager
from classes.meetingManager import MeetingManager
from classes.meeting import Meeting
from classes.module import Module
from classes.sub import Sub
import dominate
from dominate.tags import *
import os
import json
import re
from functions.download import web
from classes.vote import Vote
from classes.member import Member
from datetime import date
from yake.highlight import TextHighlighter
from dominate.util import raw
from functions.support import cwdpath
from partij_analyse import partij_analyse, partij_analyse_per_partij
from dominate.tags import html, head, body, div, span, a, script
from dominate.tags import a as anchor
from support.getInhoudFromPDF import getInhoudFromPDF
import math

#--- Render
def render_vote_html(v):
    vote_container = makeDivForVote(v)  # Render the vote container in isolation

    return vote_container.render()

def render_keywords_html(keywords_list):
    if not keywords_list:
        return "" # Return an empty string if there are no keywords
    words = [w.lower() for w in keywords_list]
    return div(span(' '.join(words), cls='keywords')).render()


def generate_and_save_card_details(module, base_path=""):

    card_id = module.module_id  # e.g., '12345'

    # Ensure the target directory exists
    details_dir = os.path.join(base_path, "Presentation", "htmls", "cards")
    os.makedirs(details_dir, exist_ok=True)

    # 1. Generate HTML for each part
    details_data = {}


    if module.vote_id:
        vote_obj = Vote(module.vote_id)
        details_data['vote'] = render_vote_html(vote_obj)

    if module.keywords:
        details_data['keywords'] = render_keywords_html(module.keywords)

    details_data['inhoud'] = getInhoudFromPDF(module)



    # 2. Write the structured data to a JSON file
    file_path = os.path.join(details_dir, f"{card_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(details_data, f)

    # 3. Return the relative path for use in the HTML data-* attribute
    return f"cards/{card_id}.json"



def new_box(date_str):
    box = div(cls='date_box wrapper', id_ = date_str)
    box+=div(date_str,cls='date_box_header')
    return box

def makeDivForVote(v):
    total_votes = len(v.member_votes)
    voor = {}
    tegen = {}
    #-- verzamel votes
    for person, vote in v.member_votes.items():
        member = Member(person)
        if vote == 'voor':
            if member.party in voor:
                voor[member.party] += 1
            else:
                voor[member.party] = 1
        else:
            if member.party in tegen:
                tegen[member.party] += 1
            else:
                tegen[member.party] = 1
    with div(cls='hidden-content') as vote_container:
        with div(id='vote_box',cls='hidden-content') as vote_box:
            for partij in voor:
                proportion = voor[partij] / total_votes
                if partij == 'Partij voor de Dieren': partij = 'PvdD'
                if 'ouderen' in partij.lower(): partij = 'OA'
                vote_div =  div(id = 'vote',cls=partij)
                vote_div+=span(partij)

                if 'style' not in vote_div.attributes:
                    vote_div['style'] = ""

                vote_div['style'] += "background-color: green;"
                vote_div['style'] += f" width:{proportion*100}%"
                vote_box+=vote_div

            for partij in tegen:
                proportion = tegen[partij] / total_votes
                if partij == 'Partij voor de Dieren': partij = 'PvdD'
                if 'ouderen' in partij.lower(): partij = 'OA'
                vote_div = div(id='vote', cls=partij)
                vote_div += span(partij)

                if 'style' not in vote_div.attributes:
                    vote_div['style'] = ""

                vote_div['style'] += "background-color: red;"
                vote_div['style'] += f" width:{proportion * 100}%"
                vote_box += vote_div
    return vote_container

def remove_before_phrase(s, phrase="De raad roept"):
    _, _, after = s.partition(phrase)
    return phrase + after

def startStringAtFirstrLetter(s):
    for i, char in enumerate(s):
        if char.isalpha():  # Check if the character is a letter
            return s[i:]
    return s

def convert_date_to_dutch(date_str):
    # Define a mapping of month numbers to Dutch names
    months_dutch = {
        "01": "jan",
        "02": "feb",
        "03": "maa",
        "04": "apr",
        "05": "mei",
        "06": "jun",
        "07": "jul",
        "08": "aug",
        "09": "sep",
        "10": "okt",
        "11": "nov",
        "12": "dec",
    }

    # Split the date string into its components (day, month, year)
    day, month, year = date_str.split("-")

    # Get the Dutch month name by looking up the month
    month_name_dutch = months_dutch.get(month, "")

    # Combine the month name and year in the desired format
    return f"{month_name_dutch} {year}"








def fancy(text):
    return text
    try:
        th = TextHighlighter(max_ngram_size=3, highlight_pre="<span class='highlight' >", highlight_post="</span>")
        out = th.highlight(text, keywords)
    except:
        out = ''
    return out




    parts = []  # To collect fragments of the DOM structure

    # Split the text into words and rebuild it with styled spans for keywords
    for word in text.split():
        w = word.strip('.,')
        if sum(1 for c in w if c.isupper())<2:
            w = w.lower()

        w = w.replace('(', '').replace(')','')




        if w in keywords:  # Match keyword (strip punctuation like ',' or '.')
            parts.append(span(word, cls='highlight'))
        else:
            parts.append(word)  # Add plain text as-is
        parts.append(' ')
    return parts


def makeDivForMeeting(m,id_,cls_,room):
    print(m.meeting_id)
    print(room)
    if not m.type:
        return

    if 'vergadering' in m.type.lower():
        typeclass = 'vergadering'
    else:
        typeclass = 'avond'

    if room not in m.meeting_subid:
        return



    url = f'/vergadering/{m.meeting_subid[room]}.html'

    with div(id=id_,cls=f'{cls_} panel {typeclass} clickable-div', data_url=url) as d:
        #--- Title bar

        if m.date and not 'indexpage' in cls_:
            span(convert_date_to_dutch(m.date),cls='date')

        span(room,cls=f'room {room}')


        if isinstance(m.title,dict) and m.title[room]:
            titel = m.title[room].replace('Raadzaal', '').replace('Commissiekamer','').replace('Gemeente Eindhoven','')
            span(titel, escape=False, cls='title')
        else:
            titel = m.title.replace('Raadzaal', '').replace('Commissiekamer','').replace('Gemeente Eindhoven','')
            span(titel,cls = 'title')


        if m.meeting_id:
            span(str(m.meeting_id), cls='keywords')
        if m.meeting_subid and room in m.meeting_subid:
            span(str(m.meeting_subid[room]), cls='keywords')
        if m.agenda and room in m.agenda and m.agenda[room]:
            with ul():
                for key in m.agenda[room]:
                    li(m.agenda[room][key]['title'], cls='keywords')

def addSplashScreen(id_):
    div(cls="splash-screen-background", id = id_)

    # Splash content
    with div(cls="splash", id=id_):
        p(b("Beste iRIS gebruiker, "))
        p("Beantwoord deze vraag om te bewijzen dat je menselijk bent:")
        p("Dieren zijn:")
        button('Vrienden', cls="vrienden-btn", id="splash")
        button("Voedsel", cls="voedsel-btn", id="splash")


def addMenu(id_,prefix):
    if not id_:
        id_ = ''
    if not prefix:
        prefix=''

    with div(cls='menu', id=id_):
        a('alle stukken', href=f'{prefix}index.html')
        a('mensen', href=f'{prefix}raad.html')
        a('cijfers', href=f'{prefix}analyse.html')
        a('raadsvoorstellen', href=f'{prefix}raadsvoorstellen.html')
        a('vergaderingen',href=f'{prefix}meetingindex.html')

def makeDivForAd(value):
    if value==1:
        ad_div = div(_class="blinking-ad adpanel")
        with ad_div:
            a(href="https://www.worldwithoutfossilads.org/projects/", target="_blank").add(
                img(src="fft.gif", alt="Ad")
            )
    else:

        ad_div = div(_class="slachthuis-ad adpanel")
        with ad_div:
            # Link wrapping the GIF
            a(href="https://www.youtube.com/watch?v=a73mPIf2-f4", target="_blank", _class="gif-link").add(
                img(src="ads/slachthuisgif.gif", alt="Ad", _class="ad-gif")
            )

            # Garage door static image
            img(src='ads/deur.png', alt="Garage Door", _class="ad-door")


def makeDivForModule(m,id_,cls_,doc=None):
    print(m.module_id)
    if not m.type:
        return

    if 'master' in id_:
        hiddenclass = ''
    else:
        hiddenclass = 'hidden-content'

    with div(id=id_,cls=f'{cls_} panel',data_id = m.module_id) as d:
        with div(cls='close-container'):
            with div(cls='fav'):
                # Use the class 'star-icon'
                span('☆', cls='star-icon')
            button('X', cls='close-button', id='closeButton')


        #--- Title bar

        if m.date and not 'indexpage' in cls_:
            span(convert_date_to_dutch(m.date),cls='date')

        if 'brief' in m.type:
            new_class = 'brief'
            a(span(m.type, cls=f'type {new_class}'), href=f'{m.module_id}.html',target="_blank")
        elif m.result:
            result = m.result.replace(' ','').lower()
            new_class = result
            a(span(f'{m.type} ({m.result})', cls=f'type {result}'),href=f'{m.module_id}.html',target="_blank")
        elif m.type.lower() == 'toezegging':
            new_class = 'toezegging'
            a(span(m.type, cls='type toezegging'),href=f'{m.module_id}.html',target="_blank")
        elif 'motie' in m.type.lower() and not m.vote_id and not m.result:
            new_class = 'ingetrokken'
            a(span(f'{m.type} (ingetrokken zonder toezegging?)', cls=f'type ingetrokken'), href=f'{m.module_id}.html',target="_blank")
        elif 'raadsvoorstel' in m.type.lower():
            new_class = 'raadsvoorstel'
            a(span(m.type, cls='type raadsvoorstel'), href=f'{m.module_id}.html',target="_blank")
        elif 'raadsvraag' in m.type.lower():
            new_class = 'raadsvraag'
            a(span(m.type, cls='type raadsvraag'), href=f'{m.module_id}.html',target="_blank")

        else:
            new_class = 'unknown'
            a(span(m.type, cls='type unknown'), href=f'{m.module_id}.html',target="_blank")


        existing_class = d['class']
        #d.set_attribute('class',f'{existing_class} {new_class}')






        if m.title:
            titel = m.title.replace('Raadsvoorstel', '').replace('Collegebrief','').replace('Raadsinformatiebrief','').replace('Burgemeesterbrief','').replace('aan de raad over','').replace('aan de leden van de raad over','').replace('Beantwoording raadsvragen -','').replace('Ingekomen raadsvragen -','').replace('Beantwoording raadsvragen','').replace('Ingekomen Raadsvragen -','').replace('Ingekomen vervolg raadsvragen -','')
            if not 'estemmingsplan' in titel and '(' in titel and ')' in titel.split('(')[1]:
                texta = titel.split('(')[0] or ''
                textb = titel.split(')')[1] or ''
                titel = f'{texta} {textb}'
            span(raw(fancy(titel)), escape=False, cls='title')

        if 'gewijzigd' in id_:
            a(span('Door de raad gewijzigd'), href=f'{m.module_id}.html', target="_blank",cls='gewijzigd')


        #-- links
        with div(cls=f'links {hiddenclass}'):
            span('Ga naar: ')
            if m.meeting_url:
                a(span('Meeting'),href=m.getMeetingUrl(), target='_blank')
            if m.pdf_url:
                a(span('PDF'),href=m.pdf_url, target='_blank')
            if m.url:
                a(span('RIS'),href=m.url, target='_blank')

        if 'master' in id_:
            if m.videolink:

                with video(id ='raadsvergaderingvideo',cls ="video-js vjs-default-skin", width="640", height="360", controls=True, data_setup='{ "playbackRates": [0.5, 1, 1.5, 2] }'):
                        source(type="application/x-mpegURL",src = m.chooseVideolink()) #'https://wowza1.notubiz.nl/nbvod/_definst_/Eindhoven/bestanden/26.11.24%20Eindhoven%20RaadV2.mp4/playlist.m3u8')
                with div(style="text-align: center;"):  # Add container to center the link
                    a('Spring naar het juiste moment', id='jump-link', href="#")


        #-- Render
        card_id = m.module_id


        with div(cls='card-container', id=f'card-{card_id}'):
            div(id=f'vote-details-{card_id}', cls='content-placeholder vote-placeholder')
            div(id=f'keywords-details-{card_id}', cls='content-placeholder keywords-placeholder')


        if 1:
            #--- Stemming

            if m.vote_id:
                votecontainer = makeDivForVote(Vote(m.vote_id))
                if id_=='master':
                    votecontainer['class'] = ''
                    votecontainer.children[0]['class'] = ''


            #-- Keywords
            if m.keywords:
                words = [w.lower() for w in m.keywords]
                span(' '.join(words),cls='keywords')


        #-- Poho
        if m.poho_id:
            h3('Portefeuillehouder:', cls=hiddenclass)
            poho = Member(m.poho_id)
            with div(cls='wrapper', id='photos'):
                with div(cls=f"member {hiddenclass}"):
                    img(src=poho.img, alt=f"{poho.name}'s photo",loading="lazy")
                    with div(id='textwrap'):
                        a(poho.name,href=poho.url, cls="member-name",target="_blank")



        #--- Indieners
        if m.member_id:
            h3('Indieners:',cls = hiddenclass)

            with div(cls='wrapper', id='photos'):
                eerste = None
                if m.eersteIndiener:
                    eerste = Member(m.eersteIndiener)
                    try:
                        party_color = eerste.get_party().color
                    except:
                        party_color = '#888888'
                    with div(cls=f'photo-container member {hiddenclass}'):
                        div(style=f'background-color:{party_color};', cls='photo-backgroundcolor')
                        a(img(src=eerste.img, alt=f"{eerste.name}'s photo", id='index-foto', partij=eerste.party, loading="lazy"),
                          href=f'{eerste.person_id}.html', style='margin:0;')
                        a(span(f"{eerste.name} ({eerste.party})", cls='photo-info',
                               style=f'background-color:{party_color};'), href=f'{eerste.person_id}.html', style='margin:0;')

                   # with div(cls=f"member {hiddenclass}"):
                   #     img(src=eerste.img, alt=f"{eerste.name}'s photo")
                    #    with div(id='textwrap'):
                     #      a(eerste.name, href=f'{eerste.person_id}.html', cls="member-name")


                for indiener in m.member_id:
                    persoon = Member(indiener)
                    try:
                        party_color = persoon.get_party().color
                    except:
                        party_color = '#888888'
                    if eerste is not None and persoon == eerste:
                        continue
                    with div(cls=f'photo-container member {hiddenclass}'):
                        div(style=f'background-color:{party_color};', cls='photo-backgroundcolor')
                        a(img(src=persoon.img, alt=f"{persoon.name}'s photo", id='index-foto', partij=persoon.party,loading="lazy"),
                          href=f'{persoon.person_id}.html', style='margin:0;')
                        a(span(f"{persoon.name} ({persoon.party})", cls='photo-info',
                               style=f'background-color:{party_color};'), href=f'{persoon.person_id}.html',
                          style='margin:0;')


        # --- Toezegging
        if m.text:
            h3('Toezegging:',cls=hiddenclass)
            with div(cls=f'scrollable {hiddenclass}'):
                p(m.text, id='larger')

        if 0 and m.keywords and 'Raadsvraag' in m.type:
            h3('Wat sleutelwoorden:',cls=hiddenclass)
            with ol(cls = hiddenclass, id='kwlist') as o:
                n_kw = 0
                for kw in m.keywords:
                    if 'raad' in kw.lower() or 'fractie' in kw.lower() or 'namens' in kw.lower() or 'inleiding' in kw.lower() or 'college' in kw.lower() or 'inboeknummer' in kw.lower() or 'vraag' in kw.lower() or 'eindhoven' in kw.lower() or 'datum' in kw.lower() or 'geacht' in kw.lower():
                        continue

                    if m.keywords[kw]<1:
                        n_kw = n_kw+1
                        li(kw)
                        if n_kw ==10:
                            break



        #-- Inhoud
        getInhoudFromPDF(m)
        #with div(cls='card-container', id=f'card-{card_id}'):
        #    div(id=f'inhoud-details-{card_id}', cls='content-placeholder inhoud-placeholder')




        if m.attachment:
            h3('Bijlages:', cls=hiddenclass)
            with div(cls=f'scrollable {hiddenclass}'):
                with ul(cls='attachments'):
                    if isinstance(m.attachment,dict):
                        for att in m.attachment:
                            if m.attachment[att]=='main':
                                m.attachment[att] = 'Hoofddocument'
                            li(
                                img(src="pdf-icon.png", alt="PDF Icon", width="17", height="22", cls='pdf-icon'),
                                a(m.attachment[att],href=att, target='_blank'))
                    else:
                        li(
                            img(src="pdf-icon.png", alt="PDF Icon", width="17", height="22", cls='pdf-icon'),
                            a('document', href=m.attachment, target='_blank'))
        elif m.pdf_url:
            h3('Bijlages:', cls=hiddenclass)
            with div(cls=f'scrollable {hiddenclass}'):
                with ul(cls='attachments'):
                    li(
                        img(src="pdf-icon.png", alt="PDF Icon", width="17", height="22", cls='pdf-icon'),
                        a('Hoofddocument', href=m.pdf_url, target='_blank'))



        if m.lastScrapeDate:
            p(f'Voor het laatst het RIS gecheckt op: {m.lastScrapeDate}', cls = hiddenclass, id='laatstecheck')
        return d


def makeMeetingIndex(mm):
    doc = dominate.document(title="iRIS /meetings ")
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link (rel="stylesheet", href="stylesheetdark.css" )
        link(rel='icon', type='image/png',href='/favicon.png')
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="clickdiv.js")

    with doc.body:
        with div(cls='header', id='header'):
            img(src='Logo iris_dark.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('','')


        with div(cls='search-header'):
            input_(type='search',id='searchbox', placeholder='Plak RIS-vergaderinglink hier...')

        with div(cls='wrapper'):
            #h1('Gerelateerd:')
            n = 0
            current_date = None
            boxes = {}
            for meeting in mm.meetings:
                dutchdate = convert_date_to_dutch(meeting.date)
                if not(dutchdate in boxes):
                    boxes[dutchdate] = new_box(dutchdate)
                with boxes[dutchdate]:
                    if isinstance(meeting.meeting_subid,dict):
                        for room in meeting.meeting_subid:
                            makeDivForMeeting(meeting, 'gerelateerd', 'box collapsible indexpage',room)
                    else:
                        makeDivForMeeting(meeting, 'gerelateerd', 'box collapsible indexpage','Raadzaal')
            script(src="searchMeeting.js")

            a('Terug naar boven', cls="back-to-top", href="#top")

    with open(f'{os.getcwd()}/Presentation/htmls/meetingindex.html', 'w') as f:
        f.write(doc.render())

def makeIndex(mm):
    #for module in mm.modules:
     #   generate_and_save_card_details(module, base_path="")

    doc = dominate.document(title="iRIS")
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link (rel="stylesheet", href="stylesheet.css" )
        script(src="panel-behaviour.js")
        script(src="loader.js")
        script(src="animal.js")
        script(src="splash.js")
        script(src='wordcloud2.js')
        script(src="fav.js")
        #script(src='eager-load-cards.js')
        link(rel='icon', type='image/png',href='/favicon.png')

    with doc.body:
        with div(cls='header full-screen-loader', id='header'):
            #h1('iRIS040',id='top')
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            p('Duurt even...',id='show-during-loading')
            with div(cls='last-update',id='hide-during-loading'):
                p('Laatste RIS check: 26 november 2025')
            addMenu('hide-during-loading2','')

            if 1:
                addSplashScreen('hide-during-loading2')


        div(id="animal-container")
        div(id="bottom-box", content="Er zijn in Nederland inmiddels: 0 kippen, 0 varkens en 0 koeien geslacht.")


        with div(cls='search-header'):
            input_(type='search',id='searchbox', placeholder='Zoek sneller dan het RIS...')
            span('★',cls='filterfavs')

        with div(cls='wrapper'):
            #h1('Gerelateerd:')
            n = 0
            current_date = None
            box = None
            for module in mm.modules:
                if module.type and 'Agenda' in module.type:
                    continue
                n += 1
                #if n>100:
                 #   break

                if n%27==0:
                    with box:
                        makeDivForAd(n%2)



                if not(convert_date_to_dutch(module.date) == current_date):
                    current_date = convert_date_to_dutch(module.date)
                    box = new_box(current_date)
                with box:
                    makeDivForModule(module, 'gerelateerd', 'box collapsible indexpage')
            script(src="search.js")
            a('Terug naar boven', cls="back-to-top", href="#top")

    with open(f'{os.getcwd()}/Presentation/htmls/index.html', 'w') as f:
        f.write(doc.render())

def makeMeetingPage(meeting,room):
    doc = dominate.document(title="iRIS")
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel="stylesheet", href="../stylesheetdark.css")
        script(src="../panel-behaviour.js")
        script(src="../loader.js")
        script(src="../videosync.js")
        script(src="../searchheaderbehaviour.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")

        link(rel='icon', type='image/png', href='../favicon.png')

        if meeting.video_url:
            videolink = meeting.video_url[room].replace('http','https')
        else:
            videolink = ''

        dynamic_script = raw(f"""
            document.addEventListener('DOMContentLoaded', function () {{
                const video = document.getElementById('raadsvergaderingvideo');
                const videoSrc = '{videolink}'; // HLS video URL
                video.addEventListener('loadedmetadata', function () {{
            video.playbackRate = 1.5;
                }});
               

                // Attach click listeners to all subtitle links
                document.querySelectorAll('.jump-link').forEach(link => {{
                    link.addEventListener('click', function (e) {{
                        e.preventDefault(); // Prevent page refresh
                        const timestamp = parseFloat(link.getAttribute('data-timestamp')); // Get timestamp from "data-timestamp"
                        if (!isNaN(timestamp)) {{
                            video.currentTime = timestamp; // Jump to specific timestamp
                            video.play(); // Play the video
                        }} else {{
                            console.warn('Invalid timestamp value:', timestamp);
                        }}
                    }});
                }});

                function setStartTime(startTime) {{
                    // Set the video start time after metadata is loaded
                    if (startTime <= video.duration) {{
                        video.currentTime = startTime;
                    }} else {{
                        console.warn('Start time exceeds video duration.');
                    }}
                }}

                // Check if browser supports native HLS playback
                if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    // Native HLS support
                    video.src = videoSrc;
                    video.addEventListener('loadedmetadata', function () {{
                        const startTime = 0; // Replace with your desired start time if needed
                        setStartTime(startTime);
                    }});
                }} else {{
                    // Use Hls.js for browsers without native HLS support
                    if (Hls.isSupported()) {{
                        const hls = new Hls();
                        hls.loadSource(videoSrc);
                        hls.attachMedia(video);

                        hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                            const startTime = 0; // Replace with your desired start time if needed
                            setStartTime(startTime);
                        }});
                    }} else {{
                        console.error('HLS not supported in this browser.');
                    }}
                }}
            }});
        """)

        script(dynamic_script, type="text/javascript")




    with doc.body:

        with div(cls='header', id='header'):
            img(src='../Logo iris_dark.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('','../')



        with div(cls='search-header'):
            input_(type='search', id='searchbox', placeholder='Doorzoek raadsvoorstellen...')


        with div(cls='wrapper'):
            risurl = f'https://raadsinformatie.eindhoven.nl/vergadering/{meeting.meeting_subid[room]}'
            div(
                button("Ga naar RIS", onclick=f"window.location.href='{risurl}';"),
                _class="fixed-button-container"
            )
            with div(id = 'stickyvideo'):
                with video(id='raadsvergaderingvideo', cls="video-js vjs-default-skin", width="640", height="360",
                           controls=True, data_setup='{ "playbackRates": [1, 1.25, 1.5, 2] }'):
                    source(type="application/x-mpegURL",
                           src=videolink)  # 'https://wowza1.notubiz.nl/nbvod/_definst_/Eindhoven/bestanden/26.11.24%20Eindhoven%20RaadV2.mp4/playlist.m3u8')
                if meeting.speakers and room in meeting.speakers:
                    for timestamp in meeting.speakers[room]:
                        if meeting.speakers[room][timestamp].id is None:
                            continue
                        speaker = Member(meeting.speakers[room][timestamp].id)
                        #module = Module(1051065)

                        # Speaker box
                        with div(id='info-container'):
                            with div(id='speakingbox'):
                                h1('Vind meer info over:')
                                with div(id='speaker-container'):
                                    img(src=speaker.img, alt=f"{speaker.name}'s photo", id='speaker-photo')
                                    with div(id='speaker-info'):
                                        a(speaker.name, href=f'{speaker.person_id}.html', id='speaker-name')
                                        if speaker.party:
                                            span(speaker.party, id='speaker-party')
                                        else:
                                            span('no party', id='speaker-party')

                            # Topic box
                            with div(id='subjectbox'):
                                h1('Onderwerp:')
                                with div(id='subject-container'):
                                    img(src='', alt = 'foto wethouder',
                                        id='subject-poho')
                                    with div(id='subject-info'):
                                        a('agenda', href='', id='subject-title')


                        break

            with div(id='link-container',cls='wrapper-no-margin', style='max-width:800px; margin:auto;'):
                color = '#444444'
                highlight = color
                if meeting.subtitles and room in meeting.subtitles and meeting.subtitles[room]:
                    for time in range(1,int(list(meeting.subtitles[room].keys())[-1])):
                        timestr = str(time)
                        if 0:
                            if timestr in subs.speaker:
                                speaker = subs.speaker[timestr].speaker_id
                                if Member(speaker).role and not ('Wethouder'  in Member(speaker).role or 'Burgemeester' in Member(speaker).role):
                                    color = Member(speaker).get_party().color
                                else:
                                    if Member(speaker).name and 'Burgemeester' in Member(speaker).name:
                                        color = '#888888'
                                    else:
                                        color = 'black'
                        if timestr in meeting.subtitles[room]:
                            person =  meeting.speaking(timestr,room)
                            if person:
                                party = person.get_party()
                                if party:
                                    color = party.color
                                    name = person.name
                                    party = f'{person.role} {party.id}'
                                    imgurl = person.img
                                    memberid = person.person_id
                                    highlight = color
                                else:
                                    #print(f'unknown person at: {timestr}')
                                    color = '#444444'
                                    party = 'unknown'
                                    name = person.name
                                    memberid = ''
                                    imgurl = '../missingphoto.png'
                                    highlight = color
                                if person.role and 'wethouder' in person.role.lower():
                                    color = '#222222'
                                    highlight = '#cccccc'
                                if person.role and 'burgeme' in person.role.lower():
                                    color = '#000'
                                    highlight = '#fff'

                            else:
                                party = 'unknown'
                                name = 'unknown'
                                imgurl = '../missingphoto.png'
                                memberid = ''
                                #print(f'unkwown person at: {timestr}')
                            text = meeting.subtitles[room][timestr]
                            timestamp = int(timestr)
                            try:
                                a(text,style=f'background-color:{color};',cls='jump-link', href="#", data_timestamp=timestamp,data_speaker = name, data_party = party,data_color = highlight,data_photo = imgurl, data_memberid = memberid)
                            except:
                                print('debug')
                        if timestr in meeting.agenda[room]:
                            agenda = meeting.agenda[room][timestr]['title']
                            mod_id = meeting.agenda[room][timestr]['module_id']
                            if mod_id:
                                if len(mod_id)>1:
                                    parentmodule = Module(mod_id[0]).parent
                                    if parentmodule:
                                        module_id = parentmodule
                                    else:
                                        module_id = mod_id[0]
                                else:
                                    module_id = mod_id[0]
                            else:
                                module_id = []

                            photolink = '../missingphoto.png'
                            if module_id:
                                thisMod = Module(module_id)
                                img_ = Member(thisMod.poho_id).img
                                if img_:
                                    photolink = img_


                            timestamp = int(timestr)

                            a(f'AGENDA: {agenda}', style='background-color:#fff; color:#000', cls='jump-link', id='ai', href="#", data_timestamp=timestamp, data_moduleid = module_id, data_photo = photolink, data_title = agenda, data_speaker='agenda')


        script(src="../searchsubinpage.js")
    if meeting.meeting_subid:
        id = meeting.meeting_subid[room]
    else:
        id = meeting.meeting_id
    with open(f'{os.getcwd()}/Presentation/htmls/vergadering/{id}.html', 'w') as f:
        f.write(doc.render())




def makeRaadsvoorstelPage(mm):
    doc = dominate.document(title="iRIS")
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel="stylesheet", href="stylesheet.css")
        script(src="panel-behaviour.js")
        script(src="loader.js")
        script(src='wordcloud2.js')
        link(rel='icon', type='image/png', href='/favicon.png')

    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')
            #with div(cls='menu'):
            #    a('alle stukken', href='index.html')
            #    a('mensen', href='raad.html')
            #    a('cijfers', href='analyse.html')
            #    a('raadsvoorstellen', href='raadsvoorstellen.html')

        with div(cls='search-header'):
            input_(type='search', id='searchbox', placeholder='Doorzoek raadsvoorstellen...')

        with div(cls='wrapper'):

            boxes = {}
            for perc in range(0,101,10):
                boxes[perc] = new_box(f'{perc}% steun')
            boxes[None] = new_box('geen stemming')

            for module in mm.modules:
                if module.type != 'Raadsvoorstel':
                    continue

                #Check of er een amendement is aangenomen:
                gewijzigd = ''
                if module.children:
                    for child in module.children:
                        if Module(child).type == 'Amendement':
                            if Module(child).result == 'aangenomen':
                                gewijzigd = 'gewijzigd'
                                break

                #Maak de paneeltjes:
                if not module.vote_id:
                    with boxes[None]:
                        makeDivForModule(module, f'gerelateerd {gewijzigd}', 'box collapsible')
                        continue
                perc = math.floor(Vote(module.vote_id).get_percentage()/10)*10
                with boxes[perc]:
                    makeDivForModule(module, f'gerelateerd {gewijzigd}', 'box collapsible')
            script(src="search.js")
            a('Terug naar boven', cls="back-to-top", href="#top")

    with open(f'{os.getcwd()}/Presentation/htmls/raadsvoorstellen.html', 'w') as f:
        f.write(doc.render())


def makeMemberIndex(members):
    doc = dominate.document(title=f'iRIS // de Raad')
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet', href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")

        script(src="https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")

    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')

        with div(cls='search-header'):
            input_(type='search',id='searchbox', placeholder=f'Zoek op naam of op partij...')

        with div(cls='wrapper', id='photos'):
            for member in members:
                if member.startswith('.'):
                    continue
                m = Member(member)
                if m is None:
                    continue
                if not hasattr(m, 'active'):
                    continue
                if not m.active:
                    continue
                if not m.img:
                    m.img = 'missingphoto.png'
                with div(cls='photo-container'):
                    party_color = m.get_party().color
                    div(style=f'background-color:{party_color};',cls='photo-backgroundcolor')
                    a(img(src=m.img, alt=f"{m.name}'s photo", id='index-foto',partij=m.party),href=f'{m.person_id}.html',style='margin:0;')
                    a(span(f"{m.name} ({m.role} {m.party})", cls='photo-info',style=f'background-color:{party_color};'),href=f'{m.person_id}.html',style='margin:0;')

        script(src="search.js")
    with open(f'{os.getcwd()}/Presentation/htmls/raad.html', 'w') as f:
        f.write(doc.render())





def makeMemberPage(member, mm):
    doc = dominate.document(title=f'iRIS // {member.name}')
    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet',href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")

        script( src=  "https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")


    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')

        with div(cls='search-header'):
            input_(type='search',id='searchbox', placeholder=f'Doorzoek de pagina van {member.name}...')


        with div(cls='wrapper', id='photos'):
            h1(f'{member.name}')
            p(f'{member.role} voor {member.party}')
        with div(cls='wrapper', id='photos'):
            img(src=member.img, alt=f"{member.name}'s photo", id='grote-foto')





        with div(cls='wrapper'):
            motie_titel = h1('Eerste indiener van XX moties',id='purpletext')

            N =0
            for m in mm.modules:
                if m.type and 'motie' in m.type.lower() and  m.eersteIndiener and int(m.eersteIndiener) == int(member.person_id):
                    makeDivForModule(m, 'gerelateerd', 'box collapsible')
                    if m.get_date() > date(2022,4,22):
                        N = N + 1
            motie_titel[0] = motie_titel[0].replace('XX',str(N))

        with div(cls='wrapper'):
            amendement_titel = h1('Eerste indiener van XX amendementen',id='purpletext')
            N = 0
            for m in mm.modules:
                if 'Amendement' == m.type and m.eersteIndiener  and int(m.eersteIndiener) == int(member.person_id):
                    makeDivForModule(m, 'gerelateerd', 'box collapsible')
                    if m.get_date() > date(2022, 4, 22):
                        N = N + 1
            amendement_titel[0] = amendement_titel[0].replace('XX',str(N))

        with div(cls='wrapper'):
            vragen_titel = h1('Indiener van XX raadsvragen',id='purpletext')
            N = 0
            for m in mm.modules:
                if 'Raadsvraag' == m.type:
                    if member.name in m.member:
                        makeDivForModule(m, 'gerelateerd', 'box collapsible')
                        if m.get_date() > date(2022, 4, 22):
                            N = N+1
            vragen_titel[0] = vragen_titel[0].replace('XX',str(N))

        script(src="search.js")
    with open(f'{os.getcwd()}/Presentation/htmls/{member.person_id}.html', 'w') as f:
        f.write(doc.render())

def makeAnalysisPagePartij(mm,partijnaam):
    doc = dominate.document(title=f'iRIS // Analyse')

    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet', href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")

        script(src="https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")

        script(raw("""
                       function toggleDataMode() {
                           const containers = document.querySelectorAll('.bar-container');
                           containers.forEach(container => {
                               const segments = container.querySelectorAll('.bar-segment');
                               segments.forEach(segment => {
                                   const label = segment.querySelector('span');
                                   const percentageValue = segment.getAttribute('data-percentage');
                                   const absoluteValue = segment.getAttribute('data-absolute');
                                   const scaling = segment.getAttribute('scaling')

                                   if (segment.dataset.mode === 'percentage') {
                                       segment.style.width = absoluteValue*scaling + "px";
                                       label.textContent = absoluteValue;
                                       segment.dataset.mode = 'absolute';
                                   } else {
                                       segment.style.width = percentageValue + "%";
                                       label.textContent = percentageValue + "%";
                                       segment.dataset.mode = 'percentage';
                                   }
                               });
                           });
                       }
                   """), type="text/javascript")

    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')
            # with div(cls = 'menu'):
            #    anchor('alle stukken',href='index.html')
            #    anchor('mensen',href='raad.html')
            #    anchor('cijfers',href='analyse.html')
            #    anchor('raadsvoorstellen', href='raadsvoorstellen.html')

        with div():
            analysis = partij_analyse_per_partij(mm,partijnaam)
            all_parties = ['coalitie', 'oppositie', 'GroenLinks', 'CDA', 'PvdA', 'D66', 'VVD', 'SP', 'Volt',
                           ' Ouderen Appèl - Hart voor Eindhoven', 'Partij voor de Dieren', '50PLUS', 'LPF ', 'FVD']

            with div(cls='chart'):

                h1(f'Moties van {partijnaam}')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Motie'][partij]['gemengd']) or 0
                        b = len(analysis['Motie'][partij]['voor']) or 0
                        c = len(analysis['Motie'][partij]['tegen']) or 0
                        totaal = a_ + b + c

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij, cls='party-name')
                        SCALING = 2.5
                        with div(cls='bar-container'):
                            if a_:
                                with div(cls='bar-segment graph_toezegging', data_percentage=round(a_ / totaal * 100),
                                         data_absolute=a_,
                                         style=f'width: {round(a_ / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_gemengd'):
                                    span(f'{round(a_ / totaal * 100)}%')
                            if b:
                                with div(cls='bar-segment graph_aangenomen', data_percentage=round(b / totaal * 100),
                                         data_absolute=b,
                                         style=f'width: {round(b / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_voor'):
                                    span(f'{round(b / totaal * 100)}%')
                            if c:
                                with div(cls='bar-segment graph_verworpen', data_percentage=round(c / totaal * 100),
                                         data_absolute=c,
                                         style=f'width: {round(c / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_tegen'):
                                    span(f'{round(c / totaal * 100)}%')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    span('Gemengd of afwezig', cls='graph_toezegging',
                         style='margin:10px;padding:2px;color:white;')
                    span('Voor', cls='graph_aangenomen', style='margin:10px;padding:2px;color:white;')
                    span('Tegen', cls='graph_verworpen', style='margin:10px;padding:2px;color:white;')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                           cls="toggle-link")

            for partij in analysis['Motie']:
                for result in analysis['Motie'][partij]:
                    if not partij:
                        continue
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij

                    with div(cls='hidden-content', id=f'motie_{partij_}_{result}'):  # 'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Motie'][partij][result]:
                                makeDivForModule(Module(module_id), 'gerelateerd', 'box collapsible')
            ####
            with div(cls='chart'):
                h1(f'Amendementen van {partijnaam}')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Amendement'][partij]['gemengd']) or 0
                        b = len(analysis['Amendement'][partij]['voor']) or 0
                        c = len(analysis['Amendement'][partij]['tegen']) or 0

                        totaal = a_ + b + c
                        if not totaal:
                            continue

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij, cls='party-name')
                        SCALING = 7
                        with div(cls='bar-container'):
                            with div(cls='bar-segment graph_toezegging', data_percentage=round(a_ / totaal * 100),
                                     data_absolute=a_,
                                     style=f'width: {round(a_ / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_gemengd'):
                                span(f'{round(b / totaal * 100)}%')

                            with div(cls='bar-segment graph_aangenomen', data_percentage=round(b / totaal * 100),
                                     data_absolute=b,
                                     style=f'width: {round(b / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_voor'):
                                span(f'{round(b / totaal * 100)}%')
                            with div(cls='bar-segment graph_verworpen', data_percentage=round(c / totaal * 100),
                                     data_absolute=c,
                                     style=f'width: {round(c / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_tegen'):
                                span(f'{round(c / totaal * 100)}%')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    span('Gemengd of afwezig', cls='graph_toezegging', style='margin:10px;padding:2px;color:white;')
                    span('Aangenomen', cls='graph_aangenomen', style='margin:10px;padding:2px;color:white;')
                    span('Verworpen', cls='graph_verworpen', style='margin:10px;padding:2px;color:white;')
                    span('*Ingetrokken amendementen zijn onvindbaar')
                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                           cls="toggle-link")

            for partij in analysis['Amendement']:
                for result in analysis['Amendement'][partij]:
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij

                    with div(cls='hidden-content', id=f'amendement_{partij_}_{result}'):  # 'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Amendement'][partij][result]:
                                makeDivForModule(Module(module_id), 'gerelateerd', 'box collapsible')

            if 0:
                for partij in all_parties:
                    h1(partij)
                    a = len(analysis['Motie'][partij]['ingetrokken na toezegging']) or 0
                    b = len(analysis['Motie'][partij]['aangenomen']) or 0
                    c = len(analysis['Motie'][partij]['verworpen']) or 0
                    d = len(analysis['Motie'][partij]['ingetrokken']) or 0
                    totaal = a + b + c + d

                    with ul():
                        if totaal:
                            li(f'Ingetrokken met toezegging: {round(a / totaal * 100)}%')
                            li(f'Aangenomen: {round(b / totaal * 100)}%')
                            li(f'Verworpen: {round(c / totaal * 100)}%')
                            li(f'Ingetrokken: {round(d / totaal * 100)}%')
                            li(f'Totaal: {totaal}')

    partijnaamgeenspatie = partijnaam.replace(' ','')
    with open(f'{os.getcwd()}/Presentation/htmls/analyse_{partijnaamgeenspatie}.html', 'w') as f:
        f.write(doc.render())



def makeAnalysisPagePvdD(mm):
    doc = dominate.document(title=f'iRIS // Analyse')

    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet', href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")

        script(src="https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")

        script(raw("""
                       function toggleDataMode() {
                           const containers = document.querySelectorAll('.bar-container');
                           containers.forEach(container => {
                               const segments = container.querySelectorAll('.bar-segment');
                               segments.forEach(segment => {
                                   const label = segment.querySelector('span');
                                   const percentageValue = segment.getAttribute('data-percentage');
                                   const absoluteValue = segment.getAttribute('data-absolute');
                                   const scaling = segment.getAttribute('scaling')

                                   if (segment.dataset.mode === 'percentage') {
                                       segment.style.width = absoluteValue*scaling + "px";
                                       label.textContent = absoluteValue;
                                       segment.dataset.mode = 'absolute';
                                   } else {
                                       segment.style.width = percentageValue + "%";
                                       label.textContent = percentageValue + "%";
                                       segment.dataset.mode = 'percentage';
                                   }
                               });
                           });
                       }
                   """), type="text/javascript")

    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')
            # with div(cls = 'menu'):
            #    anchor('alle stukken',href='index.html')
            #    anchor('mensen',href='raad.html')
            #    anchor('cijfers',href='analyse.html')
            #    anchor('raadsvoorstellen', href='raadsvoorstellen.html')

        with div():
            analysis = partij_analyse_per_partij(mm,'Dieren')
            all_parties = ['coalitie', 'oppositie', 'GroenLinks', 'CDA', 'PvdA', 'D66', 'VVD', 'SP', 'Volt',
                           ' Ouderen Appèl - Hart voor Eindhoven', 'Partij voor de Dieren', '50PLUS', 'LPF ', 'FVD']

            with div(cls='chart'):
                h1('Moties')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Motie'][partij]['gemengd']) or 0
                        b = len(analysis['Motie'][partij]['voor']) or 0
                        c = len(analysis['Motie'][partij]['tegen']) or 0
                        totaal = a_ + b + c

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij, cls='party-name')
                        SCALING = 2.5
                        with div(cls='bar-container'):
                            if a_:
                                with div(cls='bar-segment graph_toezegging', data_percentage=round(a_ / totaal * 100),
                                         data_absolute=a_,
                                         style=f'width: {round(a_ / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_gemengd'):
                                    span(f'{round(a_ / totaal * 100)}%')
                            if b:
                                with div(cls='bar-segment graph_aangenomen', data_percentage=round(b / totaal * 100),
                                         data_absolute=b,
                                         style=f'width: {round(b / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_voor'):
                                    span(f'{round(b / totaal * 100)}%')
                            if c:
                                with div(cls='bar-segment graph_verworpen', data_percentage=round(c / totaal * 100),
                                         data_absolute=c,
                                         style=f'width: {round(c / totaal * 100)}%;',
                                         data_mode="percentage",
                                         scaling=SCALING,
                                         id=f'motie_{partij}_tegen'):
                                    span(f'{round(c / totaal * 100)}%')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    span('Gemengd of afwezig', cls='graph_toezegging',
                         style='margin:10px;padding:2px;color:white;')
                    span('Voor', cls='graph_aangenomen', style='margin:10px;padding:2px;color:white;')
                    span('Tegen', cls='graph_verworpen', style='margin:10px;padding:2px;color:white;')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                           cls="toggle-link")

            for partij in analysis['Motie']:
                for result in analysis['Motie'][partij]:
                    if not partij:
                        continue
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij

                    with div(cls='hidden-content', id=f'motie_{partij_}_{result}'):  # 'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Motie'][partij][result]:
                                makeDivForModule(Module(module_id), 'gerelateerd', 'box collapsible')
            ####
            with div(cls='chart'):
                h1('Amendementen')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Amendement'][partij]['gemengd']) or 0
                        b = len(analysis['Amendement'][partij]['voor']) or 0
                        c = len(analysis['Amendement'][partij]['tegen']) or 0

                        totaal = a_ + b + c
                        if not totaal:
                            continue

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij, cls='party-name')
                        SCALING = 7
                        with div(cls='bar-container'):
                            with div(cls='bar-segment graph_toezegging', data_percentage=round(a_ / totaal * 100),
                                     data_absolute=a_,
                                     style=f'width: {round(a_ / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_gemengd'):
                                span(f'{round(b / totaal * 100)}%')

                            with div(cls='bar-segment graph_aangenomen', data_percentage=round(b / totaal * 100),
                                     data_absolute=b,
                                     style=f'width: {round(b / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_voor'):
                                span(f'{round(b / totaal * 100)}%')
                            with div(cls='bar-segment graph_verworpen', data_percentage=round(c / totaal * 100),
                                     data_absolute=c,
                                     style=f'width: {round(c / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_tegen'):
                                span(f'{round(c / totaal * 100)}%')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    span('Gemengd of afwezig', cls='graph_toezegging', style='margin:10px;padding:2px;color:white;')
                    span('Aangenomen', cls='graph_aangenomen', style='margin:10px;padding:2px;color:white;')
                    span('Verworpen', cls='graph_verworpen', style='margin:10px;padding:2px;color:white;')
                    span('*Ingetrokken amendementen zijn onvindbaar')
                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                           cls="toggle-link")

            for partij in analysis['Amendement']:
                for result in analysis['Amendement'][partij]:
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij

                    with div(cls='hidden-content', id=f'amendement_{partij_}_{result}'):  # 'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Amendement'][partij][result]:
                                makeDivForModule(Module(module_id), 'gerelateerd', 'box collapsible')

            if 0:
                for partij in all_parties:
                    h1(partij)
                    a = len(analysis['Motie'][partij]['ingetrokken na toezegging']) or 0
                    b = len(analysis['Motie'][partij]['aangenomen']) or 0
                    c = len(analysis['Motie'][partij]['verworpen']) or 0
                    d = len(analysis['Motie'][partij]['ingetrokken']) or 0
                    totaal = a + b + c + d

                    with ul():
                        if totaal:
                            li(f'Ingetrokken met toezegging: {round(a / totaal * 100)}%')
                            li(f'Aangenomen: {round(b / totaal * 100)}%')
                            li(f'Verworpen: {round(c / totaal * 100)}%')
                            li(f'Ingetrokken: {round(d / totaal * 100)}%')
                            li(f'Totaal: {totaal}')

    with open(f'{os.getcwd()}/Presentation/htmls/analysePvdD.html', 'w') as f:
        f.write(doc.render())


def makeAnalysisPage(mm):
    doc = dominate.document(title=f'iRIS // Analyse')

    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet', href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")

        script(src="https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")

        script(raw("""
                    function toggleDataMode() {
                        const containers = document.querySelectorAll('.bar-container');
                        containers.forEach(container => {
                            const segments = container.querySelectorAll('.bar-segment');
                            segments.forEach(segment => {
                                const label = segment.querySelector('span');
                                const percentageValue = segment.getAttribute('data-percentage');
                                const absoluteValue = segment.getAttribute('data-absolute');
                                const scaling = segment.getAttribute('scaling')

                                if (segment.dataset.mode === 'percentage') {
                                    segment.style.width = absoluteValue*scaling + "px";
                                    label.textContent = absoluteValue;
                                    segment.dataset.mode = 'absolute';
                                } else {
                                    segment.style.width = percentageValue + "%";
                                    label.textContent = percentageValue + "%";
                                    segment.dataset.mode = 'percentage';
                                }
                            });
                        });
                    }
                """),type="text/javascript")

    with doc.body:
        with div(cls='header', id='header'):
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')
            #with div(cls = 'menu'):
            #    anchor('alle stukken',href='index.html')
            #    anchor('mensen',href='raad.html')
            #    anchor('cijfers',href='analyse.html')
            #    anchor('raadsvoorstellen', href='raadsvoorstellen.html')


        with div():
            analysis = partij_analyse(mm)
            all_parties = ['coalitie','oppositie','GroenLinks','CDA','PvdA','D66','VVD','SP','Volt',' Ouderen Appèl - Hart voor Eindhoven','Partij voor de Dieren','50PLUS','LPF ','FVD']

            with div(cls='chart'):
                h1('Moties')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Motie'][partij]['toezegging']) or 0
                        b = len(analysis['Motie'][partij]['aangenomen']) or 0
                        c = len(analysis['Motie'][partij]['verworpen']) or 0
                        d = len(analysis['Motie'][partij]['ingetrokken']) or 0
                        totaal = a_ + b + c + d

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij,cls='party-name')
                        SCALING = 2
                        with div(cls='bar-container'):
                            if a_:
                                with div(cls = 'bar-segment graph_toezegging',data_percentage=round(a_ / totaal * 100),
                                             data_absolute=a_,
                                             style=f'width: {round(a_ / totaal * 100)}%;',
                                             data_mode="percentage",
                                             scaling = SCALING,
                                            id=f'motie_{partij}_toezegging'):
                                    span(f'{round(a_/totaal*100)}%')
                            if b:
                                with div(cls = 'bar-segment graph_aangenomen',data_percentage=round(b / totaal * 100),
                                             data_absolute=b,
                                             style=f'width: {round(b / totaal * 100)}%;',
                                             data_mode="percentage",
                                            scaling=SCALING,
                                             id=f'motie_{partij}_aangenomen'):
                                    span(f'{round(b/totaal*100)}%')
                            if c:
                                with div(cls = 'bar-segment graph_verworpen',data_percentage=round(c / totaal * 100),
                                             data_absolute=c,
                                             style=f'width: {round(c / totaal * 100)}%;',
                                             data_mode="percentage",
                                            scaling = SCALING,
                                            id = f'motie_{partij}_verworpen'):

                                    span(f'{round(c/totaal*100)}%')
                            if d:
                                with div(cls = 'bar-segment graph_ingetrokken',data_percentage=round(d / totaal * 100),
                                             data_absolute=d,
                                             style=f'width: {round(d / totaal * 100)}%;',
                                             data_mode="percentage",
                                             scaling = SCALING,
                                            id = f'motie_{partij}_ingetrokken'):

                                    span(f'{round(d/totaal*100)}%')
                with div(cls='row',style='padding-top:10px; justify-content:center;'):
                    span('Ingetrokken met toezegging',cls='graph_toezegging',style='margin:10px;padding:2px;color:white;')
                    span('Aangenomen', cls='graph_aangenomen',style='margin:10px;padding:2px;color:white;')
                    span('Verworpen', cls='graph_verworpen',style='margin:10px;padding:2px;color:white;')
                    span('Ingetrokken', cls='graph_ingetrokken',style='margin:10px;padding:2px;color:white;')
                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                       cls="toggle-link")

            for partij in analysis['Motie']:
                for result in analysis['Motie'][partij]:
                    if not partij:
                        continue
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij


                    with div(cls='hidden-content', id=f'motie_{partij_}_{result}'):#'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Motie'][partij][result]:
                                makeDivForModule(Module(module_id),'gerelateerd','box collapsible')
           ####
            with div(cls='chart'):
                h1('Amendementen')
                for partij in all_parties:
                    print(partij)
                    with div(cls='row'):
                        a_ = len(analysis['Amendement'][partij]['toezegging']) or 0
                        b = len(analysis['Amendement'][partij]['aangenomen']) or 0
                        c = len(analysis['Amendement'][partij]['verworpen']) or 0
                        d = len(analysis['Amendement'][partij]['ingetrokken']) or 0
                        totaal = a_ + b + c + d
                        if not totaal:
                            continue

                        if 'Dieren' in partij:
                            partij = 'PvdD'
                        elif 'Ouderen' in partij:
                            partij = 'OAHvE'
                        elif 'LPF' in partij:
                            partij = 'LPF'
                        div(partij, cls='party-name')
                        SCALING = 5
                        with div(cls='bar-container'):

                            with div(cls='bar-segment graph_aangenomen', data_percentage=round(b / totaal * 100),
                                     data_absolute=b,
                                     style=f'width: {round(b / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_aangenomen'):
                                span(f'{round(b / totaal * 100)}%')
                            with div(cls='bar-segment graph_verworpen', data_percentage=round(c / totaal * 100),
                                     data_absolute=c,
                                     style=f'width: {round(c / totaal * 100)}%;',
                                     data_mode="percentage",
                                     scaling=SCALING,
                                     id=f'amendement_{partij}_verworpen'):
                                span(f'{round(c / totaal * 100)}%')

                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    span('Aangenomen', cls='graph_aangenomen', style='margin:10px;padding:2px;color:white;')
                    span('Verworpen', cls='graph_verworpen', style='margin:10px;padding:2px;color:white;')
                    span('*Ingetrokken amendementen zijn onvindbaar')
                with div(cls='row', style='padding-top:10px; justify-content:center;'):
                    anchor("Percentage  / aantallen", href="#", onclick="toggleDataMode(); return false;",
                           cls="toggle-link")

            for partij in analysis['Amendement']:
                for result in analysis['Amendement'][partij]:
                    if 'Dieren' in partij:
                        partij_ = 'PvdD'
                    elif 'Ouderen' in partij:
                        partij_ = 'OAHvE'
                    elif 'LPF' in partij:
                        partij_ = 'LPF'
                    else:
                        partij_ = partij

                    with div(cls='hidden-content', id=f'amendement_{partij_}_{result}'):  # 'hidden-content
                        with div(cls='wrapper-no-margin'):
                            h1(f'{partij} {result}')
                            for module_id in analysis['Amendement'][partij][result]:
                                makeDivForModule(Module(module_id), 'gerelateerd', 'box collapsible')

            if 0:
                for partij in all_parties:
                    h1(partij)
                    a = len(analysis['Motie'][partij]['ingetrokken na toezegging']) or 0
                    b = len(analysis['Motie'][partij]['aangenomen']) or 0
                    c = len(analysis['Motie'][partij]['verworpen']) or 0
                    d = len(analysis['Motie'][partij]['ingetrokken']) or 0
                    totaal = a+b+c+d

                    with ul():
                        if totaal:
                            li(f'Ingetrokken met toezegging: {round(a / totaal * 100)}%')
                            li(f'Aangenomen: {round(b / totaal * 100)}%')
                            li(f'Verworpen: {round(c / totaal * 100)}%')
                            li(f'Ingetrokken: {round(d / totaal * 100)}%')
                            li(f'Totaal: {totaal}')


    with open(f'{os.getcwd()}/Presentation/htmls/analyse.html', 'w') as f:
        f.write(doc.render())




def makePage(m):
    doc = dominate.document(title=f'iRIS // {m.title}')


    with doc.head:
        meta(charset="UTF-8")
        # Include the Roboto font from Google Fonts
        link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap")
        link(rel='stylesheet',href="https://vjs.zencdn.net/7.2.3/video-js.css")
        link(rel="stylesheet", href="stylesheet.css")



        script( src=  "https://vjs.zencdn.net/ie8/ie8-version/videojs-ie8.min.js")
        #script(src="https://cdnjs.cloudflare.com/ajax/libs/videojs-contrib-hls/5.14.1/videojs-contrib-hls.js")
        #script(src="https://vjs.zencdn.net/7.2.3/video.js")
        script(src="https://cdn.jsdelivr.net/npm/hls.js@latest")
        script(src="panel-behaviour.js")

        dynamic_script = raw(f"""
            document.addEventListener('DOMContentLoaded', function () {{
                const video = document.getElementById('raadsvergaderingvideo');
                const videoSrc = '{m.chooseVideolink()}'; // HLS video URL
                const startTime = {m.chooseVideostarttime()}; // Start time in seconds

                document.getElementById('jump-link').addEventListener('click', function(e) {{
                    e.preventDefault(); // Prevent the URL refresh (since we're already on this page)
                    video.currentTime = startTime; // Set video to specified time
                }});

                function setStartTime() {{
                    // Set the video start time after metadata is loaded
                    if (startTime <= video.duration) {{
                        video.currentTime = startTime;
                    }} else {{
                        console.warn('Start time exceeds video duration.');
                    }}
                }}

                // Check if browser supports native HLS playback
                if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    // Native HLS support
                    video.src = videoSrc;
                    video.addEventListener('loadedmetadata', setStartTime);
                }} else {{
                    // Use Hls.js for browsers without native HLS support
                    if (Hls.isSupported()) {{
                        const hls = new Hls();
                        hls.loadSource(videoSrc);
                        hls.attachMedia(video);

                        hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                            setStartTime();
                        }});
                    }} else {{
                        console.error('HLS not supported in this browser.');
                    }}
                }}
            }});
        """)

        script(dynamic_script, type="text/javascript")








    with doc.body:
        with div(cls='header', id='header'):
            # h1('iRIS040',id='top')
            img(src='logo horizontaal.svg', alt='Iris logo', cls='center-logo', id='top')
            addMenu('', '')
            #if 0:
            #    with div(cls = 'menu'):
            #    a('alle stukken',href='index.html')
            #    a('mensen',href='raad.html')
            #    a('cijfers',href='analyse.html')
            #    a('raadsvoorstellen', href='raadsvoorstellen.html')




        if m.parent:
            with div(id='parentcontainer', cls='collapsible horizontal'):
                h2('Onderdeel van:',id='yellowtext')
                makeDivForModule(Module(m.parent),'parent','collapsible')

        makeDivForModule(m,'master','',doc)

        with div(cls='children'):
            if m.children:
                for child in m.children:
                    m_child = Module(child)
                    makeDivForModule(m_child,'child','collapsible')

        if m.related:

            with div(cls='wrapper',id='relatedcontainer'):
                h1('Gerelateerde stukken',id='purpletext')
                n = 0
                for related in m.related:
                    n+= 1
                    m_related = Module(related['id'])
                    makeDivForModule(m_related,'gerelateerd','box collapsible')
                    if n==20:
                        break

    with open(f'{os.getcwd()}/Presentation/htmls/{m.module_id}.html', 'w') as f:
        f.write(doc.render())


########
if 0:
    with open('json/relations/keyword_map.json', 'r') as file:
        keywords = json.load(file)
        #Module(966267).getvideostarttime()
        if 1:
            makePage(Module(1045940))
            makePage(Module(1034468))


if 1:
    mm = ModuleManager()
    mm.addall()
    mm.sort_chronological()
    makeIndex(mm)

if 0:
    mm = ModuleManager()
    mm.addall()
    mm.sort_chronological()
    makeIndex(mm)
    if 1:
        i = 1
        for module in mm.modules:
            print(module)
            #module.getvideostarttime()
            makePage(module)
            i+=1




if 0:
    mm = ModuleManager()
    all = mm.all()
    i = 0
    for m in all:
        mm.addmodule(m)
        i+=1
        if i>100:
            break
    with open('json/relations/keyword_map.json', 'r') as file:
        keywords_dict = json.load(file)
        keywords = tuple(keywords_dict.items())
    makeIndex(mm)


if 0:
    mm = ModuleManager()
    mm.add2022()
    mm.sort_chronological()


    with open('json/relations/keyword_map.json', 'r') as file:
        keywords_dict = json.load(file)
        keywords = tuple(keywords_dict.items())
    m  = 0
    if 0:
        for module in mm.modules:

            if module.get_date() > date(2025, 4, 22):
                makePage(module)
    if 0:
        makeIndex(mm)

    if 0:
        makeMemberPage(Member(194366),mm)

    if 1:
        folder_path = cwdpath(os.path.join('json', 'members', 'person'))
        members = os.listdir(folder_path)
        makeMemberIndex(members)
        if 1:
            for member_id in members:
                if member_id.startswith('.'):
                    continue
                makeMemberPage(Member(member_id), mm)


    if 0:
        makeAnalysisPagePartij(mm,'GroenLinks')
        makeAnalysisPagePartij(mm, 'FVD')
        makeAnalysisPagePartij(mm, 'SP')
        makeAnalysisPagePvdD(mm)
        makeAnalysisPage(mm)


    if 0: makeRaadsvoorstelPage(mm)

    if 0:
        counter =0
        for module in mm.modules:
            counter +=1
            if module.get_date() > date(2021, 4, 22):
            #keywords = list(module.keywords.keys())
                makePage(module)
if 0:
    makePage(Module(920652))



if 0:
    MeMa = MeetingManager()
    MeMa.addall()
    MeMa.sort_chronological()
    #makeMeetingPage(MeMa.meetings[8],'Raadzaal')
    makeMeetingIndex(MeMa)
if 0:

    count = 0
    for meeting in MeMa.meetings:
        count+=1
        print(count)

        #try:
        if meeting.subtitles and 'Raadzaal' in meeting.subtitles:
            makeMeetingPage(meeting,'Raadzaal')
        if meeting.subtitles and 'Commissiekamer' in meeting.subtitles:
            makeMeetingPage(meeting, 'Commissiekamer')
        #except:
        #    print(f'failed at: {meeting.title}')


