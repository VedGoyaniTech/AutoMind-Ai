import json
import re
import asyncio
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db, SessionLocal
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.chat import ChatMessageSend
from app.schemas.car import CarVariantSummary
from app.repositories.chat_repo import ChatRepository
from app.repositories.car_repo import CarRepository
from app.services.ai.query_analyzer import QueryAnalyzer
from app.services.ai.vector_store import global_vector_store
from app.services.ai.retriever import HybridRetriever
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.llm_provider import get_llm_provider
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat & RAG Engine"])

class UniversalMessageRouter:
    """Semantic Conversation & Intent Classifier for Fast Routing (Sections 1 - 20)"""

    GREETINGS = {
        "hi", "hii", "hiii", "hello", "hey", "heyy", "yo", "hola",
        "good morning", "good afternoon", "good evening", "good night"
    }
    THANKS = {"thanks", "thank you", "thanks a lot", "thank you so much"}
    FAREWELS = {"bye", "goodbye", "see you", "talk later"}
    CONVERSATIONAL = {
        "how are you", "how are you?", "how is it going", "how's it going",
        "what's up", "whatup", "nice", "cool", "great", "okay", "ok", "alright"
    }

    PREFACE_PHRASES = [
        "i have a question", "i have one question", "i have something to ask", "i wanted to ask something",
        "i have so many question", "i hve so many question", "i have so many questions", "i hve so many questions",
        "can i ask something", "can i ask you something", "may i ask you something", "i need to ask you something",
        "i want to ask you something", "i wanted to know something", "i need some help", "can you help me",
        "could you help me", "i need your help", "i have something i want to know", "there's something i want to ask",
        "let me ask you something", "can i ask you one thing", "i want to know something", "i was wondering about something"
    ]

    REAL_QUESTION_INDICATORS = [
        "what", "where", "which", "who", "why", "how", "when", "compare", "vs", "versus",
        "price", "prices", "cost", "list", "top", "best", "safest", "cheapest", "specs", "specifications",
        "lakh", "crore", "under", "below", "suv", "car", "ev", "laptop", "phone", "calculate", "explain", "adas", "ncap"
    ]

    def route(self, message: str) -> dict:
        clean = message.strip().lower()
        clean_nopunct = clean.rstrip("!?.").strip()
        words = clean_nopunct.split()

        # 0. User Self-Introduction & Name Capture (e.g. "my name is Ved", "mera naam rahul hai", "call me X")
        name_patterns = [
            r"(?:my name is|i am|i'm|this is|call me|name's)\s+([A-Za-z]+)",
            r"(?:mera naam|mera name|mujhko|mujhe)\s+([A-Za-z\u0900-\u097F]+)",
            r"(?:maru naam|maru name|hu)\s+([A-Za-z\u0A80-\u0AFF]+)",
            r"(?:you call me|call me a|call me)\s+([A-Za-z]+)"
        ]
        detected_name = None
        for pat in name_patterns:
            m = re.search(pat, message, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().capitalize()
                if cand.lower() not in ["a", "an", "the", "car", "suv", "ev", "here", "ready", "asking", "interested", "looking", "conversation"]:
                    detected_name = cand
                    break

        if detected_name:
            reply = f"Hello {detected_name}! 👋 Great to meet you! Main aage se humari har conversation mein aapko {detected_name} kehkar hi address karunga.\n\nAaj main aapki automotive research, car prices, comparisons, ya specifications me kya help kar sakta hoon?"
            return {
                "type": "CASUAL",
                "reply": reply,
                "user_name": detected_name
            }

        # 0.5. Identity & Bot Capability Questions
        if any(w in clean for w in ["who are you", "what is your name", "tum kaun ho", "aap kaun ho", "tam kaun cho", "who made you", "who created you"]):
            reply = "Main AutoMind AI hoon — aapka intelligent automotive AI research assistant! 🚗 Main aapko car prices, on-road RTO breakdown, EMI calculation, EV vs Petrol comparisons aur detailed specifications me help kar sakta hoon. Aap kisi bhi car ke baare me pooch sakte hain!"
            return {"type": "CASUAL", "reply": reply}

        # 1. Pure Greeting / Thanks / Farewell / Casual Conversation (< 80ms)
        if len(words) <= 5:
            if clean_nopunct in self.GREETINGS or (len(words) <= 3 and any(w in self.GREETINGS for w in words)):
                has_real_req = any(ind in clean for ind in self.REAL_QUESTION_INDICATORS if ind not in ["hey", "hi", "hello"])
                if not has_real_req:
                    return {"type": "CASUAL", "reply": "Hi! 👋 How can I help you today?"}

            if clean_nopunct in self.THANKS or any(t in clean for t in ["thanks", "thank you"]):
                if not any(ind in clean for ind in ["which", "what", "how", "compare"]):
                    return {"type": "CASUAL", "reply": "You're very welcome! 😊 Let me know if you need anything else."}

            if clean_nopunct in self.FAREWELS:
                return {"type": "CASUAL", "reply": "Goodbye! 👋 Have a great day!"}

            if clean_nopunct in self.CONVERSATIONAL:
                return {"type": "CASUAL", "reply": "I'm doing great, thank you! 😊 How can I assist you today?"}

        # 2. Question Prefaces (e.g. "I have a question", "can I ask something?")
        for pref in self.PREFACE_PHRASES:
            if pref in clean:
                after_pref = clean.replace(pref, "").strip(" :,-!?")
                if len(after_pref) > 3 and any(ind in after_pref for ind in self.REAL_QUESTION_INDICATORS):
                    return {"type": "REAL_REQUEST", "actual_request": after_pref}
                elif len(after_pref) <= 3:
                    return {"type": "QUESTION_PREFACE", "reply": "Of course! 😊 What would you like to ask?"}

        # 3. Real Information Request
        actual_req = clean
        for g in ["hey", "hi", "hello", "yo", "please"]:
            if actual_req.startswith(g):
                actual_req = actual_req[len(g):].strip(" ,:-!?")

        return {"type": "REAL_REQUEST", "actual_request": actual_req}


@router.post("/stream")
async def chat_stream(
    payload: ChatMessageSend,
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    msg_text = payload.message.strip()
    import uuid
    req_id = str(uuid.uuid4())

    logger.info(f"[CHAT] request_id={req_id} user_id={user_id} msg='{msg_text[:40]}'")

    init_db = SessionLocal()
    try:
        chat_repo = ChatRepository(init_db)
        clean_title = msg_text.strip().rstrip("!?./\\")
        title_snippet = clean_title[:35].strip() + ("..." if len(clean_title) > 35 else "")
        if not title_snippet:
            title_snippet = "Research Query"

        conv_id = payload.conversation_id
        if not conv_id:
            conv = chat_repo.create_conversation(user_id=user_id, title=title_snippet)
            conv_id = conv.id
        else:
            conv = chat_repo.get_conversation_by_id(conv_id, user_id)
            if not conv:
                conv = chat_repo.create_conversation(user_id=user_id, title=title_snippet)
                conv_id = conv.id
            elif conv.title in ["Car Research Session", "New Car Research Session", "New Chat", "Untitled"]:
                chat_repo.update_conversation_title(conv_id, title_snippet)

        chat_repo.add_message(conversation_id=conv_id, role="user", content=msg_text)
    finally:
        init_db.close()

    async def event_generator() -> AsyncGenerator[str, None]:
        gen_db = SessionLocal()
        import time
        t_start = time.perf_counter()
        try:
            gen_chat_repo = ChatRepository(gen_db)
            gen_car_repo = CarRepository(gen_db)

            def format_event(event_type: str, data: dict) -> str:
                data["event_type"] = event_type
                data["conversation_id"] = conv_id
                return f"data: {json.dumps(data)}\n\n"

            # 1. FAST SEMANTIC ROUTER FOR CASUAL & PREFACE MESSAGES (< 10ms)
            msg_router = UniversalMessageRouter()
            route_res = msg_router.route(msg_text)

            if route_res["type"] in ["CASUAL", "QUESTION_PREFACE"]:
                t_route = time.perf_counter()
                logger.info(f"[PERF] Fast Router Matched ({route_res['type']}): {(t_route - t_start)*1000:.2f}ms")
                fast_reply = route_res["reply"]
                yield format_event("token", {"token": fast_reply})
                try:
                    gen_chat_repo.add_message(conversation_id=conv_id, role="assistant", content=fast_reply)
                except Exception as db_err:
                    logger.warning(f"[ChatAPI] Could not save casual assistant message to DB: {db_err}")
                yield format_event("complete", {"message": "Fast response complete."})
                return

            actual_msg_text = route_res.get("actual_request", msg_text)

            llm = get_llm_provider()

            # 2. FAST ROUTER FOR NON-AUTOMOTIVE / GENERAL QUERIES
            if not llm._is_automotive_query(actual_msg_text):
                t_gen_start = time.perf_counter()
                logger.info(f"[PERF] Non-Automotive Query Router: {(t_gen_start - t_start)*1000:.2f}ms")
                accumulated_text = ""
                for token in llm.stream(actual_msg_text, ""):
                    accumulated_text += token
                    yield format_event("token", {"token": token})
                try:
                    gen_chat_repo.add_message(conversation_id=conv_id, role="assistant", content=accumulated_text)
                except Exception as db_err:
                    logger.warning(f"[ChatAPI] Could not save general assistant message to DB: {db_err}")
                yield format_event("complete", {"message": "General response complete."})
                return

            # 3. AUTOMOTIVE RESEARCH PIPELINE
            t_auto_start = time.perf_counter()
            yield format_event("progress", {"stage": "understanding", "message": "Analyzing automotive query constraints..."})

            try:
                analyzer = QueryAnalyzer()
                query_analysis = analyzer.analyze(msg_text)
                logger.info(f"[STAGE:query_analysis] OK req_id={req_id}")
            except Exception as e:
                logger.exception(f"[STAGE:query_analysis] FAILED req_id={req_id}: {e}")
                raise

            yield format_event("progress", {"stage": "searching", "message": "Searching database & trusted automotive web index..."})

            try:
                retriever = HybridRetriever(gen_db, global_vector_store)
                docs, sources, web_results = retriever.retrieve(
                    prompt=msg_text,
                    filter_schema=query_analysis["filter_schema"]
                )
                logger.info(f"[STAGE:retriever] OK docs={len(docs)} web={len(web_results)} req_id={req_id}")
            except Exception as e:
                logger.exception(f"[STAGE:retriever] FAILED req_id={req_id}: {e}")
                raise

            # Execute Vehicle Search Pipeline asynchronously with strict 2.0s deadline
            merged_dict = None
            try:
                from app.services.vehicle_search import VehicleSearchOrchestrator
                vehicle_orchestrator = VehicleSearchOrchestrator()
                merged_obj = await asyncio.wait_for(
                    asyncio.to_thread(vehicle_orchestrator.search_vehicle, msg_text),
                    timeout=2.0
                )
                merged_dict = merged_obj.model_dump() if merged_obj else None
            except Exception as v_err:
                logger.warning(f"[STAGE:vehicle_search] deadline/fallback req_id={req_id}: {v_err}")
                merged_dict = None

            try:
                context_builder = ContextBuilder()
                context_text = context_builder.build_context(
                    docs=docs,
                    parsed_constraints=query_analysis["parsed_constraints"],
                    web_results=web_results,
                    merged_result=merged_dict
                )
                logger.info(f"[STAGE:context_builder] OK len={len(context_text)} req_id={req_id}")
            except Exception as e:
                logger.exception(f"[STAGE:context_builder] FAILED req_id={req_id}: {e}")
                raise

            # Prepend recent user queries for follow-up context continuity
            try:
                recent_msgs = gen_chat_repo.get_messages(conv_id)
                user_history = [m.content for m in recent_msgs[-4:] if m.role == "user" and m.content != msg_text]
                if user_history:
                    context_text = f"PREVIOUS_USER_QUERIES: {' | '.join(user_history)}\n\n" + context_text
                logger.info(f"[STAGE:history] OK history_msgs={len(user_history)} req_id={req_id}")
            except Exception as e:
                logger.warning(f"[STAGE:history] SKIPPED req_id={req_id}: {e}")

            yield format_event("progress", {"stage": "generating", "message": "Generating AI response..."})

            accumulated_text = ""
            t_first_token = None
            try:
                for token in llm.stream(msg_text, context_text):
                    if t_first_token is None:
                        t_first_token = time.perf_counter()
                        logger.info(f"[STAGE:stream] first_token req_id={req_id} latency={(t_first_token - t_start)*1000:.0f}ms")
                    accumulated_text += token
                    yield format_event("token", {"token": token})
                logger.info(f"[STAGE:stream] COMPLETE req_id={req_id} chars={len(accumulated_text)}")
            except Exception as e:
                logger.exception(f"[STAGE:stream] FAILED req_id={req_id}: {e}")
                raise


            # Save assistant message into DB (metadata kept for history)
            sources_data = [s.model_dump() for s in sources]
            top_variant_ids = [d["car_variant_id"] for d in docs[:5] if "car_variant_id" in d]
            car_variants = gen_car_repo.get_variants_by_ids(top_variant_ids)
            cars_data = []
            for v in car_variants:
                try:
                    m_name = v.car_model.manufacturer.name if (v.car_model and getattr(v.car_model, 'manufacturer', None)) else "Automotive Manufacturer"
                    model_n = v.car_model.name if v.car_model else "Vehicle Model"
                    body_t = v.car_model.body_type if v.car_model else "SUV"
                    cars_data.append(CarVariantSummary(
                        id=v.id,
                        manufacturer_name=m_name,
                        model_name=model_n,
                        variant_name=v.variant_name or "Standard Variant",
                        model_year=v.model_year or 2024,
                        body_type=body_t,
                        fuel_type=v.fuel_type or "Petrol",
                        transmission=v.transmission or "Manual",
                        ex_showroom_price=v.ex_showroom_price or "Market Pricing",
                        estimated_on_road_price=v.estimated_on_road_price or "Market Pricing",
                        currency=v.currency or "INR",
                        combined_mileage=v.combined_mileage or "15.0 kmpl",
                        electric_range=v.electric_range,
                        seating_capacity=v.seating_capacity or 5,
                        airbags=v.airbags or 6,
                        safety_rating=v.safety_rating or "5-Star NCAP",
                        image_url=v.image_url
                    ).model_dump())
                except Exception as card_err:
                    logger.warning(f"[ChatAPI] Skipping car card due to missing DB field: {card_err}")

            from app.services.vehicle_media import get_vehicle_gallery_for_query
            gallery_data = get_vehicle_gallery_for_query(msg_text) or get_vehicle_gallery_for_query(accumulated_text[:200])
            if gallery_data:
                yield format_event("gallery", gallery_data)

            # Check for Pricing / EMI Quote Intent & Dispatch Pricing Event
            pricing_quote_dict = None
            if any(w in msg_text.lower() for w in ["on-road", "on road", "price", "rto", "tax", "emi", "down payment", "kitna", "keemat", "કિંમત"]):
                try:
                    from app.services.agentic.tools.pricing_quote import execute_pricing_quote
                    from app.services.pricing.city_mapping import extract_city_from_text
                    
                    detected_city, detected_state = extract_city_from_text(msg_text)
                    pq_res = execute_pricing_quote(
                        db=gen_db,
                        city=detected_city or "Ahmedabad",
                        state_code=detected_state,
                        model=msg_text,
                        fuel_type="petrol"
                    )
                    if pq_res.success and pq_res.data:
                        pricing_quote_dict = pq_res.data
                        yield format_event("pricing_quote", pricing_quote_dict)
                except Exception as p_err:
                    logger.warning(f"[ChatAPI] Pricing tool notice: {p_err}")

            meta = {
                "sources": sources_data,
                "cars": cars_data,
                "gallery": gallery_data,
                "pricing_quote": pricing_quote_dict,
                "parsed_constraints": query_analysis["parsed_constraints"]
            }
            try:
                saved_msg = gen_chat_repo.add_message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=accumulated_text,
                    metadata=meta
                )
                msg_id = saved_msg.id if saved_msg else None
            except Exception as db_err:
                logger.warning(f"[ChatAPI] Could not save assistant message to DB: {db_err}")
                msg_id = None

            # Send complete event with message_id for feedback actions
            yield format_event("complete", {
                "message": "Response generation complete.",
                "message_id": msg_id
            })

        except Exception as err:
            logger.exception(f"[CHAT GENERATION ERROR] request_id={req_id} conv_id={conv_id} provider=NvidiaNIM/GroundedLLM: {err}")
            yield format_event("error", {
                "message": "An error occurred while generating the response. Please try again.",
                "request_id": req_id
            })
        finally:
            gen_db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": req_id
        }
    )
