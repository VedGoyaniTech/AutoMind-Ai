"""
AutoMind AI — Unit Test Suite for Offline DPO Dataset Exporter & ML Safety
"""

import os
import sys

from ml.datasets.export_dpo_dataset import redact_pii, normalize_prompt, run_dpo_export
from app.db.session import SessionLocal, engine, Base
from app.models.feedback import MessageFeedback

def test_pii_redaction():
    text_with_email = "Contact me at buyer@example.com for Thar quotation."
    redacted_email = redact_pii(text_with_email)
    assert "[EMAIL REDACTED]" in redacted_email
    assert "buyer@example.com" not in redacted_email

    text_with_phone = "Call me on 9876543210 regarding Creta EMI."
    redacted_phone = redact_pii(text_with_phone)
    assert "[PHONE REDACTED]" in redacted_phone
    assert "9876543210" not in redacted_phone

def test_prompt_normalization():
    p1 = "Nexon ka Ahmedabad me on-road price kitna hoga?"
    p2 = "nexon ka ahmedabad me on-road price kitna hoga??  "
    assert normalize_prompt(p1) == normalize_prompt(p2)

def test_dpo_pairing_and_no_fabrication():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clear previous records
        db.query(MessageFeedback).delete()
        db.commit()

        # 1. Add single un-paired upvote (should NOT generate DPO pair)
        single_up = MessageFeedback(
            conversation_id=1,
            message_id=1,
            prompt="What is Nexon safety rating?",
            response_content="Tata Nexon has a 5-Star Bharat NCAP safety rating.",
            rating="up",
            model_version="qwen_lora_v4"
        )
        db.add(single_up)
        db.commit()

        stats_single = run_dpo_export(dry_run=True)
        assert stats_single["raw_events_scanned"] == 1
        assert stats_single["dpo_pairs_generated"] == 0
        assert stats_single["single_rating_skipped"] == 1

        # 2. Add downvote for SAME prompt (now forms 1 valid DPO pair)
        single_down = MessageFeedback(
            conversation_id=2,
            message_id=2,
            prompt="What is Nexon safety rating?",
            response_content="Nexon has 2 airbags and 3 star rating.",
            rating="down",
            reason_code="incorrect_price",
            model_version="qwen_lora_v4"
        )
        db.add(single_down)
        db.commit()

        stats_paired = run_dpo_export(dry_run=True)
        assert stats_paired["raw_events_scanned"] == 2
        assert stats_paired["dpo_pairs_generated"] == 1
        assert stats_paired["single_rating_skipped"] == 0

    finally:
        db.close()
