# Git Interviewer 🎤

A pre-commit hook that _interviews you_ about your code before letting you commit.

Git Interviewer acts as a technical interviewer living in your terminal. Before each commit, it analyzes your staged changes using Google Gemini, generates a relevant question based on a selected "persona", and requires a meaningful answer.

It forces deeper understanding, intentional commits, and better engineering discipline—but in a fun way.

## 🚀 Features

- **AI-Powered Analysis**: Uses Google Gemini to understand your exact code changes.
- **Multiple Personas**: Choose from `nice`, `grumpy`, `systems` architect, or startup `founder`.
- **Interactive Hook**: Blocks the commit until you provide a satisfactory answer.
- **Zero Config Overhead**: Settings stored in your standard `git config`.

Most developers commit code too quickly:

- without thinking about design decisions
- without explaining intent
- without validating risks
- without reflecting on tradeoffs

`pip install git-interviewer`

## 🛠️ Usage

### 1. Initialize the Hook

Go to your git repository and run:

```bash
git-interviewer init
```

This installs the pre-commit hook in `.git/hooks/pre-commit`.

### 2. Set your API Key

You need a Google Gemini API key (it's free tier is generous). [Get one here](https://aistudio.google.com/app/apikey).

```bash
export GEMINI_API_KEY="your_api_key_here"
```

_(Add this to your `~/.zshrc` or `~/.bashrc` to make it permanent)_

### 3. Commit Code

Stage your changes and commit normally:

```bash
git add .
git commit -m "refactor login logic"
```

The interviewer will pop up:

```text
🎤 Git Interviewer (systems mode)
Analyzing changes...

Interviewer:
> I see you added a new dependency. How does this impact our cold-start time?

Your Answer:
> It's lazy loaded, so impact is negligible.
```

### 4. Changing Personas

Switch the personality of your interviewer:

```bash
# List modes
git-interviewer mode

# Switch to 'grumpy' (saves to local git config)
git-interviewer mode grumpy
```

**Available Modes:**

- `nice`: Supportive and clarifying.
- `grumpy`: Cynical, picky senior dev.
- `systems`: Focuses on scale, risk, and reliability.
- `founder`: Focuses on business value and speed.

## ⚡ Bypass

In a hurry? You can skip the interview using the standard git flag:

```bash
git commit --no-verify -m "urgent fix"
```

## 🤝 Contributing

Issues and PRs are welcome!

## 📄 License

MIT
