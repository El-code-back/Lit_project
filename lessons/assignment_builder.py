import re


DEFAULT_SHORT_PROMPTS = [
    "Кратко сформулируйте главную мысль материала.",
    "Назовите два важных факта из урока.",
    "Объясните, почему этот материал важен для темы.",
]


def split_sentences(text, limit=6):
    sentences = [
        sentence.strip(" \n\t.-")
        for sentence in re.split(r"(?<=[.!?])\s+", text or "")
        if len(sentence.strip()) > 20
    ]
    return sentences[:limit]


def extract_terms(text, limit=6):
    words = re.findall(r"[A-Za-zА-Яа-яЁё]{5,}", text or "")
    seen = set()
    terms = []
    for word in words:
        normalized = word.lower()
        if normalized not in seen:
            seen.add(normalized)
            terms.append(word)
        if len(terms) >= limit:
            break
    return terms


def manual_lines_to_items(manual_questions, assignment_type):
    lines = [line.strip() for line in (manual_questions or "").splitlines() if line.strip()]
    items = []
    for index, line in enumerate(lines[:12], start=1):
        item = {
            "id": f"q{index}",
            "type": assignment_type,
            "prompt": line,
        }
        if assignment_type == "test":
            item["options"] = ["Верно", "Неверно", "Частично верно"]
            item["answer"] = "Верно"
        elif assignment_type == "fill":
            item["answer"] = ""
        else:
            item["answer"] = ""
        items.append(item)
    return items


def build_assignment_payload(assignment_type, source_text="", manual_questions=""):
    manual_items = manual_lines_to_items(manual_questions, assignment_type)
    if manual_items:
        return {"items": manual_items}

    if assignment_type == "test":
        sentences = split_sentences(source_text, limit=5)
        if not sentences:
            sentences = ["Материал урока нужно внимательно прочитать перед ответом."]
        items = []
        for index, sentence in enumerate(sentences, start=1):
            items.append({
                "id": f"q{index}",
                "type": "test",
                "prompt": "Выберите верное утверждение по материалу урока.",
                "options": [
                    sentence,
                    "Это утверждение не относится к теме урока.",
                    "В материале говорится об обратном.",
                ],
                "answer": sentence,
            })
        return {"items": items}

    if assignment_type == "fill":
        sentences = split_sentences(source_text, limit=5)
        terms = extract_terms(source_text, limit=len(sentences))
        items = []
        for index, sentence in enumerate(sentences, start=1):
            answer = terms[index - 1] if index - 1 < len(terms) else ""
            prompt = sentence.replace(answer, "____", 1) if answer else sentence
            items.append({
                "id": f"q{index}",
                "type": "fill",
                "prompt": prompt,
                "answer": answer,
            })
        if not items:
            items.append({
                "id": "q1",
                "type": "fill",
                "prompt": "Заполните пропуск: ключевое понятие урока — ____.",
                "answer": "",
            })
        return {"items": items}

    prompts = split_sentences(source_text, limit=3)
    if prompts:
        items = [
            {"id": f"q{index}", "type": "short", "prompt": f"Объясните своими словами: {sentence}?", "answer": ""}
            for index, sentence in enumerate(prompts, start=1)
        ]
    else:
        items = [
            {"id": f"q{index}", "type": "short", "prompt": prompt, "answer": ""}
            for index, prompt in enumerate(DEFAULT_SHORT_PROMPTS, start=1)
        ]
    return {"items": items}
