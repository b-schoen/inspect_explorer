# Inspect Python Library Guide

Inspect is a Python library designed for creating and managing evaluations of large language models (LLMs). It offers a structured approach to defining tasks, utilizing solvers and tools, handling errors, and scoring model outputs. This guide provides a concise overview of Inspect's core functionalities, enabling users and AI models to effectively leverage the library for comprehensive model evaluations.

## Table of Contents

- [Inspect Python Library Guide](#inspect-python-library-guide)
  - [Table of Contents](#table-of-contents)
  - [Core Components](#core-components)
    - [Tasks](#tasks)
    - [Datasets](#datasets)
    - [Solvers](#solvers)
    - [Scorers](#scorers)
    - [Tools](#tools)
  - [Sample Preservation](#sample-preservation)
  - [Errors and Retries](#errors-and-retries)
  - [Concurrency](#concurrency)
  - [Agents](#agents)
  - [Logging](#logging)
  - [Extensions](#extensions)
  - [Models](#models)
  - [Using Inspect in Code](#using-inspect-in-code)
  - [Conclusion](#conclusion)

## Core Components

### Tasks

**Class** `inspect_ai.Task`

Tasks are the fundamental units of evaluation in Inspect. Each task encapsulates a dataset, a plan of solvers, a scorer, and configuration settings.

- **Attributes:**
  - `dataset`: The collection of samples to evaluate.
  - `plan`: A sequence of solvers that define how each sample is processed.
  - `scorer`: Determines how model outputs are evaluated against targets.
  - `config`: Configuration settings for generation and evaluation behaviors.

- **Usage Example:**

  ```python
  from inspect_ai import Task, task
  from inspect_ai.dataset import json_dataset
  from inspect_ai.scorer import model_graded_fact
  from inspect_ai.solver import generate, system_message

  @task
  def security_guide():
      return Task(
          dataset=json_dataset("security_guide.jsonl"),
          plan=[system_message("system.txt"), generate()],
          scorer=model_graded_fact(),
      )
  ```

### Datasets

**Function** `inspect_ai.dataset.json_dataset`

Inspect supports various dataset formats, including CSV, JSON, and JSON Lines, as well as integration with Hugging Face datasets.

- **Parameters:**
  - `path`: Path or URI to the dataset file.
  - `sample_fields`: Defines how dataset fields map to `Sample` attributes.
  - `split`: (Hugging Face) Specifies the dataset split (e.g., train, test).
  - `trust`: (Hugging Face) Allows execution of dataset loading code from trusted sources.

- **Usage Example:**

  ```python
  from inspect_ai.dataset import FieldSpec, json_dataset

  def record_to_sample(record):
      return Sample(
          input=record["question"],
          target=record["answer"],
          id=record["question_id"],
          metadata={"difficulty": record["level"]}
      )

  dataset = json_dataset("quiz.jsonl", sample_fields=record_to_sample)
  ```

### Solvers

**Function** `inspect_ai.solver.generate`

Solvers define the processing steps applied to each sample in a task. Inspect provides built-in solvers and supports custom solver implementations.

- **Built-In Solvers:**
  - `system_message()`: Adds a system prompt to guide model behavior.
  - `chain_of_thought()`: Encourages models to provide reasoning steps.
  - `generate()`: Invokes the model to generate outputs.
  - `self_critique()`: Uses the model to critique its own outputs.
  - `multiple_choice()`: Handles multiple-choice questions.

- **Creating Custom Solvers:**

  ```python
  from inspect_ai.solver import Solver, solver
  from inspect_ai.dataset import TaskState

  @solver
  def custom_solver():
      async def solve(state: TaskState, generate: Generate) -> TaskState:
          # Custom processing logic
          return state
      return solve
  ```

- **Usage Example:**

  ```python
  @task
  def mathematics():
      return Task(
          dataset=json_dataset("math_problems.jsonl"),
          plan=[chain_of_thought(), generate()],
          scorer=model_graded_fact(),
      )
  ```

### Scorers

**Function** `inspect_ai.scorer.model_graded_fact`

Scorers evaluate the quality of model outputs against predefined targets using various strategies, including model-graded assessments.

- **Built-In Scorers:**
  - `includes()`: Checks if the target appears in the model output.
  - `match()`: Verifies if the model output matches the target at specific positions.
  - `model_graded_fact()`: Utilizes another model to assess factual accuracy of outputs.

- **Creating Custom Scorers:**

  ```python
  from inspect_ai.scorer import scorer, Score, Target

  @scorer
  def custom_scorer():
      async def score(state: TaskState, target: Target) -> Score:
          # Custom scoring logic
          return Score(value="C" if condition else "I")
      return score
  ```

- **Usage Example:**

  ```python
  @task
  def reasoning():
      return Task(
          dataset=json_dataset("reasoning_tasks.jsonl"),
          plan=[generate()],
          scorer=includes(),
      )
  ```

### Tools

**Decorator** `inspect_ai.tool.tool`

Tools extend Inspect's capabilities by allowing models to perform specific functions, such as executing code or searching the web.

- **Built-In Tools:**
  - `bash()`: Executes shell commands within a sandboxed environment.
  - `python()`: Runs Python code within a sandbox.
  - `web_search()`: Performs web searches using specified APIs.

- **Creating Custom Tools:**

  ```python
  from inspect_ai.tool import tool, ToolError

  @tool
  def add_numbers():
      async def execute(x: int, y: int) -> int:
          """Add two integers."""
          return x + y
      return execute
  ```

- **Usage Example:**

  ```python
  @task
  def addition_problem():
      return Task(
          dataset=[Sample(input="What is 2 + 3?", target=["5"])],
          plan=[use_tools(add_numbers()), generate()],
          scorer=match(numeric=True),
      )
  ```

## Sample Preservation

**Section:** `Sample Preservation`

Inspect allows reusing completed samples from previous tasks to save time and resources. This requires stable unique identifiers (`id`) for each sample.

- **ID Management:**
  - **Explicit `id` Field:** Define an `id` within each sample.
  - **Auto-Incrementing `id`:** Let Inspect assign `id`s automatically, but avoid dataset shuffling to ensure consistency.

- **Max Samples:**
  - Controls the number of samples processed concurrently.
  - Default: `max_connections + 1` (usually 11).
  - Balances throughput with frequency of log writes and recoverable samples.

- **Usage Recommendations:**
  - Prefer explicit `id` fields if dataset shuffling is essential.
  - Adjust `max_samples` based on concurrency needs and recovery requirements.

## Errors and Retries

**Section:** `Errors and Retries`

Inspect handles errors gracefully, allowing tasks to be retried while preserving completed samples.

- **Error Handling:**
  - **Expected Errors:** Such as `PermissionError`, `TimeoutError`, etc., can be caught and reported to the model for potential recovery.
  - **Unexpected Errors:** Lead to sample failure without model intervention.

- **Retry Mechanism:**
  - **Commands:**
    - Shell: `inspect eval-retry <log_file>`
    - Python: `eval_retry("<log_file>")`
  - **Constraints:**
    - Applicable only to tasks created with `@task` decorators.
    - Creates a new log file without overwriting the original.

- **Usage Example:**

  ```python
  log = eval(my_task)[0]
  if log.status != "success":
      eval_retry(log, max_connections=3)
  ```

## Concurrency

**Section:** `Concurrency`

Inspect employs a highly parallel asynchronous architecture to maximize evaluation throughput while respecting rate limits and resource constraints.

- **Model Connections:**
  - **`max_connections`:** Limits concurrent API connections (default: 10).
  - **Rate Limits:** Adjust `max_connections` to align with provider limits to avoid excessive retries due to rate limiting.

- **Parallel Tasks and Models:**
  - Run multiple tasks or evaluate multiple models in parallel to utilize available connections efficiently.
  - Example: Evaluating a suite of tasks against several models concurrently.

- **Subprocess Management:**
  - Use `subprocess()` for executing external processes without blocking.
  - **`max_subprocesses`:** Controls the number of concurrent subprocesses (default based on CPU count).

- **Best Practices:**
  - Leverage `asyncio.gather()` to handle parallel asynchronous operations within solvers, tools, and scorers.
  - Use `concurrency()` context managers to manage access to external APIs within custom components.

## Agents

**Section:** `Agents`

Agents in Inspect combine planning, memory, and tool usage to tackle complex, multi-turn tasks.

- **Built-In Agent: `basic_agent()`:**
  - Implements a ReAct-style tool loop.
  - Supports retries and prompts continuation if stuck.
  - **Usage Example:**

    ```python
    from inspect_ai.solver import basic_agent, system_message
    from inspect_ai.tool import bash, python

    @task
    def ctf_challenge():
        return Task(
            dataset=read_ctf_dataset(),
            plan=basic_agent(
                init=system_message("You are a CTF participant."),
                tools=[bash(timeout=180), python(timeout=180)],
                max_attempts=3,
            ),
            scorer=includes(),
            max_messages=30,
            sandbox="docker",
        )
    ```

- **Custom Agents:**
  - Create tailored tool loops and state management.
  - Utilize `Store` for shared state across solvers and tools.
  - **Example:**

    ```python
    from inspect_ai.solver import plan, Store

    @plan
    def custom_agent():
        async def solve(state: TaskState, generate: Generate) -> TaskState:
            # Custom reasoning and tool usage
            return state
        return solve
    ```

- **Integration with External Libraries:**
  - Adapt agents from frameworks like LangChain.
  - Bridge Inspect's model API with external agent interfaces for advanced functionalities.

## Logging

**Section:** `Logging`

Logging in Inspect provides insights into evaluation processes, facilitating debugging and analysis.

- **Eval Logs:**
  - Stored in JSON format within the specified `log_dir`.
  - Accessible via the Inspect Log Viewer for interactive exploration.

- **Logging Levels:**
  - Controlled via `INSPECT_LOG_LEVEL` or `--log-level`.
  - Common levels: `info`, `warning`, `error`.

- **Python Logging Integration:**
  - Use Python's `logging` module to emit logs.
  - Logs are captured and included in eval logs.
  - **Usage Example:**

    ```python
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Starting evaluation task.")
    ```

- **External Log Files:**
  - Specify `INSPECT_PY_LOGGER_FILE` to write logs to an external file.
  - Useful for integrating with other tools or conducting detailed analyses.

## Extensions

**Section:** `Extensions`

Inspect's modular design allows for the integration of additional functionalities through extensions.

- **Model API Extensions:**
  - Support additional language model providers.
  - Implement by subclassing `ModelAPI` and registering via setuptools entry points.

- **Sandbox Environment Extensions:**
  - Integrate alternative sandboxing mechanisms beyond Docker.
  - Subclass `SandboxEnvironment` and define lifecycle methods.

- **Custom Filesystems:**
  - Extend dataset access to diverse storage backends using fsspec-compatible filesystems.
  - Register custom filesystems through setuptools entry points.

- **Usage Example:**

  ```python
  # Registering a custom model provider
  @modelapi(name="custom")
  def custom_provider():
      from .custom_model import CustomModelAPI
      return CustomModelAPI
  ```

## Models

**Section:** `Models`

Inspect supports various language model providers, enabling evaluation across different platforms.

- **Supported Providers:**
  - **OpenAI:** `openai/gpt-4`
  - **Anthropic:** `anthropic/claude-3`
  - **Google Gemini:** `google/gemini-1.0-pro`
  - **Mistral:** `mistral/mistral-large-latest`
  - **Hugging Face:** `hf/meta-llama/Llama-2-7b-chat-hf`
  - **vLLM:** `vllm/meta-llama/Llama-2-7b-chat-hf`
  - **TogetherAI**, **AWS Bedrock**, **Azure AI**, **Groq**, **Cloudflare**

- **Model Configuration:**
  - **Base URL:** Customize API endpoints using environment variables.
  - **Concurrency Settings:** Adjust `max_connections` and related parameters to align with provider rate limits.

- **Usage Example:**

  ```bash
  inspect eval task.py --model openai/gpt-4
  ```

- **Helper Models:**
  - Facilitate advanced scoring and grading by leveraging auxiliary models within evaluations.
  - Configure separately from evaluation models for specialized tasks like self-critique or fact-checking.

## Using Inspect in Code

**Section:** `Using Inspect in Code`

Integrate Inspect's functionalities programmatically within Python scripts or applications for dynamic and automated evaluations.

- **Running Evaluations:**

  ```python
  from inspect_ai import eval, task

  @task
  def sample_task():
      return Task(
          dataset=json_dataset("sample.jsonl"),
          plan=[generate()],
          scorer=includes(),
      )

  # Execute evaluation
  logs = eval("sample_task.py", model="openai/gpt-4")
  ```

- **Analyzing Logs:**

  ```python
  from inspect_ai.log import list_eval_logs, read_eval_log

  # List all logs
  logs = list_eval_logs()

  # Read a specific log
  log = read_eval_log("logs/sample_task_2024-04-27.json")
  
  if log.status == "success":
      # Process successful log
      print(log.results)
  else:
      # Handle errors
      print(log.error)
  ```

- **Managing Cache:**

  ```python
  from inspect_ai.log import cache_prune

  # Prune expired cache entries
  cache_prune()
  ```

- **Custom Automation:**
  - Combine Inspect's API with other Python tools to build custom evaluation pipelines, dashboards, or reporting systems.

## Conclusion

Inspect offers a robust framework for designing, executing, and managing evaluations of large language models. By leveraging its modular components—tasks, solvers, scorers, and tools—users can create intricate evaluation workflows tailored to diverse testing scenarios. Additionally, Inspect's support for extensions and integrations ensures adaptability to evolving evaluation needs and model advancements.

For detailed examples, advanced configurations, and troubleshooting, refer to the [Tutorial](#tutorial) and other comprehensive sections within Inspect's documentation.