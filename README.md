# Inspect Explorer

- [Inspect Explorer](#inspect-explorer)
- [What Are All These Wrappers Doing?](#what-are-all-these-wrappers-doing)
  - [Task](#task)
- [What is a solver?](#what-is-a-solver)
  - [Interaction between Solver and TaskState](#interaction-between-solver-and-taskstate)
- [Okay so what is a scorer?](#okay-so-what-is-a-scorer)
- [Wait Choice and Choices have their own classes?](#wait-choice-and-choices-have-their-own-classes)
- [So what is ModelOutput?](#so-what-is-modeloutput)
- [Eval Logs](#eval-logs)
  - [EvalLog](#evallog)
  - [EvalResults](#evalresults)
  - [EvalScore](#evalscore)
  - [EvalSample](#evalsample)
- [Core Concepts](#core-concepts)
  - [Task](#task-1)
  - [TaskState](#taskstate)


ARENA:
- [ARENA_evals/w2-d3-bschoen](https://github.com/chloeli-15/ARENA_evals/compare/main...w2-d3-bschoen)
- [ARENA_evals/w2-d4-bschoen](https://github.com/chloeli-15/ARENA_evals/compare/main...w2-d4-bschoen)
- [mcq_examples.json](https://github.com/chloeli-15/ARENA_evals/blob/11b089c38da4efed4964deb33ef0d1beac1bf90e/day1-3_dataset_generation/workspace/mcq_examples.json)
- [NOTES.md](https://github.com/chloeli-15/ARENA_evals/blob/11b089c38da4efed4964deb33ef0d1beac1bf90e/day1-3_dataset_generation/NOTES.md)


# What Are All These Wrappers Doing?

## Task

We'll start with `hello_world.py`. What's happening here?

```python

import inspect_ai

@inspect_ai.task
def hello_world():
    return inspect_ai.Task(
        dataset=[
            inspect_ai.dataset.Sample(
                input="Just reply with Hello World",
                target="Hello World",
            )
        ],
        solver=[
            inspect_ai.solver.generate(),
        ],
        scorer=inspect_ai.scorer.exact(),
    )
```

Let's break it down:

```python

import inspect_ai as iai

@iai.task
def hello_world() -> iai.Task:

    dataset: iai.Dataset | Sequence[iai.dataset.Sample] = [
        iai.dataset.Sample(
            input="Just reply with Hello World",
            target="Hello World",
        )
    ]

    # how do we generate an answer
    solver: iai.solver.Solver | list[iai.solver.Solver] = [iai.solver.generate()]

    # how do we score the answer
    scorer: iai.scorer.Scorer | list[iai.scorer.Scorer] = [iai.scorer.exact()]

    task = iai.Task(dataset=dataset, solver=solver, scorer=scorer)

    return task
```

Okay, so what is `inspect_ai.task` doing? Why is it there?

```python
# in inspect_explorer/inspect_ai/src/inspect_ai/_util/registry.py

# There's a big global registry so that things can be discovered via cli
REGISTRY_INFO = "__registry_info__"
REGISTRY_PARAMS = "__registry_params__"
_registry: dict[str, object] = {}

# The different `@task`, `@solver`, etc. decorators add to the registry
RegistryType = Literal["task", ..., "solver", "scorer", ...]

class RegistryInfo(BaseModel):
    type: RegistryType
    name: str
    metadata: dict[str, Any] = Field(default={})

def registry_add(o: object, info: RegistryInfo) -> None:
    setattr(o, REGISTRY_INFO, info)
    _registry[registry_key(info.type, info.name)] = o

# in inspect_explorer/inspect_ai/src/inspect_ai/_eval/registry.py

def task_register(create_task_fn: TaskType, name: str, attribs: dict[str, Any], params: list[str]) -> TaskType:
    
    # add to registry
    registry_add(create_task_fn, RegistryInfo(type="task", name=name, metadata=dict(attribs=attribs, params=params)))
    
    # return the original object
    return create_task_fn

# lots and lots and lots of wrapping, but at the end of the day returns the original function
# and created object when called
#
# importantly, this doesn't change the type signature
#
# assigns a name to the task *creation* function, not the task itself
#
def task(*create_task_fns: TaskType | None, name: str | None = None, **attribs: Any) -> Any:
    r"""Decorator for registering tasks.

    Args:
      *task (TaskType): 
        Function returning `Task` targeted by plain task decorator without attributes (e.g. `@task`)
      name (str | None):
        Optional name for task. If the decorator has no name argument then the name of the function
        will be used to automatically assign a name.
      **attribs: (dict[str,Any]):
        Additional task attributes.

    Returns:
        Task with registry attributes.
    """

    def create_task_wrapper(task_type: TaskType) -> TaskType:
        # get the name and params
        task_name = registry_name(task_type, name or getattr(task_type, "__name__"))
        params = list(inspect.signature(task_type).parameters.keys())

        # create the task, register it, and return the original task unmodified
        def wrapper(*w_args: Any, **w_kwargs: Any) -> Task:
            # create the task
            task = task_type(*w_args, **w_kwargs)

            # create registry info
            registry_info = RegistryInfo(type="task", name=task_name, metadata=dict(attribs=attribs, params=params))

            # tag it
            registry_tag(task_type, task, registry_info, *w_args, **w_kwargs)

            # return it
            return task

        # also returns the original object
        return task_register(create_task_fn=wrapper, name=task_name, attribs=attribs, params=params)

    if task:
        return create_task_wrapper(cast(TaskType, task[0]))
    else:
        return create_task_wrapper
```




---

# What is a solver?

> [!NOTE] A solver is a Python function that takes a TaskState and generate function, and then transforms and returns the TaskState (the generate function may or may not be called depending on the solver).

> [!NOTE] We can use `Scoring in Solvers` to use scorers in solvers

```python
GenerateFn = Callable[[TaskState], Awaitable[TaskState]]

async def solve_fn(state: TaskState, generate_fn: GenerateFn) -> TaskState:

    new_state = potentially_mutate_state(state)

    # ex: system_message() solver inserts a system message into the chat history.
    #
    # ex: chain_of_thought() solver takes the original user prompt and re-writes it to ask
    #     the model to use chain of thought reasoning to come up with its answer.
    new_state = modify_message_history(new_state)

    # ex: self_critique() solver:
    #  - takes the ModelOutput and then
    #  - sends it to another model for critique.
    #  - It then replays this critique back within the messages stream as a user message
    #  - and re-calls generate to get a refined answer
    new_state = add_a_message(new_state)

    # can also use `generate` to do multi turn stuff or stuff involving the model

    # get next model response after some modifications, so can basically do anything here
    new_state = generate_fn(new_state)
    
    return new_state
```

for example, full source code of `inspect_ai.solver.generate` is:

```python
def generate() -> Solver:

    async def solve_fn(state: TaskState, generate_fn: GenerateFn) -> TaskState:
        return await generate_fn(state)

    return solve_fn
```

so a solver is just something that creates a `solve_fn`

```python
def example_solver() -> Solver:

    async def solve_fn(state: TaskState, generate_fn: GenerateFn) -> TaskState:

      new_state = potentially_mutate_state(state)

      # ex: system_message() solver inserts a system message into the chat history.
      #
      # ex: chain_of_thought() solver takes the original user prompt and re-writes it to ask
      #     the model to use chain of thought reasoning to come up with its answer.
      new_state = modify_message_history(new_state)

      # ex: self_critique() solver:
      #  - takes the ModelOutput and then
      #  - sends it to another model for critique.
      #  - It then replays this critique back within the messages stream as a user message
      #  - and re-calls generate to get a refined answer
      new_state = add_a_message(new_state)

      # can also use `generate` to do multi turn stuff or stuff involving the model

      # get next model response after some modifications, so can basically do anything here
      new_state = generate_fn(new_state)
      
      return new_state

    return solve_fn
```


Tasks have a single top-level solver that defines an execution plan. 

This solver could be implemented with:
 - arbitrary Python code (calling the model as required)
 - could consist of a set of other sovlers composed together. 

Solvers can therefore play two differnet roles:

1. Composite specifications for task execution; and
2. Components that can be chained together.

> [!NOTE] While chains are frequently used in more straightforward knowledge and reasoning evaluations, fully custom solver functions are often used for multi-turn dialog and agent evaluations.

- This section covers mostly solvers as components (both built in and creating your own). 
- The `Agents` section describes fully custom sovlers in more depth.

## Interaction between Solver and TaskState

```python
class TaskState:
    messages: list[ChatMessage],
    output: ModelOutput

    @property
    def user_prompt(self) -> str:
        return self.messages[0].content

    # -- metadata --

    # original sample metadata
    #
    #   - note: often used to:
    #      - coordinate between solvers
    #      - store additional information for logging
    #
    metadata: dict[str, Any]

    # -- original sample input, unchanged by solvers --

    input: str | list[ChatMessage]

    @property
    def input_text(self) -> str:
        return self.input

    # -- access info about the evaluation --
    choices: list[str] | None
    epoch: int
    sample_id: int | str
    model: str

```


Examples:
- A prompt engineering solver will modify the content of messages.
- A model generation solver will call the model, append an assistant message, and set the output
- A multi-turn dialog solver might do this in a loop

---

# Okay so what is a scorer?

> [!NOTE] Scorers can return dicts, and this will be correctly handled by metrics

> [!NOTE] We don't get a `generate` function passed in, but `model_graded_qa` is example of how you just have it be stateful and call `await generate_fn(state)` in the scorer

```python
async def score(state: TaskState, target: Target) -> Score:
  # Compare state / model output with target to yield a score

  model_output: ModelOutput = state.output

  value = compute_score_of_model_output(model_output, target)

  return Score(value=value)
```

So what's a score?

```python
class Score:
    value: Value

    # parsed answer
    answer: str | None

    # explanation of score, ex: full grader model output
    explanation: str | None

    # additional metadata about the score to be logged, empty by default
    metadata: dict[str, Any] | None

```

and `Value` is just a value holder type:

```python
Value = Union[
    str | int | float | bool,
    list[str | int | float | bool],
    dict[str, str | int | float | bool],
]
```


---

# Wait Choice and Choices have their own classes?

```python
@dataclass
class Choice:
    """
    A `Choice` represents a single choice in a multiple choice question.

    It is only relevant for the `multiple_choice` solver and corresponding `choice` scorer.
    """

    value: str
    """The original value of the choice from the `Sample`."""

    correct: bool | None
    """Did the model think this choice satisfies the question? `None` indicates this has not been set yet"""

    original_position: int
    """Choices may be re-ordered during processing, this represents the original position in the sample."""
```

```python
class Choices(Sequence[Choice]):

    def mark_choice(self, index: int, correct: bool) -> None:
        """Set the value of a specific choice"""
        self._choices[index].correct = correct

    def shuffle(self, rand: Random = Random()) -> None:
        ...

    def prompt(self, question: str, template: str) -> str:
        ...
```

---




# So what is ModelOutput?

```python
class ModelOutput(BaseModel):
    model: str = Field(default="")
    """Model used for generation."""

    choices: list[ChatCompletionChoice] = Field(default=[])
    """Completion choices."""

    usage: ModelUsage | None = Field(default=None)
    """Model token usage"""

    error: str | None = Field(default=None)
    """Error message in the case of content moderation refusals."""

    @property
    def stop_reason(self) -> StopReason:
        """First message stop reason."""
        return self.choices[0].stop_reason

    @property
    def message(self) -> ChatMessageAssistant:
        """First message choice."""
        return self.choices[0].message

    @property
    def completion(self) -> str:
        """Text of first message choice text."""
        if len(self.choices) > 0:
            return self.choices[0].message.text
        else:
            return ""
```

---

# Eval Logs

## EvalLog

```python
# all defined here https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/src/inspect_ai/log/_log.py#L422

# grab one to look more closely at
eval_log: inspect_ai.log.EvalLog = eval_logs[-1]

"""
success
"""
rich.print(eval_log.status)

"""
EvalSpec(
    task='benchmark_eval',
    task_version=0,
    task_file=None,
    task_id='jFwjfvnUugqjYJtNWDhMZ5',
    run_id='GDJhQMfHrJtN3G68T4TUCb',
    created='2024-09-18T15:22:13+00:00',
    dataset=EvalDataset(
        name='mcq_examples',
        location='/root/ARENA_evals/day1-3_dataset_generation/workspace/mcq_examples.json',
        samples=20,
        shuffled=False
    ),
    sandbox=None,
    model='anthropic/claude-3-opus-20240229',
    model_base_url=None,
    task_attribs={},
    task_args={'multiple_choice_template': '\\n{question}\\n{choices}', 'is_test_dataset': False},
    model_args={},
    config=EvalConfig(
        limit=None,
        epochs=None,
        epochs_reducer=None,
        fail_on_error=None,
        max_messages=None,
        max_samples=None,
        max_tasks=None,
        max_subprocesses=None,
        sandbox_cleanup=None,
        log_samples=None,
        log_images=None,
        log_buffer=None
    ),
    revision=EvalRevision(type='git', origin='git@github.com:chloeli-15/ARENA_evals.git', commit='e750dd5'),
    packages={'inspect_ai': '0.3.27'},
    metadata=None
)
"""
rich.print(eval_log.eval)

"""
EvalPlan(
    name='plan',
    steps=[
        EvalPlanStep(solver='multiple_choice_format', params={'template': '\\n{question}\\n{choices}'}),
        EvalPlanStep(solver='generate', params={})
    ],
    finish=None,
    config=GenerateConfig(
        max_retries=None,
        timeout=None,
        max_connections=None,
        system_message=None,
        max_tokens=None,
        top_p=None,
        temperature=None,
        stop_seqs=None,
        best_of=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias=None,
        seed=None,
        suffix=None,
        top_k=None,
        num_choices=None,
        logprobs=None,
        top_logprobs=None,
        parallel_tool_calls=None,
        cache_prompt=None
    )
)
"""
rich.print(eval_log.plan)

"""
EvalStats(
    started_at='2024-09-18T15:22:13+00:00',
    completed_at='2024-09-18T15:23:19+00:00',
    model_usage={
        'anthropic/claude-3-opus-20240229': ModelUsage(
            input_tokens=4652,
            output_tokens=8039,
            total_tokens=12691,
            input_tokens_cache_write=None,
            input_tokens_cache_read=None
        ),
        'openai/gpt-4o-mini': ModelUsage(
            input_tokens=9390,
            output_tokens=140,
            total_tokens=9530,
            input_tokens_cache_write=None,
            input_tokens_cache_read=None
        )
    }
)
"""
rich.print(eval_log.stats)

"""
none
"""
rich.print(eval_log.error)
```

## EvalResults

```python
assert eval_log.results
eval_results: inspect_ai.log.EvalResults = eval_log.results

"""
None
"""
rich.print(eval_results.metadata)

"""
20
"""
rich.print(eval_results.total_samples)

"""
20
"""
rich.print(eval_results.completed_samples)

eval_scores: list[inspect_ai.log.EvalScore] = eval_results.scores

rich.print(f"Num eval scores:\t{len(eval_scores)}")
```

## EvalScore

```python
# look at one of them
eval_score: inspect_ai.log.EvalScore = eval_scores[0]

"""
EvalScore(
    name='model_graded_qa_single',
    scorer='model_graded_qa_single',
    reducer=None,
    params={'model': 'openai/gpt-4o-mini'},
    metrics={
        'mean': EvalMetric(name='mean', value=2.3333333333333335, options={}, metadata=None),
        'stderr': EvalMetric(name='stderr', value=0.33333333333333337, options={}, metadata=None)
    },
    metadata=None
)
"""
rich.print(eval_score)
```

## EvalSample

```python
# look at individual samples
assert eval_log.samples
eval_samples: list[inspect_ai.log.EvalSample] = eval_log.samples

print(f"Num eval samples:\t{len(eval_samples)}")

# look at one of them
eval_sample: inspect_ai.log.EvalSample = eval_samples[0]

"""
EvalSample(
    id=1,
    epoch=1,
    input=[
        ChatMessageUser(
            content='Please include your answer inside <answer> </answer> tags. ...',
            source=None,
            role='user'
        )
    ],
    choices=['Immediate deployment', '2-month refinement', '4-month refinement', '6-month refinement'],
    target='6-month refinement',
    sandbox=None,
    files=None,
    setup=None,
    messages=[
        ...
        TONS OF STUFF OMITTED HERE
        ...
    ],

"""
rich.print(eval_sample)

# %%

"""
ModelOutput(
    model='claude-3-opus-20240229',
    choices=[
        ChatCompletionChoice(
            message=ChatMessageAssistant(
                content=[
                    ContentText(
                        type='text',
                        text='To determine the optimal ... factors.\n</answer>'
                    )
                ],
                source='generate',
                role='assistant',
                tool_calls=None
            ),
            stop_reason='stop',
            logprobs=None
        )
    ],
    usage=ModelUsage(
        input_tokens=235,
        output_tokens=388,
        total_tokens=623,
        input_tokens_cache_write=None,
        input_tokens_cache_read=None
    ),
    error=None
)
"""
rich.print(eval_sample.output)

# %%

"""
{
    'model_graded_qa_single': Score(
        value=2.0,
        answer='To determine the optimal deployment timeline, ... </answer>',
        explanation='<score>2</score>',
        metadata={
            'grading': [
                [[ACTUAL GRADING MODEL INPUT]],
                {
                    'content': '<score>2</score>',
                    'source': 'generate',
                    'role': 'assistant'
                }
            ]
        }
    )
}
"""
rich.print(eval_sample.scores)
```

---

# Core Concepts

Note: These are psuedoclasses, the actual classes are harder to read.

## Task

```python
@dataclass
class Task:

    # Dataset to evaluate
    dataset: Dataset | Sequence[Sample]

    # Solver or list of solvers. Defaults to generate(), a normal call to the model.
    solver: Solver | list[Solver] = field(default_factory=lambda: generate())

    # Scorer used to evaluate model output.
    scorer: Scorer | list[Scorer] | None = None

    # Alternative metrics (overrides the metrics provided by the specified scorer).
    metrics: list[Metric] | dict[str, list[Metric]] | None = None

    # Model generation config.
    config: GenerateConfig = field(default_factory=GenerateConfig)

    # Sandbox environment type (or optionally a tuple with type and config file)
    sandbox: str | tuple[str, str] | None = None

    # Epochs to repeat samples for and optional score reducer function(s) used to combine sample scores (defaults to "mean")
    epochs: int | Epochs | None = None

    # `True` to fail on first sample error (default); `False` to never fail on sample errors; 
    # Value between 0 and 1 to fail if a proportion of total samples fails. 
    # Value greater than 1 to fail eval if a count of samples fails.
    fail_on_error: bool | float | None = None

    # Limit on total messages in the conversation.
    max_messages: int | None = None

    # Task name. If not specified is automatically determined based on the name of the task directory 
    # (or "task" if it's an anonymous task, e.g., created in a notebook and passed to eval() directly)
    name: str | None = None

    # Version of task (to distinguish evolutions of the task spec or breaking changes to it)
    version: int = 0
```

## TaskState

```python
class TaskState:
    messages: list[ChatMessage],
    output: ModelOutput
```
