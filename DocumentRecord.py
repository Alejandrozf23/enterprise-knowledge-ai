class DocumentRecord:
    def __init__(self, title, content, tags=None):
        if not isinstance(title, str) or not isinstance(content, str):
            raise TypeError("title y content deben ser strings")

        normalized_title = title.strip().lower()
        if not normalized_title:
            raise ValueError("title no debe estar vacío")

        if tags is not None:
            if not isinstance(tags, list):
                raise TypeError("tags debe ser una lista de strings o None")

            for tag in tags:
                if not isinstance(tag, str):
                    raise TypeError("cada etiqueta debe ser un string")

        self.title = normalized_title
        self.content = content.strip()
        self.tags = tags.copy() if tags is not None else []

    @property
    def word_count(self):
        return len(self.content.split())

    def add_tag(self, tag):
        if not isinstance(tag, str):
            raise TypeError("tag debe ser un string")

        normalized_tag = tag.strip().lower()
        if not normalized_tag:
            raise ValueError("tag no debe estar vacío")

        for existing_tag in self.tags:
            if existing_tag.strip().lower() == normalized_tag:
                return

        self.tags.append(normalized_tag)

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "tags": self.tags.copy(),
            "word_count": self.word_count,
        }