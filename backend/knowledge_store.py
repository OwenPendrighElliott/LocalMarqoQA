from typing import Union, Dict, List, Callable

import marqo


def default_chunker(document: str):
    return [{"text": document}]


class MarqoKnowledgeStore:
    def __init__(
        self,
        client: marqo.Client,
        index_name: str,
        document_chunker: Callable[[str], List[str]] = default_chunker,
        document_cleaner: Union[Callable[[str], List[str]], None] = None,
    ) -> None:
        self._client = client
        self._index_name = index_name
        self._document_chunker = document_chunker
        self._document_cleaner = document_cleaner

        self._index_settings = {
            "model": "hf/e5-base-v2",
        }

        try:
            self._client.create_index(
                self._index_name, settings_dict=self._index_settings
            )
        except:
            print("Index exists")

    def query_for_content(
        self, query: Union[str, Dict[str, float]], content_var: str, limit: int = 5
    ) -> List[str]:
        resp = self._client.index(self._index_name).search(q=query, limit=limit)
        knowledge = [res[content_var] for res in resp["hits"] if res["_score"] > 0.5]

        return knowledge

    def add_document(self, document):
        if self._document_cleaner is not None:
            document = self._document_cleaner(document)

        print(document)
        print(self._document_chunker(document))
        self._client.index(self._index_name).add_documents(
            self._document_chunker(document),
            tensor_fields=["text"],
            client_batch_size=4,
        )

    def reset_index(self):
        self._client.delete_index(self._index_name)
        self._client.create_index(self._index_name, settings_dict=self._index_settings)
