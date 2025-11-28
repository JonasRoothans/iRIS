import dominate
from dominate.tags import *
from dominate.tags import html, head, body, div, span, a, script
import re

def cleanLine(line):
    try:
        return line.split(' ', 1)[1].strip()
    except:
        return line


def text_to_dominate_lists(text):
    lines = text.strip().split("\n")

    # State variables to track current lists
    container = div()
    current = container
    preceding_text = p()
    container.add(preceding_text)
    current_ul = None
    type = ''
    level =-1

    for line in lines:
        line = line.strip()
        if 'leden van de raad' in line:
            return container

        # Match numbered lists ("1.", "2.")
        if re.match(r'^\d+\.', line) or re.match(r'^\d+\ ', line) or re.match(r'^\d+\)', line):
            nestedOnLine = False
            if line.startswith('1.') or line.startswith('1 ') or line.startswith('1)'):
                current_ol = ol()
                level +=1
                current.add(current_ol)
                current = current_ol
                type = '1'

            if len(line)<3:
                #probably a page number, let's ignore it.
                continue

            if line[2:].lstrip().startswith('a.'):
                #there is a nested list on this line.
                current.add(li(''))
                current_ol = ol(type="a")  # Ordered list with letters
                current.add(current_ol)
                current = current_ol
                type = 'a'
                level += 1
                nestedOnLine = True
                line = cleanLine(line)



            if type != '1' and level>0 and not nestedOnLine:
                current = current.parent
                level -= 1
                type = '1'

            if level >= 0:
                current.add(li(cleanLine(line)))  # Text after "1. "

            current_ul = None

        elif re.match(r'^[IVXLCDM]+\.', line) or re.match(r'^[IVXLCDM]+\)', line) or re.match(r'^[ivxlcdm]+\)', line):
            if line.startswith('I.') or line.startswith('i.') or line.startswith('i)'):
                current_ol = ol(type="I")
                current.add(current_ol)
                current = current_ol
                type = 'I'
                level +=1

            if type != 'I' and type != 'a' and level>0:
                current = current.parent
                level -= 1
                type = 'I'

            if level >= 0:
                    current.add(li(cleanLine(line)))  # Text after "1. "

            current_ul = None


        # Match lettered lists ("a.", "b.")
        elif re.match(r'^[a-z]\.', line, flags=re.IGNORECASE) or re.match(r'^[a-z]\)', line, flags=re.IGNORECASE):
            if line.startswith('a.') or line.startswith('a)'):
                current_ol = ol(type="a")  # Ordered list with letters
                current.add(current_ol)
                current = current_ol
                type = 'a'
                level += 1

            if type != 'a' and level>0:
                current = current.parent
                level -= 1
                type = 'a'

            if 'Jongbloed' in line:
                #een regel die begint met J. Jonbloed komt hier ook uit, maar markeert einde van het document
                return container

            try:
                current.add(li(cleanLine(line)))  # Text after "a. "
            except:
                print('debug')
            current_ul = None



        # Match unordered list items (starting with "•")
        elif re.match(r'^•', line) or re.match(r'^-', line) :
            if not current_ul:
                current_ul = ul()
                current.add(current_ul)
                level += 1
            current_ul.add(li(cleanLine(line)))  # Text after "•"


        else:
            if current and current.children and level >= 0:
                current.children[-1].add(f' {line}')
            elif level < 0 and preceding_text:

                preceding_text.add(verwijderOpOm(line))

    return container

def verwijderOpOm(line):
    if ':' in line and 'ollege' in line.split(':')[0]:
        return line.split(':')[1]
    else:
        return f' {line}'

def getInhoudFromPDF(m):
    hiddenclass = 'hidden-content'
    with div(id='inhoud') as inhoud:
        if m.pdf_text:
            h3('Inhoud:', cls=hiddenclass)
            with div(cls=f'scrollable {hiddenclass}'):
                with p() as besluit_p:
                    # Find the positions of the start and end markers
                    start = m.pdf_text.find("Doelstelling")  # Start after 'besluit:'
                    end = m.pdf_text.find("Argumenten")  # End position before 'Aldus vastgesteld'

                    # Als het een ontwerpraadsbesluit is:
                    if start != -1 and end != -1 and start < end:
                        result = m.pdf_text[start:end]  # Extract and remove surrounding whitespace

                        if 'Voorstel' in m.pdf_text.split('Doelstelling')[1].split('Argumenten')[0]:
                            doelstelling_text = m.pdf_text.split('Doelstelling')[1].split('Voorstel')[0]
                            voorstel_text = m.pdf_text.split('Voorstel')[1].split('Argumenten')[0]
                        else:
                            doelstelling_text = m.pdf_text.split('Doelstelling')[1].split('Argumenten')[0]
                            voorstel_text = ''

                        p(strong('Doelstelling'))
                        p(doelstelling_text)
                        if 0:
                            if 'master' in id_:
                                with doc.head:
                                    meta(
                                        name='description',
                                        content=doelstelling_text
                                    )

                        p(strong('Voorstel'))
                        text_to_dominate_lists(voorstel_text)

                        counter = 0

                        if 0:

                            with ol():
                                while True:

                                    counter += 1
                                    index = voorstel_text.find(f'{counter}. ')
                                    if index == -1:
                                        index = voorstel_text.find(f'{counter}) ')
                                        if index == -1:
                                            break
                                    indexend = voorstel_text.find(f'{counter + 1}. ')
                                    if indexend == -1:
                                        indexend = voorstel_text.find(f'{counter + 1}) ')
                                    li(voorstel_text[index + 2:indexend])
                    if 'Collegebrief' in m.pdf_text:
                        p('Die je kun je het beste even zelf lezen:')
                        a('Lees de brief hier', href=m.pdf_url)
                        return

                    if 'Raadsinformatiebrief' in m.type:
                        if 'Besluit van' in m.pdf_text:
                            voorstel_text = m.pdf_text.split('Besluit van')[1].split('Argumenten')[0]
                        elif 'Voorstel' in m.pdf_text:
                            voorstel_text = m.pdf_text.split('Voorstel')[1].split('Argumenten')[0]
                        else:
                            p('het was lastig de kern te vinden...')
                            return

                        p(strong('Besluit van het college:'))

                        counter = 0

                        with ol():
                            while True:

                                counter += 1
                                index = voorstel_text.find(f'{counter}. ')
                                if index == -1:
                                    index = voorstel_text.find(f'{counter}) ')
                                    if index == -1:
                                        break
                                indexend = voorstel_text.find(f'{counter + 1}. ')
                                if indexend == -1:
                                    indexend = voorstel_text.find(f'{counter + 1}) ')
                                li(voorstel_text[index + 2:indexend])
                    if 'motie' in m.type.lower():
                        sentences = re.split(r'[;:]', m.pdf_text)
                        s = 0
                        counter = 0
                        laatstedeel = None
                        txt = m.pdf_text.replace('  ', ' ')

                        if 'De raad roept' in txt:
                            text_to_dominate_lists(txt.split('De raad roept')[1])
                        if 'oept het college op' in txt:
                            text_to_dominate_lists(txt.split('oept het college op')[1])
                        if 'draagt het college van' in txt:
                            text_to_dominate_lists(txt.split('draagt het college van')[1])
                        if 'roepen het college' in txt:
                            text_to_dominate_lists(txt.split('roepen het college')[1])

                        if 0:

                            if 'De raad roept' in txt or 'oept het college op' in txt or 'draagt het college van' in txt or 'roepen het college':
                                dictum_detected = False
                                for sentence in sentences:
                                    sentence = sentence.replace('  ', ' ')
                                    if 'wethouders op om' in sentence or dictum_detected or 'college op om':
                                        if not dictum_detected:
                                            if 'wethouders op om' in sentence:
                                                sentence = sentence.split('wethouders op om')[1]
                                                dictum_detected = True
                                                if 'leden van de raad' in sentence:
                                                    laatstedeel = sentence.split('leden van de raad')[0]
                                                if 'lid van de raad' in sentence:
                                                    laatstedeel = sentence.split('lid van de raad')[0]

                                                if laatstedeel:
                                                    einde = laatstedeel.rfind('Eindhoven')

                                                    p(laatstedeel[:einde])
                                                    break
                                            if 'college op om' in sentence:
                                                sentence = sentence.split('college op om')[1]
                                                dictum_detected = True
                                                if 'leden van de raad' in sentence:
                                                    laatstedeel = sentence.split('leden van de raad')[0]
                                                if 'lid van de raad' in sentence:
                                                    laatstedeel = sentence.split('lid van de raad')[0]
                                                if laatstedeel:
                                                    einde = laatstedeel.rfind('Eindhoven')

                                                    p(laatstedeel[:einde])
                                                    break

                                        elif 'leden van de raad' in sentence or 'lid van de raad' in sentence:
                                            if 'leden van de raad' in sentence:
                                                laatstedeel = sentence.split('leden van de raad')[0]
                                            if 'lid van de raad' in sentence:
                                                laatstedeel = sentence.split('lid van de raad')[0]
                                            einde = laatstedeel.rfind('Eindhoven')

                                            p(laatstedeel[:einde])
                                            break

                                        else:
                                            p(sentence)

                            else:

                                for sentence in sentences:
                                    s += 1
                                    if sentence.strip().startswith('-') or sentence.strip().startswith('•'):
                                        with ul():
                                            li(raw(fancy(startStringAtFirstrLetter(sentence.strip()))))
                                    if sentence.strip()[:1].isdigit():
                                        counter += 1
                                        with ol(start=counter):
                                            li(raw(fancy(startStringAtFirstrLetter(sentence.strip()))))
                                    if 'De raad roept het college van burgemeester' in sentence:
                                        p(sentence)
                                        for lastsentences in sentences[s:]:
                                            if 'De leden van de raad' in lastsentences:
                                                strong(p(lastsentences.split('De leden van de raad')[0]))
                                                break
                                            strong(p(raw(fancy(lastsentences))))
                                        break

                    if len(besluit_p) < 500:
                        besluit_p.set_attribute('id', 'larger')
    return
