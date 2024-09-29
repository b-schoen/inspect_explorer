# Inspect Explorer

- [Inspect Explorer](#inspect-explorer)
- [What Are All These Wrappers Doing?](#what-are-all-these-wrappers-doing)
  - [Task](#task)
- [Core Concepts](#core-concepts)
  - [Task](#task-1)


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
