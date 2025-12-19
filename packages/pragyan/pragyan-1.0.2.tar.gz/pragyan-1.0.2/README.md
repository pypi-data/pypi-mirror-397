# Pragyan 🚀

**AI-Powered DSA Question Solver with Video Explanations**

Pragyan is a powerful Python package that helps you understand and solve Data Structures and Algorithms (DSA) problems. It can:

- 📝 Scrape problems from LeetCode, GeeksforGeeks, and other platforms
- 🤖 Analyze and generate solutions using AI (Gemini or Groq)
- 💻 Generate code in 11+ programming languages
- 🎥 Create animated explanation videos using Manim
- 📚 Provide step-by-step explanations with examples

## Features

- **Multi-Platform Support**: Scrape problems from LeetCode, GeeksforGeeks, Codeforces, HackerRank, and more
- **AI-Powered Solutions**: Uses Google Gemini or Groq (free tier) for intelligent solution generation
- **Multiple Languages**: Generate solutions in Python, Java, C++, JavaScript, Go, Rust, and more
- **Video Explanations**: Automatic video generation with Manim animations
- **Concept Explanations**: Learn the underlying concepts and approaches
- **Test Cases**: Auto-generate test cases for validation

## Installation

```bash
pip install pragyan
```

### Additional Requirements

For video generation, you'll need to install Manim dependencies:

**Windows:**
```bash
# Install Manim
pip install manim

# Install additional dependencies (FFmpeg, etc.)
choco install ffmpeg
```

**macOS:**
```bash
pip install manim
brew install ffmpeg
```

**Linux:**
```bash
pip install manim
sudo apt-get install ffmpeg
```

## Quick Start

### Command Line Interface

```bash
# Interactive mode (recommended for first-time users)
pragyan interactive

# Solve from URL
pragyan solve -u https://leetcode.com/problems/two-sum -p gemini -k YOUR_API_KEY

# Solve from text
pragyan solve -t "Given an array of integers, find two numbers that add up to a target" -l python

# Analyze a problem without solving
pragyan analyze https://leetcode.com/problems/two-sum -p gemini -k YOUR_KEY

# List supported languages
pragyan languages
```

### Python API

```python
from pragyan import Pragyan

# Initialize with your API key
pragyan = Pragyan(
    provider="gemini",  # or "groq"
    api_key="YOUR_API_KEY"
)

# Solve from URL
result = pragyan.process(
    "https://leetcode.com/problems/two-sum",
    language="python",
    generate_video=True
)

# Access results
print(result["solution"].code)
print(result["solution"].explanation)
print(f"Video saved to: {result['video_path']}")
```

### Detailed Usage

```python
from pragyan import Pragyan, ProgrammingLanguage, VideoConfig

# Custom configuration
video_config = VideoConfig(
    output_dir="./videos",
    video_quality="high_quality",
    resolution="1080p"
)

pragyan = Pragyan(
    provider="gemini",
    api_key="YOUR_API_KEY",
    video_config=video_config
)

# Scrape a question
question = pragyan.scrape_question("https://leetcode.com/problems/binary-search")

# Analyze the question
analysis = pragyan.analyze(question)
print(f"Topics: {analysis['topics']}")
print(f"Concept: {analysis['main_concept']}")

# Generate solution
solution = pragyan.solve(question, ProgrammingLanguage.JAVA, analysis)

# Print solution details
print(f"Code:\n{solution.code}")
print(f"\nApproach: {solution.approach}")
print(f"Time Complexity: {solution.time_complexity}")
print(f"Space Complexity: {solution.space_complexity}")

# Generate explanation video
video_path = pragyan.generate_video(question, solution, analysis)
print(f"Video saved to: {video_path}")

# Generate test cases
test_cases = pragyan.generate_test_cases(question)
for tc in test_cases:
    print(f"Input: {tc['input']}, Expected: {tc['expected_output']}")
```

## API Keys

Pragyan supports two AI providers (both have free tiers):

### Google Gemini (Recommended)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Use with `provider="gemini"`

### Groq
1. Go to [Groq Console](https://console.groq.com/keys)
2. Create a new API key
3. Use with `provider="groq"`

You can also set the API key as an environment variable:
```bash
export PRAGYAN_API_KEY="your_api_key_here"
```

## Supported Languages

| Language   | Aliases              |
|------------|----------------------|
| Python     | python, py           |
| Java       | java                 |
| C++        | cpp, c++             |
| C          | c                    |
| JavaScript | javascript, js       |
| TypeScript | typescript, ts       |
| Go         | go, golang           |
| Rust       | rust, rs             |
| Kotlin     | kotlin, kt           |
| Swift      | swift                |
| C#         | csharp, c#, cs       |

## Video Generation

The package uses **Manim** (Community Edition) to generate animated explanation videos. Videos include:

1. **Introduction**: Problem title and topics
2. **Problem Overview**: Description and key points
3. **Concept Explanation**: Main algorithm/technique used
4. **Step-by-Step Approach**: Detailed walkthrough
5. **Code Walkthrough**: Syntax-highlighted code with explanations
6. **Example Walkthrough**: Working through an example
7. **Complexity Analysis**: Time and space complexity
8. **Summary**: Key takeaways

### Video Quality Options

- `low_quality`: 480p, faster rendering
- `medium_quality`: 720p, balanced
- `high_quality`: 1080p, best quality

## Project Structure

```
pragyan/
├── src/
│   └── pragyan/
│       ├── __init__.py      # Package entry point
│       ├── main.py          # Main orchestration
│       ├── cli.py           # Command-line interface
│       ├── models.py        # Data models
│       ├── llm_client.py    # AI integrations
│       ├── scraper.py       # Web scraping
│       ├── solver.py        # Solution generation
│       └── video_generator.py # Video creation
├── pyproject.toml           # Package configuration
└── README.md               # This file
```

## Examples

### Example 1: Two Sum Problem

```python
from pragyan import Pragyan

pragyan = Pragyan(provider="gemini", api_key="YOUR_KEY")

result = pragyan.process(
    "https://leetcode.com/problems/two-sum",
    language="python"
)

print(result["solution"].code)
# Output:
# def twoSum(nums, target):
#     seen = {}
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in seen:
#             return [seen[complement], i]
#         seen[num] = i
#     return []
```

### Example 2: Custom Problem Text

```python
from pragyan import Pragyan

pragyan = Pragyan(provider="groq", api_key="YOUR_KEY")

problem_text = """
Given an array of integers, find the maximum subarray sum.

Example:
Input: [-2, 1, -3, 4, -1, 2, 1, -5, 4]
Output: 6
Explanation: The subarray [4, -1, 2, 1] has the maximum sum 6.

Constraints:
- 1 <= array length <= 10^5
- -10^4 <= array[i] <= 10^4
"""

question = pragyan.parse_question(problem_text)
solution = pragyan.solve(question, "cpp")
print(solution.code)
```

### Example 3: Compare Approaches

```python
from pragyan import Pragyan

pragyan = Pragyan(provider="gemini", api_key="YOUR_KEY")

question = pragyan.scrape_question("https://leetcode.com/problems/longest-substring-without-repeating-characters")

comparison = pragyan.compare_approaches(question)

for approach in comparison["approaches"]:
    print(f"\n{approach['name']}")
    print(f"  Time: {approach['time_complexity']}")
    print(f"  Space: {approach['space_complexity']}")
    print(f"  Description: {approach['description']}")

print(f"\nRecommended: {comparison['recommended']}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Manim Community](https://www.manim.community/) for the animation library
- Google Gemini and Groq for AI capabilities
- LangChain for web scraping utilities

---

Made with ❤️ by Kamal
