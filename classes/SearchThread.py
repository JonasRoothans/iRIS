import threading
import queue
from classes.module import Module



class SearchThread:
    def __init__(self):
        self.current_thread = None
        self.stop_event = threading.Event()
        self.result_queue = queue.Queue()

    def search(self,iris,query):
        self.stop_event.clear()
        result = {}

        for item in iris.all_items:
            if self.stop_event.is_set():
                print(f'Search stopped for query: {query}')
                return

            node_matches = match(iris,item,query)
            result[item] = {
                'show' : node_matches,
                'match' : node_matches
                        }
            if node_matches:
                #Family is welcome:
                parent = iris.all_parents[item]
                if parent != '':
                    if parent not in result:
                        result[parent] = {
                            'show' : False, #default will be overwritten in the next line
                            'match' :False
                        }
                    result[parent]['show'] = True
                    siblings = iris.tree.get_children(parent)
                    for sibling in siblings:
                        if sibling not in result:
                            result[sibling] = {
                                'show': False, #default will be overwritten in the next line
                                'match': False
                            }
                        result[sibling]['show'] = True

        iris.root.after(0, lambda: iris.apply_search_result(result))

    def start_search(self,iris,query):
        print(f'Initiating search: {query}')
        #abort previous search
        if self.current_thread and self.current_thread.is_alive():
            self.stop_event.set()
            #self.current_thread.join()


        #make new search:
        self.stop_event.clear()
        self.current_thread = threading.Thread(target=self.search, args=(iris,query,))
        self.current_thread.start()
        iris.update_activity(f'Aan het zoeken naar  {query}')


def match(iris,item,query)->bool:
    item_text = iris.tree.item(item, 'text').lower()
    description_text = iris.tree.item(item, 'values')[2].lower()
    pdf_text = iris.pdf_texts[item]

    if not iris.search_show_rib.get():
        if iris.types[item] and iris.types[item] in 'Raadsinformatiebrief Collegebrief Nieuwsbrief Burgemeesterbrief':
            return False

    if query in item_text:
        return True
    if query in description_text:
        return True
    if iris.search_pdf_toggle.get():
        if pdf_text:
            if query in pdf_text.lower():
                return True
    return False

