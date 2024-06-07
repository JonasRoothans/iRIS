from classes.sub import Sub

s = Sub()
s.add_speakers_from_eventAPI('https://api.notubiz.nl/events/1147937?format=json')

s.print(500)
