from hydrangea import chat


def test_request_has_rules_findings_and_trimmed_history():
    hist = [{"role": "user" if i % 2 == 0 else "model", "text": f"m{i}"} for i in range(10)] + [{"role": "system", "text": "x"}]
    r = chat.build_request("can I cut now?", {"plant": "Hydrangea", "answer": "Only a little"}, hist, "ru")
    system = r["system_instruction"]["parts"][0]["text"]
    assert "Russian" in system and "Plant: Hydrangea" in system and "Never give doses" in system
    assert len(r["contents"]) == chat.MAX_TURNS + 1 and r["contents"][-1]["parts"][0]["text"] == "can I cut now?"


def test_bad_context_does_not_crash():
    assert "no photo checked yet" in chat.build_request("hi", "oops", None, "en")["system_instruction"]["parts"][0]["text"]


def test_rate_limit_per_ip():
    chat._per_ip.clear(); chat._day.clear()
    assert all(chat._allow("1.2.3.4", 1000.0) for _ in range(chat.PER_IP_PER_HOUR))
    assert not chat._allow("1.2.3.4", 1001.0)
    assert chat._allow("5.6.7.8", 1001.0)
    assert chat._allow("1.2.3.4", 1000.0 + 3601)


def test_identify_request_and_parsing():
    cands = {"plum": "Plum tree", "rose": "Rose"}
    r = chat.build_identify_request([b"x", b"y"], "ru", cands)
    parts = r["contents"][0]["parts"]
    assert "Russian" in parts[0]["text"] and '"plum"' in parts[0]["text"] and len(parts) == 3
    ok = chat.parse_identify('{"name": "Plum", "key": "plum", "confidence": "medium"}', cands)
    assert ok == {"name": "Plum", "key": "plum", "confidence": "medium"}
    odd = chat.parse_identify('{"name": "Cactus", "key": "cactus", "confidence": "sure"}', cands)
    assert odd["key"] is None and odd["confidence"] == "low"
