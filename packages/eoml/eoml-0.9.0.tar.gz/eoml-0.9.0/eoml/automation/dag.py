"""
Directed Acyclic Graph (DAG) module for task automation.

This module provides classes for creating and managing directed acyclic graphs
of tasks with dependencies. It enables workflow automation and task orchestration
for machine learning experiments.
"""


class TaskGraph:
    """
    Container for a directed acyclic graph of tasks.

    The TaskGraph manages a collection of tasks with dependencies, ensuring
    unique task names and maintaining the execution order.

    Attributes:
        task_list (list): Ordered list of tasks in the graph.
        task_dic (dict): Dictionary mapping task names to task objects.
    """

    def __init__(self, task_list):
        """
        Initialize a TaskGraph with a list of tasks.

        Args:
            task_list (list): List of Task objects to include in the graph.

        Raises:
            Exception: If duplicate task names are found.
        """
        self.task_list = task_list
        self.task_dic = self._make_task_dic(task_list)

        for t in task_list:
            t.task_graph = self

    def _make_task_dic(self, task_list):
        """
        Create a dictionary mapping task names to task objects.

        Args:
            task_list (list): List of Task objects.

        Returns:
            dict: Dictionary with task names as keys and Task objects as values.

        Raises:
            Exception: If duplicate task names are found.
        """
        task_dic = {}
        for task in task_list:
            if task.name in task_dic:
                raise Exception(f"Duplicate task with task id {task.name}, task id should be unique ")

            task_dic[task.name] = task

        return task_dic

    def manage_outputs(self, task_id, outputs):
        """
        Manage outputs of a task and propagate them to dependent tasks.

        Args:
            task_id: Identifier of the task producing outputs.
            outputs: Outputs produced by the task.

        Note:
            This method is a placeholder and needs implementation.
        """
        # todo need function
        index = self.task_list.index(task_id)

        for n in range(index, len(self.task_list)):
            pass


class Task:
    """
    Base class representing a task in a task graph.

    A task has a name, inputs, and can be executed as part of a workflow.
    Tasks can depend on outputs from other tasks in the graph.

    Attributes:
        name (str): Unique identifier for the task.
        inputs (list): List of TaskInput objects defining task inputs.
        need (dict): Dictionary of dependencies on other tasks.
        task_graph (TaskGraph): Reference to the containing task graph.
    """

    def __init__(self, name, inputs):
        """
        Initialize a Task.

        Args:
            name (str): Unique identifier for the task.
            inputs (list): List of TaskInput objects defining inputs.
        """
        self.name = name
        self.inputs = inputs

        self.need = self._need()

        self.task_graph: TaskGraph = None

    def make_input(self):
        """
        Resolve task inputs from the task graph.

        Returns:
            dict: Dictionary of resolved input values, with input names as keys.
        """
        inputs_dic = {}

        for task_input in self.inputs:

            if task_input.depend:
                inputs_dic[task_input.name] = self.task_graph.task_dic[task_input.value]
            else:
                inputs_dic[task_input.name] = task_input.value

        return inputs_dic

    def _need(self):
        """
        Compute the dependencies the task needs from other tasks.

        Returns:
            dict: Dictionary mapping dependency names to lists of input names.

        Note:
            This method needs implementation (TODO noted in original code).
        """
        # TODO

        need = {}
        for i in self.inputs:
            if i.depend:
                need.get(i.value, []).append(i.name)

        return need

    def execute(self):
        """
        Execute the task by resolving inputs and calling process().

        This method resolves all inputs from the task graph and passes them
        to the process() method for execution.
        """
        inputs = self.make_input()
        self.process(**inputs)

    def process(self, **inputs):
        """
        Process the task with resolved inputs.

        This is a placeholder method to be overridden by subclasses to implement
        specific task logic.

        Args:
            **inputs: Resolved input values as keyword arguments.
        """
        pass


class TaskInput:
    """
    Represents an input to a task.

    A TaskInput can either be a direct value or a dependency on another task's output.

    Attributes:
        name (str): Name of the input parameter.
        value: The value or name of the dependency.
        depend (bool): If True, value refers to another task name; if False, value is used directly.
    """

    def __init__(self, name, value, depend=False):
        """
        Initialize a TaskInput.

        Args:
            name (str): Name of the input parameter.
            value: The value or name of the dependency.
            depend (bool, optional): Whether this input depends on another task. Defaults to False.
        """
        self.name = name
        self.value = value
        self.depend = depend


class Value(Task):
    """
    A task that represents a constant value.

    This is a simple task type that holds a value without any inputs or processing.
    Useful for providing constant parameters to other tasks in the graph.

    Attributes:
        value: The constant value held by this task.
    """

    def __init__(self, name, value):
        """
        Initialize a Value task.

        Args:
            name (str): Unique identifier for the task.
            value: The constant value to hold.
        """
        super().__init__(name, [])
        self.value = value


class ReadProfile(Task):
    """
    A task for reading a profile or configuration.

    This task is intended to read and provide configuration profiles to other tasks.

    Note:
        This appears to be a placeholder class requiring implementation.
    """

    def __init__(self, name):
        """
        Initialize a ReadProfile task.

        Args:
            name (str): Unique identifier for the task.
        """
        super().__init__(name, [])
