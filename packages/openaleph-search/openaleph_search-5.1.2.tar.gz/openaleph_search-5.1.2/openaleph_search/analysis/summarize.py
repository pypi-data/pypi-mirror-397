"""
Document summarization via deterministic analysis.

Generates semantic document summaries by analyzing:
- Entity mentions (names of persons, organizations, etc.)
- Key phrases and topics from fulltext
- Matched structured entities from the Things index
- Optional topic clustering via term vectors
"""

import math
from typing import Any, TypeAlias

from anystore.logging import get_logger
from pydantic import BaseModel, Field

from openaleph_search.core import get_es
from openaleph_search.index.indexes import entities_read_index
from openaleph_search.index.mapping import Field as MappingField
from openaleph_search.settings import Settings

log = get_logger(__name__)
settings = Settings()

TermVector: TypeAlias = dict[str, float]

# spaCy English stopwords (326 words) - copied to avoid runtime dependency
# Source: https://github.com/explosion/spaCy/blob/master/spacy/lang/en/stop_words.py
STOPWORDS = frozenset({
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amount", "an", "and", "another", "any", "anyhow",
    "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at",
    "back", "be", "became", "because", "become", "becomes", "becoming", "been",
    "before", "beforehand", "behind", "being", "below", "beside", "besides",
    "between", "beyond", "both", "bottom", "but", "by", "call", "can", "cannot",
    "ca", "could", "did", "do", "does", "doing", "done", "down", "due", "during",
    "each", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough",
    "even", "ever", "every", "everyone", "everything", "everywhere", "except",
    "few", "fifteen", "fifty", "first", "five", "for", "former", "formerly",
    "forty", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "have", "he", "hence", "her", "here", "hereafter", "hereby",
    "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how",
    "however", "hundred", "i", "if", "in", "indeed", "into", "is", "it", "its",
    "itself", "just", "keep", "last", "latter", "latterly", "least", "less",
    "made", "make", "many", "may", "me", "meanwhile", "might", "mine", "more",
    "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name",
    "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody",
    "none", "noone", "nor", "not", "nothing", "now", "nowhere", "n't", "of",
    "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others",
    "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per",
    "perhaps", "please", "put", "quite", "rather", "re", "really", "regarding",
    "same", "say", "see", "seem", "seemed", "seeming", "seems", "serious",
    "several", "she", "should", "show", "side", "since", "six", "sixty", "so",
    "some", "somehow", "someone", "something", "sometime", "sometimes",
    "somewhere", "still", "such", "take", "ten", "than", "that", "the", "their",
    "them", "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "third", "this",
    "those", "though", "three", "through", "throughout", "thru", "thus", "to",
    "together", "too", "top", "toward", "towards", "twelve", "twenty", "two",
    "under", "unless", "until", "up", "upon", "us", "used", "using", "various",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein",
    "whereupon", "wherever", "whether", "which", "while", "whither", "who",
    "whoever", "whole", "whom", "whose", "why", "will", "with", "within",
    "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves",
    "'d", "'ll", "'m", "'re", "'s", "'ve",
})

# Minimum word length for significant terms (filters out noise)
MIN_TERM_LENGTH = 3


class NameMention(BaseModel):
    """An entity name mentioned in the document with frequency."""

    name: str
    count: int
    # Whether this name matches a known entity in the Things index
    is_known_entity: bool = False
    entity_schema: str | None = None


class KeyPhrase(BaseModel):
    """A significant phrase or term from the document."""

    phrase: str
    score: float
    # Number of words in the phrase
    word_count: int = 1
    # How many other documents contain this phrase
    corpus_frequency: int = 0


class MatchedEntity(BaseModel):
    """An entity from the Things index that matches a mentioned name."""

    entity_id: str
    caption: str
    schema_: str = Field(alias="schema")
    score: float = 0.0

    model_config = {"populate_by_name": True}


class TopicCluster(BaseModel):
    """Topic cluster assignment from term vector clustering."""

    cluster_id: int
    top_terms: list[str] = Field(default_factory=list)
    similarity: float = 0.0


class DocumentSummary(BaseModel):
    """Semantic summary of a document's content."""

    document_id: str
    index: str
    schema_: str = Field(default="Document", alias="schema")

    # WHO: Entity mentions (persons, organizations, etc.)
    entity_mentions: list[NameMention] = Field(default_factory=list)

    # WHAT: Key phrases and topics
    key_phrases: list[KeyPhrase] = Field(default_factory=list)

    # Links to structured entities in the dataset
    matched_entities: list[MatchedEntity] = Field(default_factory=list)

    # Optional clustering
    topic_cluster: TopicCluster | None = None

    # Metadata
    total_names: int = 0
    total_terms: int = 0

    model_config = {"populate_by_name": True}


def _get_document(es, document_id: str) -> tuple[dict[str, Any], str] | None:
    """Fetch document by ID across all document indexes."""
    index_pattern = entities_read_index(schema=["Document", "Pages"])
    result = es.search(
        index=index_pattern,
        body={
            "query": {"ids": {"values": [document_id]}},
            "size": 1,
            "_source": [MappingField.NAMES, MappingField.DATASET, MappingField.SCHEMA],
        },
    )
    hits = result.get("hits", {}).get("hits", [])
    if not hits:
        return None
    return hits[0]["_source"], hits[0]["_index"]


def _is_meaningful_term(term: str) -> bool:
    """Check if a term is semantically meaningful (not a stopword or noise)."""
    term_lower = term.lower()

    # Too short
    if len(term_lower) < MIN_TERM_LENGTH:
        return False

    # Stopword
    if term_lower in STOPWORDS:
        return False

    # Pure numbers (but allow alphanumeric like "2016" in context)
    if term_lower.isdigit():
        return False

    # Single repeated character
    if len(set(term_lower)) == 1:
        return False

    return True


def _get_name_frequencies(
    es, document_id: str, index: str, names: list[str]
) -> dict[str, int]:
    """
    Count occurrences of each name in the document's fulltext content.

    Returns a dict mapping name -> count.
    """
    if not names:
        return {}

    try:
        tv_response = es.termvectors(
            index=index,
            id=document_id,
            fields=[MappingField.CONTENT],
            term_statistics=False,
            field_statistics=False,
            positions=False,
            offsets=False,
        )
    except Exception as e:
        log.warning("Failed to get term vectors", error=str(e), document_id=document_id)
        return {}

    content_terms = (
        tv_response.get("term_vectors", {})
        .get(MappingField.CONTENT, {})
        .get("terms", {})
    )

    name_counts: dict[str, int] = {}
    for name in names:
        # Tokenize the name (simple lowercase split)
        tokens = name.lower().split()

        # Find minimum token frequency (conservative count)
        min_freq = float("inf")
        for token in tokens:
            term_info = content_terms.get(token, {})
            freq = term_info.get("term_freq", 0)
            if freq == 0:
                min_freq = 0
                break
            min_freq = min(min_freq, freq)

        if min_freq > 0 and min_freq != float("inf"):
            name_counts[name] = int(min_freq)

    return name_counts


def _match_entities_from_things(
    es,
    names: list[str],
    dataset: str,
    size: int = 50,
) -> dict[str, MatchedEntity]:
    """
    Match document names against structured entities in the Things index.

    Returns a dict mapping name -> MatchedEntity for quick lookup.
    """
    if not names:
        return {}

    things_index = entities_read_index(schema=["Thing"])

    # Build a bool query with should clauses for each name
    should_clauses = [
        {"match": {MappingField.NAMES: {"query": name, "fuzziness": "AUTO"}}}
        for name in names[:50]
    ]

    body = {
        "query": {
            "bool": {
                "must": [{"term": {MappingField.DATASET: dataset}}],
                "should": should_clauses,
                "minimum_should_match": 1,
            }
        },
        "size": size,
        "_source": [MappingField.CAPTION, MappingField.SCHEMA, MappingField.NAMES],
    }

    try:
        result = es.search(index=things_index, body=body)
    except Exception as e:
        log.warning("Failed to match entities from Things index", error=str(e))
        return {}

    hits = result.get("hits", {}).get("hits", [])

    # Build lookup by matching names
    matched: dict[str, MatchedEntity] = {}
    for hit in hits:
        entity = MatchedEntity(
            entity_id=hit["_id"],
            caption=hit["_source"].get(MappingField.CAPTION, ""),
            schema=hit["_source"].get(MappingField.SCHEMA, "Thing"),
            score=hit.get("_score", 0.0),
        )
        # Map each name variant to this entity
        entity_names = hit["_source"].get(MappingField.NAMES, [])
        for name in entity_names:
            if name.lower() in [n.lower() for n in names]:
                matched[name] = entity

    return matched


def _extract_phrases_from_termvectors(
    es,
    document_id: str,
    index: str,
    size: int = 20,
    field: str = MappingField.CONTENT,
) -> list[KeyPhrase]:
    """
    Extract significant phrases using term vectors with positions.

    Identifies both single meaningful terms and adjacent term pairs (bigrams)
    that appear together, boosting phrases over single words.
    """
    try:
        tv = es.termvectors(
            index=index,
            id=document_id,
            fields=[field],
            term_statistics=True,
            field_statistics=True,
            positions=True,
        )
    except Exception as e:
        log.warning("Failed to get term vectors for phrases", error=str(e))
        return []

    field_data = tv.get("term_vectors", {}).get(field, {})
    field_stats = field_data.get("field_statistics", {})
    terms_data = field_data.get("terms", {})

    if not terms_data:
        return []

    total_docs = field_stats.get("doc_count", 1)

    # Build position -> term mapping for phrase detection
    position_to_term: dict[int, tuple[str, int, int]] = {}  # pos -> (term, tf, df)
    term_scores: dict[str, tuple[float, int, int]] = {}  # term -> (score, tf, df)

    for term, stats in terms_data.items():
        if not _is_meaningful_term(term):
            continue

        tf = stats.get("term_freq", 0)
        df = stats.get("doc_freq", 1)

        # Only include terms that appear in other documents
        if df <= 1:
            continue

        # TF-IDF scoring
        tf_weight = 1 + math.log(tf) if tf > 0 else 0
        idf_weight = math.log(total_docs / df) if df > 0 else 0
        score = tf_weight * idf_weight

        term_scores[term] = (score, tf, df)

        # Record positions for phrase detection
        tokens = stats.get("tokens", [])
        for token in tokens:
            pos = token.get("position")
            if pos is not None:
                position_to_term[pos] = (term, tf, df)

    # Detect bigrams (adjacent meaningful terms)
    bigram_scores: dict[str, tuple[float, int]] = {}  # phrase -> (score, df)
    positions = sorted(position_to_term.keys())

    for i in range(len(positions) - 1):
        pos1, pos2 = positions[i], positions[i + 1]
        # Adjacent positions
        if pos2 - pos1 == 1:
            term1, _, df1 = position_to_term[pos1]
            term2, _, df2 = position_to_term[pos2]

            # Create bigram
            bigram = f"{term1} {term2}"

            # Score: geometric mean of individual scores, boosted by 1.5x for being a phrase
            score1 = term_scores.get(term1, (0, 0, 0))[0]
            score2 = term_scores.get(term2, (0, 0, 0))[0]
            bigram_score = math.sqrt(score1 * score2) * 1.5

            # Use min df as phrase frequency estimate
            min_df = min(df1, df2)

            if bigram not in bigram_scores or bigram_scores[bigram][0] < bigram_score:
                bigram_scores[bigram] = (bigram_score, min_df)

    # Combine single terms and bigrams
    all_phrases: list[tuple[str, float, int, int]] = []

    # Add bigrams first (they're more meaningful)
    for phrase, (score, df) in bigram_scores.items():
        all_phrases.append((phrase, score, 2, df))

    # Add single terms
    for term, (score, tf, df) in term_scores.items():
        all_phrases.append((term, score, 1, df))

    # Sort by score descending
    all_phrases.sort(key=lambda x: x[1], reverse=True)

    # Deduplicate: if a term is part of a higher-scoring bigram, skip it
    seen_terms: set[str] = set()
    result: list[KeyPhrase] = []

    for phrase, score, word_count, df in all_phrases:
        if len(result) >= size:
            break

        # Skip if this single term is already covered by a bigram
        if word_count == 1 and phrase in seen_terms:
            continue

        result.append(
            KeyPhrase(
                phrase=phrase,
                score=round(score, 3),
                word_count=word_count,
                corpus_frequency=df,
            )
        )

        # Mark terms as seen
        for word in phrase.split():
            seen_terms.add(word)

    return result


def _get_term_vector(es, document_id: str, index: str) -> TermVector:
    """Extract TF-IDF weighted term vector for clustering."""
    try:
        response = es.termvectors(
            index=index,
            id=document_id,
            fields=[MappingField.CONTENT],
            term_statistics=True,
            field_statistics=True,
            positions=False,
            offsets=False,
        )
    except Exception as e:
        log.warning("Failed to get term vectors for clustering", error=str(e))
        return {}

    if MappingField.CONTENT not in response.get("term_vectors", {}):
        return {}

    field_data = response["term_vectors"][MappingField.CONTENT]
    field_stats = field_data.get("field_statistics", {})
    total_docs = field_stats.get("doc_count", 1)
    terms = field_data.get("terms", {})

    term_weights: TermVector = {}
    for term, stats in terms.items():
        if not _is_meaningful_term(term):
            continue

        tf = stats.get("term_freq", 0)
        df = stats.get("doc_freq", 1)

        tf_weight = 1 + math.log(tf) if tf > 0 else 0
        idf_weight = math.log(total_docs / df) if df > 0 else 0
        tfidf = tf_weight * idf_weight

        if tfidf > 0:
            term_weights[term] = tfidf

    return term_weights


def _cluster_document(
    es,
    document_id: str,
    index: str,
    doc_vector: TermVector,
    n_clusters: int = 5,
    sample_size: int = 100,
    dataset: str | None = None,
) -> TopicCluster | None:
    """Assign document to a topic cluster using k-means on term vectors."""
    if not doc_vector:
        return None

    try:
        from sklearn.cluster import KMeans
        from sklearn.feature_extraction import DictVectorizer
    except ImportError:
        log.warning("sklearn not available for clustering")
        return None

    query: dict[str, Any] = {"match_all": {}}
    if dataset:
        query = {"term": {MappingField.DATASET: dataset}}

    try:
        sample_result = es.search(
            index=index,
            body={
                "query": query,
                "size": sample_size,
                "_source": False,
            },
        )
    except Exception as e:
        log.warning("Failed to sample documents for clustering", error=str(e))
        return None

    sample_ids = [
        hit["_id"]
        for hit in sample_result.get("hits", {}).get("hits", [])
        if hit["_id"] != document_id
    ]

    if len(sample_ids) < n_clusters:
        log.debug("Not enough documents for clustering", sample_size=len(sample_ids))
        return None

    doc_vectors: dict[str, TermVector] = {document_id: doc_vector}
    for sample_id in sample_ids:
        vec = _get_term_vector(es, sample_id, index)
        if vec:
            doc_vectors[sample_id] = vec

    if len(doc_vectors) < n_clusters + 1:
        return None

    vectorizer = DictVectorizer()
    all_ids = list(doc_vectors.keys())
    feature_matrix = vectorizer.fit_transform([doc_vectors[did] for did in all_ids])

    target_idx = all_ids.index(document_id)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    cluster_labels = kmeans.fit_predict(feature_matrix)

    cluster_id = int(cluster_labels[target_idx])

    feature_names = vectorizer.get_feature_names_out()
    cluster_center = kmeans.cluster_centers_[cluster_id]
    top_indices = cluster_center.argsort()[-10:][::-1]
    top_terms = [str(feature_names[i]) for i in top_indices]

    target_vector = feature_matrix[target_idx].toarray().flatten()
    similarity = float(
        sum(target_vector[i] * cluster_center[i] for i in range(len(cluster_center)))
        / (math.sqrt(sum(target_vector**2)) * math.sqrt(sum(cluster_center**2)) + 1e-10)
    )

    return TopicCluster(
        cluster_id=cluster_id,
        top_terms=top_terms,
        similarity=similarity,
    )


def summarize_document(
    document_id: str,
    entity_mentions_size: int = 15,
    key_phrases_size: int = 15,
    matched_entities_size: int = 20,
    include_clustering: bool = False,
    n_clusters: int = 5,
    cluster_sample_size: int = 100,
) -> DocumentSummary | None:
    """
    Generate a semantic summary for a document.

    The summary focuses on:
    - WHO: Entity mentions (persons, organizations) from the names field
    - WHAT: Key phrases and topics extracted from fulltext
    - LINKS: Matched structured entities from the Things index

    Args:
        document_id: The document ID to summarize
        entity_mentions_size: Max number of entity mentions to return
        key_phrases_size: Max number of key phrases to return
        matched_entities_size: Max matched entities from Things index
        include_clustering: Whether to compute topic cluster assignment
        n_clusters: Number of clusters for k-means
        cluster_sample_size: Documents to sample for clustering

    Returns:
        DocumentSummary or None if document not found
    """
    es = get_es()

    # Fetch the document
    doc_result = _get_document(es, document_id)
    if not doc_result:
        log.warning("Document not found", document_id=document_id)
        return None

    doc_source, doc_index = doc_result
    names = doc_source.get(MappingField.NAMES, [])
    schema = doc_source.get(MappingField.SCHEMA, "Document")
    dataset = doc_source.get(MappingField.DATASET)

    if not dataset:
        log.warning("Document has no dataset", document_id=document_id)
        return None

    log.debug(
        "Summarizing document",
        document_id=document_id,
        index=doc_index,
        name_count=len(names),
    )

    # 1. Get name frequencies in content
    name_frequencies = _get_name_frequencies(es, document_id, doc_index, names)

    # 2. Match names against Things index
    matched_entities_map = _match_entities_from_things(
        es, names, dataset=dataset, size=matched_entities_size
    )

    # 3. Build entity mentions with frequency and known-entity flag
    entity_mentions: list[NameMention] = []
    for name in names:
        count = name_frequencies.get(name, 0)
        matched = matched_entities_map.get(name)
        entity_mentions.append(
            NameMention(
                name=name,
                count=count,
                is_known_entity=matched is not None,
                entity_schema=matched.schema_ if matched else None,
            )
        )

    # Sort by: known entities first, then by count
    entity_mentions.sort(key=lambda x: (not x.is_known_entity, -x.count))
    entity_mentions = entity_mentions[:entity_mentions_size]

    # 4. Extract key phrases from fulltext
    key_phrases = _extract_phrases_from_termvectors(
        es, document_id, doc_index, size=key_phrases_size
    )

    # 5. Get unique matched entities
    matched_entities = list(matched_entities_map.values())[:matched_entities_size]

    # 6. Optional clustering
    topic_cluster = None
    doc_vector: TermVector = {}
    if include_clustering:
        doc_vector = _get_term_vector(es, document_id, doc_index)
        topic_cluster = _cluster_document(
            es,
            document_id,
            doc_index,
            doc_vector,
            n_clusters=n_clusters,
            sample_size=cluster_sample_size,
            dataset=dataset,
        )

    return DocumentSummary(
        document_id=document_id,
        index=doc_index,
        schema=schema,
        entity_mentions=entity_mentions,
        key_phrases=key_phrases,
        matched_entities=matched_entities,
        topic_cluster=topic_cluster,
        total_names=len(names),
        total_terms=len(doc_vector) if doc_vector else 0,
    )
