class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        # self.metadata = metadata

    def __repr__(self):
        return f'Document(page_content="{self.page_content}")'

def markdown_splitter(input_file, delimiter="#####"):
    with open(input_file, 'r') as file:
        content = file.read()

    parts = [part.strip() for part in content.split(delimiter) if part.strip()]
    documents = []
    for part in parts:
        lines = part.split('\n')
        # api_name = lines[0].strip() if lines else "Unknown"
        page_content = '\n'.join(lines[1:]).strip()
        documents.append(page_content)  # Append only the page_content as a string
    return documents
