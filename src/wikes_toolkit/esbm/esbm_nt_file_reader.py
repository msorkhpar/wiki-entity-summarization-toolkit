from typing import List, Tuple
import re

from rdflib.term import URIRef, Literal, BNode

nt_triple_pattern = re.compile(r'<?(.*?)>?\s+<?(.*?)>?\s+<?(.*?)>?\s+\.\s*')


def _get_value(entity):
    if isinstance(entity, URIRef):
        return str(entity)
    elif isinstance(entity, Literal):
        if str(entity._datatype) == "http://dbpedia.org/datatype/usDollar":
            return f"${float(str(entity))}"
        elif entity._datatype:
            return str(entity)
        elif entity._language:
            return f"{entity.value}@{entity._language}"
        else:
            return entity.value


def _parse_nt_line(line):
    match = nt_triple_pattern.match(line)
    if match:
        subject = match.group(1)
        predicate = match.group(2)
        object_ = match.group(3)

        def parse_term(term):
            if term.startswith('<') and term.endswith('>'):
                return URIRef(term[1:-1])
            elif term.startswith('_:'):
                return BNode(term)
            elif term.startswith('"'):
                if '^^' in term:
                    value, datatype = term.rsplit('^^', 1)
                    return Literal(value.strip('"'), datatype=URIRef(datatype.strip('<>')))
                elif '@' in term:
                    value, lang = term.rsplit('@', 1)
                    return Literal(value.strip('"'), lang=lang)
                else:
                    return Literal(term.strip('"'))
            else:
                return URIRef(term)

        return parse_term(subject), URIRef(predicate.strip('<>')), parse_term(object_)
    return None


def _convert_line_to_triple(line: str):
    triple = _parse_nt_line(line)
    subject = _get_value(triple[0])
    predicate = _get_value(triple[1])
    object_ = _get_value(triple[2])
    return subject, predicate, object_


def extract_triples(nt_file_path: str) -> List[Tuple[str, str, str]]:
    result = list()
    with open(nt_file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        result.append(
            _convert_line_to_triple(line)
        )
    return result
