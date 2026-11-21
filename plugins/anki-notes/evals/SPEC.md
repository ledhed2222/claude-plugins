# anki-notes eval spec

What the [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals.md) suite in this folder tests, and what counts as passing. The case list below is generated from the case files by `gen_spec.py`; everything else here is written by hand.

## What it protects

The skill's job is to turn what Claude teaches into cards worth studying. Each case reproduces one mistake found while reviewing real cards by hand, so a passing suite means none of those mistakes came back.

## How a run works

1. A fresh, headless Claude Code session starts with only this plugin and `ankimcp` loaded.
2. The Anki server is replaced by a mock (`mocks/anki/`): every Anki tool call gets a canned reply, and no real deck is touched. `_tools.json` holds the real server's tool descriptions so Claude sees the real tools.
3. The case's user message is sent, and Claude answers as it normally would.
4. Each grader checks one thing about that run and passes or fails.

Every case runs 3 times with the plugin and 3 times without it, on the plain model, to show what the plugin adds. All graders here apply to the with-plugin runs only.

## Scoring and the pass bar

- A run's score is the share of its graders that passed (all graders weigh the same). A case's score is the average over its runs.
- **Kinds of grader:**
  - **tool check:** whether an Anki tool was called, and how often.
  - **text search:** a pattern that must never appear in what Claude sent to the Anki tools. It sees every call, but understands nothing.
  - **LLM judge:** a model applies a plain-English rule and votes PASS or FAIL three times; the majority wins. It understands nuance, but sees only the first and last 12 messages of a transcript, which is why some rules also have a text search.
- **Pass bar: 1.00** for every case, which is the harness default: every grader passes in every run.
- The suite costs about $6 a run, so it runs by hand, not in CI. CI only checks that this file matches the cases.

## Not covered

- Queuing cards to the Anki inbox doc (the eval sessions have no docs tools).
- Whether the LLM judges agree with a human reviewer (see Ideas in the plugin README).
- `scripts/apply_stage.py` and the real AnkiMCP server.

## Running and updating

From the repo root:

```
claude plugin eval . --trust-plugin                    # the whole suite
claude plugin eval . --trust-plugin --case <name>      # one case
python3 -I plugins/anki-notes/evals/gen_spec.py        # after changing a case: regenerate the list below
```

## Cases

<!-- generated:start -->
| case | what it checks |
|---|---|
| [`ask-mode-deck`](#ask-mode-deck) | In a deck whose charter says Ask, cards are offered, not added. |
| [`coined-term`](#coined-term) | A term coined in the session must not become a card's premise or answer. |
| [`doing-not-teaching`](#doing-not-teaching) | Helping with a task, as opposed to teaching a concept, makes no cards. |
| [`metric-concept`](#metric-concept) | Teaching an AI-engineering concept in an Automatic deck should produce one-fact, self-contained cards with no arithmetic drills. |
| [`missing-prereq`](#missing-prereq) | A card may only rely on concepts the deck already teaches; missing ones are taught first or flagged. |
| [`name-the-options`](#name-the-options) | A two-option idea becomes a card that names both options in its question. |
| [`project-specific`](#project-specific) | Lessons learned in a project become general cards without the project's names. |

### ask-mode-deck

In a deck whose charter says Ask, cards are offered, not added.

**User message:**

> In Spanish, what's the difference between ser and estar?

**Deck:** the shared mock deck, with this case's own `get_deck_description`.

| grader | kind | passes when |
|---|---|---|
| `no-cards` | tool check | `add_notes` is never called |
| `offers-cards` | LLM judge, reads the final reply | PASS if the reply answers the question and offers to make Anki cards (in any wording), without claiming any were added. FAIL if it says cards were added, or never mentions making cards. |

### coined-term

A term coined in the session must not become a card's premise or answer.

**User message:**

> On my team we've started calling the run-to-run wobble in eval scores the "jitter band". Explain why a prompt change that gains 2 points might not be real when reruns of an unchanged prompt move the score by 3 points.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-coined-term-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `jitter band` (case-insensitive) |
| `no-coined-term` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card uses the phrase "jitter band" (in its question, answer or cloze), and the lesson is stated in plain words, such as run-to-run variation. FAIL if any card uses "jitter band", or asks for it as a term to recall. |

### doing-not-teaching

Helping with a task, as opposed to teaching a concept, makes no cards.

**User message:**

> My tmux status bar shows the time in UTC instead of my local time. What do I put in tmux.conf to fix it?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `no-cards` | tool check | `add_notes` is never called |

### metric-concept

Teaching an AI-engineering concept in an Automatic deck should produce one-fact, self-contained cards with no arithmetic drills.

**User message:**

> Can you explain precision and recall for a classifier? I get them mixed up. A worked example with numbers would help.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-arithmetic-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `TP *= *[0-9]` (case-insensitive) |
| `no-arithmetic` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card asks the learner to compute a value from numbers (for example "TP = 8, FP = 2: what is precision?"). FAIL if any card is an arithmetic drill. A card may still contain a formula, as long as it tests what the formula means rather than asking for a calculation. |
| `one-fact-per-card` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card's answer (Back, or each cloze blank) is one fact that can be recalled exactly: a word, a number, or one short clause, with any context in an optional Why/Example line. FAIL if any card's answer packs two or more separate facts, a list, or more than one sentence of explanation. |
| `self-contained` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card makes sense on its own, shuffled among hundreds of others months later: each term it relies on is either standard in the field or defined in the card, and the question names its options when there are only two or three. FAIL if any card relies on wording or context from the conversation or from another card (for example "which kind?" or "the example above"), or is a telegraphic fragment rather than a complete question. |

### missing-prereq

A card may only rely on concepts the deck already teaches; missing ones are taught first or flagged.

**User message:**

> Explain what an F1 score is, and why it uses a harmonic mean instead of an ordinary average.

**Deck:** the shared mock deck, with this case's own `find_notes`.

| grader | kind | passes when |
|---|---|---|
| `prereqs-handled` | LLM judge, reads the transcript | The deck the cards go into is empty: its find_notes search returned no cards, so it does not yet teach precision, recall or what a harmonic mean is. PASS if the cards added include ones that introduce the concepts the F1 cards rely on (precision, recall, and the harmonic mean, or whichever of these the F1 cards use) before or alongside the F1 cards, OR if the reply clearly tells the user that those prerequisite cards are missing and offers to add them. FAIL if F1 cards rely on precision, recall or the harmonic mean without any card introducing them and without flagging the gap. |

### name-the-options

A two-option idea becomes a card that names both options in its question.

**User message:**

> When should an eval use a code-based check, and when an LLM judge?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `names-options` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card that contrasts two or three options names all of them in its own question or cloze text (for example "...: code or an LLM judge?"), so it works without any other card. FAIL if a card asks "which kind?" or similar without naming the options, or depends on another card to know what the options are. |

### project-specific

Lessons learned in a project become general cards without the project's names.

**User message:**

> At Acme Health we built a module called packet-segmenter that splits each faxed bundle in the SNF-2025 corpus into its separate documents before extraction runs. Explain why that splitting step matters for extraction accuracy.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-project-names-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `acme\|packet-segmenter\|snf-2025` (case-insensitive) |
| `no-project-names` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card mentions Acme Health, packet-segmenter, SNF-2025, or any other name specific to this one project, while still teaching the general lesson (for example, that splitting a bundled file into its documents helps extraction). FAIL if any card contains one of those project names. |
<!-- generated:end -->
