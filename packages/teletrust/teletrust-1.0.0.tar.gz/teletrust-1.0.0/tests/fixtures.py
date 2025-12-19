"""
Test Fixtures for MOA Demos
===========================
ISOLATED sample data for testing only — NOT for production.

These samples should NEVER be used for training or validation.
Use opengov.data or real clinical data for that.

Copyright (c) 2025 Michael Ordon.
"""

# =============================================================================
# DEMO SCENARIOS (For run_demo.py)
# =============================================================================

DEMO_SCENARIOS = {
    "routine_billing": {
        "title": "Routine Billing",
        "input": "Hi, I have a question about my copay for the last visit.",
        "expected_zone": "GREEN",
    },
    "crisis_intervention": {
        "title": "Crisis Intervention",
        "input": "I can't take this anymore, I'm thinking about ending it all.",
        "expected_zone": "RED",
    },
    "complex_clinical": {
        "title": "Complex Clinical Query",
        "input": "Patient presents with acute abdominal pain, rule out appendicitis vs diverticulitis.",
        "expected_zone": "GREEN",
    },
}

# =============================================================================
# TOKEN OPTIMIZER SAMPLES (For run_full_demo.py)
# =============================================================================

VERBOSE_PROMPT_SAMPLE = """
In order to provide you with the most comprehensive and accurate response possible,
I would like to take this opportunity to explain the following information in great detail.

As previously mentioned in our earlier correspondence, the patient presents with
symptoms that are consistent with a diagnosis of acute respiratory infection.
At this point in time, it is important to note that the patient has been experiencing
these symptoms for a period of approximately three to five days.

Due to the fact that the patient is currently taking multiple medications, including
but not limited to blood pressure medications and diabetes management medications,
it is of the utmost importance that we carefully consider potential drug interactions
prior to prescribing any new medications for the respiratory infection.
"""

# =============================================================================
# GRAMMAR VALIDATOR SAMPLES
# =============================================================================

GRAMMAR_TRAINING_SAMPLE = ["Q", "T", "H", "T", "Q", "T", "H", "H", "Q"]
GRAMMAR_TEST_VALID = ["T", "H", "Q", "T"]
GRAMMAR_TEST_ANOMALY = ["T", "X", "Q"]  # "X" is unknown state

# =============================================================================
# ESM PHYSICS TEST SAMPLES
# =============================================================================

BOT_TEXT_SAMPLE = "spam spam spam spam " * 50
CHAOS_TEXT_SAMPLE = "".join([chr((i * 17 + 31) % 95 + 32) for i in range(1000)])
HUMAN_TEXT_SAMPLE = """
The patient reports moderate improvement in symptoms since starting the new medication
regimen two weeks ago. Blood pressure readings have stabilized within normal range.
Follow-up appointment scheduled for next month to assess continued progress.
"""
