def build_title_index(documents):
    processed_documents = process_document_collection(documents)
    title_index = {}

    for document in processed_documents:
        title = document["title"]

        if title not in title_index:
            title_index[title] = []

        title_index[title].append(document["content"])

    return title_index