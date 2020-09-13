def parse_tree(token, tag):
    for child in token.children:
        if child.dep_ == tag:
            return child

def get_image_subject(doc):
    
    for token in doc:
        
        lemma = token.lemma_
        
        if lemma in ['image','picture','photo','look']:
            prep = parse_tree(token, 'prep')
            if prep is not None:
                pobj = parse_tree(prep, 'pobj')
            
            else:
                pobj = parse_tree(token, 'poss')
                
            children = [child for child in pobj.children]
            _obj = ""
            for child in children:
                _obj = child.text +" "+ _obj
            
            _obj += pobj.text
            return _obj


def needs_image(result, doc):
    
    if result[0][0]>0.4:
        confirm = False
        for token in doc:
            if token.lemma_ in ['image','picture','photo','look']:
                confirm = True
                return True

        if not confirm:
            return False
    else:
        return False

def needs_plot(doc):
    plot_list = ['chart','plot']
    for token in doc:
        if token.lemma_ in plot_list:
            return True
    return False

def get_plot_name(doc):
    plot_names = ['bar','pie','histogram']
    for token in doc:
        if token.text.lower() in plot_names:
            return token.text.lower()

def needs_table(doc):
    
    text = doc.text.lower()

    if text.find('table') == -1:
        return False
    else:
        return True



