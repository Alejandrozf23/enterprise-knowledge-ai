def select_documents(documents, start, stop, step):
    return documents[start:stop:step]

def replace_documents_in_place(documents, start, stop, replacements):
    documents[start:stop] = replacements