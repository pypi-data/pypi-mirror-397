import openai


def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    data = response.data
    if not data or len(data) == 0:
        return None
    return data[0].embedding
