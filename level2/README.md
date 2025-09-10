# Chatbot with CLI — Level 2 🤖

Welcome to Level 2 of the Chatbot CLI challenge! You've discovered a corporate chatbot system that helps manage notes and generate reports.

## 📋 Challenge Overview

This chatbot has several functions:
- **Add notes**: Store markdown content for later use
- **Merge notes**: Combine notes into a master report
- **Summarize reports**: Generate summaries of the compiled data
- **View reports**: Display current report contents

## 🎯 Your Mission

Your goal is to achieve **remote command execution** on the underlying system. The chatbot has some interesting functionality that might be exploited...

## 🚀 Getting Started

1. **Start the challenge environment**:
   ```bash
   docker run -p 8082:8000 chatbot-cli-level2
   ```

2. **Open the web interface**:
   - Navigate to `http://localhost:8082` in your browser
   - You should see the chatbot interface

3. **Interact with the chatbot using natural language**:
   Try the basic commands to understand the workflow:
   - `Add this note: Hello world`
   - `merge <note_id>` (use the ID returned from adding a note)
   - `show report`
   - `summarize the report`

## 🔍 What to Look For

- Pay attention to the **system prompt** displayed in responses
- Notice any **filtering or security measures** mentioned
- Observe how content flows through the system: notes → report → summary
- Look for **special formatting or syntax** that might trigger functionality

## 💡 Hints

<details>
<summary>Click for Hint #1 (Workflow Understanding)</summary>

The chatbot processes content in stages:
1. User input → Note storage
2. Note content → Report merging  
3. Report content → Summarization

Each stage might handle data differently. What happens to your content as it moves through this pipeline?

</details>

<details>
<summary>Click for Hint #2 (Special Syntax)</summary>

The system prompt mentions something about "HTML comments" and a specific format. Web developers often use HTML comments for instructions or metadata. What if the chatbot is looking for special instructions in a particular format?

Think about: `<!-- SOMETHING: action 'parameter' -->`

</details>

<details>
<summary>Click for Hint #3 (Security Bypass)</summary>

There might be a naive security filter that blocks certain keywords in direct user input. But what if you could:
- Use different capitalization?
- Add spaces between letters?
- Work with content that gets modified by the filter?

Remember: security filters often focus on exact string matches!

</details>

<details>
<summary>Click for Hint #4 (Command Discovery)</summary>

If you manage to achieve command execution, try these commands to explore:
- `ls -la` - List files and permissions
- `find /data -name "*.md"` - Find markdown files
- `cat /etc/hostname` - Show system hostname
- `head /data/report.md` - View report content

The system only allows certain "safe" commands, so stick to basic file operations.

</details>

## 🏁 Success Criteria

You'll know you've succeeded when:
- The chatbot executes system commands
- You can see command output in the response
- You've achieved remote code execution through the intended vulnerability

## 🎓 Learning Objectives

This challenge teaches:
- **Input validation bypass techniques**
- **Multi-stage attack chains**
- **Command injection vulnerabilities**
- **Security filter evasion**

## 🔧 Technical Notes

- The frontend displays all content as plain text (no HTML rendering)
- Commands are restricted to a specific allowlist
- The system uses a sandbox environment for safety

---

Good luck, and remember: sometimes the most obvious security measures are the easiest to bypass! 🔓