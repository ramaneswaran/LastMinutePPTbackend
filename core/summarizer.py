def get_summary(text):
    
    # Removing Square Brackets and Extra Spaces
    text = re.sub(r'\[[0-9]*\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Removing special characters and digits
    formatted_text = re.sub('[^a-zA-Z]', ' ', text )
    formatted_text = re.sub(r'\s+', ' ', formatted_text)
    
    sentence_list = nltk.sent_tokenize(text)
    
    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
                
    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
        
    
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
        
    summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)

    
    summary = ' '.join(summary_sentences)
    
    return summary
    

def get_title(doc):
    
    phrases = doc._.phrases
    
    if len(phrases)>0:
        phrase =  phrases[0].text
        phrase = phrase.title()
        return phrase

    if (len(doc.sents)) == 1:
        return doc.text




def get_connected_words(root, visited):

    phrase = []
    for child in root.children:
        if child not in visited:
            phrase.append((child.text, child.i))
            visited.add(child)


            extra = get_connected_words(child, visited)
            
            phrase += extra
    
    head = root.head

    for child in head.children:
        if child not in visited:
            phrase.append((child.text, child.i))
            visited.add(child)
            
            extra = get_connected_words(child, visited)
            
            phrase += extra
    
    return phrase


def get_bullets(doc):
    chunks = []
    for chunk in doc.noun_chunks:
        chunks += chunk.text.split()
    
    roots = [token for token in doc if token.text in chunks or token.pos_ == 'VERB']

    sents = []
    bullet = set()
    for root in roots:
        visited = set()
        words = get_connected_words(root, visited)

        words.sort(key=lambda x: x[1])
        
        if len(words)>2:
            sent = ' '.join([item[0] for item in words])
            if sent not in bullet:
                sents.append(sent)
                bullet.add(sent)

    return sents