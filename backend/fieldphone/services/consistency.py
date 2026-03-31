"""Inter-session consistency checking for transcription quality."""

from sqlalchemy.orm import Session

from fieldphone.models.token import Token
from fieldphone.models.transcription import Transcription
from fieldphone.models.audit import AuditFlag, FlagType, FlagSeverity


def check_inter_session(
    db_session: Session,
    orthographic_form: str | None = None,
) -> list[dict]:
    """Find tokens with the same orthographic form but different transcriptions across sessions.
    
    For each normalized orthographic form, get the latest transcription for every token.
    If any two tokens of the same form have different IPA transcriptions, flag them.
    """
    query = db_session.query(Token).filter(Token.normalized_form.isnot(None))
    
    if orthographic_form:
        query = query.filter(Token.normalized_form == orthographic_form)
    
    # Group tokens by normalized form
    tokens = query.all()
    form_groups: dict[str, list[Token]] = {}
    for token in tokens:
        form = token.normalized_form
        if form:
            form_groups.setdefault(form, []).append(token)
    
    conflicts = []
    for form, token_list in form_groups.items():
        if len(token_list) < 2:
            continue
        
        # Get latest transcription for each token
        transcriptions: dict[int, Transcription | None] = {}
        for token in token_list:
            latest = (
                db_session.query(Transcription)
                .filter(Transcription.token_id == token.id)
                .order_by(Transcription.created_at.desc())
                .first()
            )
            transcriptions[token.id] = latest
        
        # Compare all pairs
        items = [(tid, t) for tid, t in transcriptions.items() if t is not None]
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                tid_a, trans_a = items[i]
                tid_b, trans_b = items[j]
                if trans_a.ipa_form != trans_b.ipa_form:
                    conflicts.append({
                        "orthographic_form": form,
                        "token_a_id": tid_a,
                        "token_b_id": tid_b,
                        "ipa_a": trans_a.ipa_form,
                        "ipa_b": trans_b.ipa_form,
                        "session_a_id": next(t.session_id for t in token_list if t.id == tid_a),
                        "session_b_id": next(t.session_id for t in token_list if t.id == tid_b),
                    })
    
    # Create audit flags for new conflicts
    for conflict in conflicts:
        existing = (
            db_session.query(AuditFlag)
            .filter(
                AuditFlag.token_id == conflict["token_a_id"],
                AuditFlag.related_token_id == conflict["token_b_id"],
                AuditFlag.flag_type == FlagType.CONSISTENCY,
                AuditFlag.resolved == False,
            )
            .first()
        )
        if not existing:
            flag = AuditFlag(
                token_id=conflict["token_a_id"],
                related_token_id=conflict["token_b_id"],
                flag_type=FlagType.CONSISTENCY,
                severity=FlagSeverity.MEDIUM,
                description=(
                    f"'{conflict['orthographic_form']}' transcribed as "
                    f"/{conflict['ipa_a']}/ in session {conflict['session_a_id']} "
                    f"but /{conflict['ipa_b']}/ in session {conflict['session_b_id']}"
                ),
                resolved=False,
            )
            db_session.add(flag)
    
    db_session.commit()
    return conflicts


def check_all(db_session: Session) -> list[dict]:
    """Run all consistency checks across the entire database."""
    return check_inter_session(db_session, orthographic_form=None)
