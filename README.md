# 🧠 AI-Agent (Mini-Cursor)

A sample project that turns a **Google Gemini** LLM into a small coding agent.
The bundled calculator app is just a sandbox; the real goal is to experiment with **agentic, tool-calling workflows**:

1. **Inspect** a codebase (`get_file_content`, `get_files_info`)
2. **Modify** it in-place (`write_file`)
3. **Execute & verify** changes (`run_python_file`)
4. **Iterate** until the task is complete

&nbsp;

## Why this repo exists

| Goal | What you’ll learn |
|------|-------------------|
| Build a **feedback-loop agent** | Plan → call → observe → plan again |
| Safely expose Python & FS to an LLM | Guardrails, working directory scoping |
| Practice automated bug-fixing | Precedence bug in the sample calculator |
| Extend to tougher tasks | Refactors, new features, alt models/providers |

---

## 🗂️ Project Structure


.
├── calculator/                  Sample target app
│   ├── main.py                  Expression CLI
│   ├── pkg/
│   │   ├── calculator.py        Eval logic (precedence bug!)
│   │   └── render.py            ASCII renderer
│   └── tests.py                 9 unit tests
├── functions/                   Tool layer for the agent
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python.py
├── main.py                      Agent driver script
├── requirements.txt             Dependencies (google-genai, python-dotenv)
└── .env                         GEMINI_API_KEY (git-ignored)


⸻

## ⚙️ Quick Start

# clone & install
git clone https://github.com/<you>/ai-agent.git
cd ai-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# add your key
echo 'GEMINI_API_KEY="your_api_key_here"' > .env

# reproduce the bug (optional)
python calculator/main.py "3 + 7 * 2"   # → 20  (wrong)

# run the agent to auto-fix
python main.py "fix the bug: 3 + 7 * 2 shouldn't be 20" --verbose

The agent will:
	1.	List files →
	2.	Read pkg/calculator.py →
	3.	Patch the operator precedence →
	4.	Run tests (run_python_file tests.py) →
	5.	Print “Ran 9 tests” ✓

⸻

## 🛠️ How the Agent Works

flowchart TD
  A[User prompt] --> B[Gemini LLM]
  B --function_call--> C[Tool dispatcher<br/>call_function()]
  C -->|I/O| D[Python FS / subprocess]
  D --> C -->|function_response| B
  B --> E[Plain-text answer]

	•	GenerateContentConfig.system_instruction → tells Gemini what tools exist
	•	Gemini returns function_call objects → driver executes & feeds results back as tool messages
	•	Loop ≤ 20 iterations → stop when Gemini returns plain text

⸻

## - Extending The Sample -

	•	Harder bugs – e.g. division-by-zero, parentheses, floating-point edge cases
	•	Refactor – ask the agent to extract helpers or add logging
	•	New features – exponent ^, modulo %, memory store, etc.
	•	Other models – swap Gemini for GPT-4o, Claude 3, open-source Llama models
	•	Additional tools – git commits, HTTP fetch, database queries
	•	Different codebases – clone any project, commit first, let the agent hack


⚠️ Safety: This agent can read & write files and run Python.
Always sandbox, use a throwaway repo, and commit before experimenting.

⸻

## 📚 Resources
	•	Gemini Function-Calling Docs → https://ai.google.dev/gemini-api/docs/function-calling
	•	LangChain / CrewAI – higher-level agent tooling

