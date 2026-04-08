# Schema

### users
- telegram_id: integer (pk, fk)
- name: text
- life_context: text
- pain_point: text
- onboard_step: integer (default)
- referral_code: text (unique)
- referred_by: text
- first_msg_at: text
- msg_count: integer (default)
- summary_sent: integer (default)
- morning_sent: integer (default)

### messages
- id: integer (pk)
- telegram_id: integer (fk)
- role: text (required)
- content: text (required)

### analytics
- id: integer (pk)
- event: text (required)
- telegram_id: integer (fk)
- data: text
