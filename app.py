from recordtype import recordtype

# weight is the priority of the task
# duration is how long it will take to complete the task
# due is the due date of the task
# done is the date the task is completed (starts with 0, and set to whenever the task is done)
Task = recordtype('Task', 'weight duration due done')

import numpy as np


# create todo task
def create_tasks(num):
    tasks = []
    distribution = np.round(np.random.exponential(5, 10000))
    for i in range(num):
        weight = np.random.randint(1, 100)
        due = np.random.choice(distribution) + 1
        duration = np.random.randint(0, due)
        t = Task(weight=weight, duration=duration, due=due, done=0)
        tasks.append(t)
    return tasks


# Tallies up the results from running the simulation. Calculates:
# 1. percentage of completed tasks
# 2. percentage of important tasks completed
# 3. percentage of tasks completed in time
def tally(completed_tasks, all_tasks):
    # percentage of tasks completed
    completed = len(completed_tasks) / len(all_tasks)

    # set the 75th percentile of all tasks based on weight as the important tasks
    percentile = round(0.75 * len(all_tasks))
    important_tasks = sorted(all_tasks,
                             key=lambda x: x.weight)[percentile:len(all_tasks)]

    # count how many important tasks have been completed
    overlap = 0
    for t in important_tasks:
        if t in completed_tasks:
            overlap += 1
    # the weight is the percentage of important tasks completed
    if len(important_tasks) > 0:
        important = overlap / len(important_tasks)
    else:
        important = 0

    # percentage of tasks that are completed in time
    intime_tasks = []
    for task in completed_tasks:
        if task.done <= task.due:
            intime_tasks.append(task)
    intime = len(intime_tasks) / len(all_tasks)

    return (completed, important, intime)


def duration(task):
    return task.duration


# run a single simulation
def simulate(ratio, *tasks):
    deadline = ratio * sum(list(map(duration, tasks)))
    completed_tasks = []
    elapsed_time = 0
    for task in tasks:
        elapsed_time += task.duration
        if elapsed_time <= deadline:
            task.done = elapsed_time
            completed_tasks.append(task)
        else:
            break

    return tally(completed_tasks, tasks)


def add(a, b):
    return tuple(map(lambda x, y: x + y, a, b))


def divide(a, b):
    return tuple([x / b for x in a])


# run multipl eiterations of the simulation
def run(ratio, iterations, num, algorithm):
    results, final_results = (0, 0, 0), (0, 0, 0)

    for i in range(iterations):
        tasks = create_tasks(num)
        results = simulate(ratio, *tuple(algorithm(*tasks)))
        final_results = add(final_results, results)

    return divide(final_results, iterations)


# print results from running the simulation
def print_results(data):
    params = ("- tasks completed", "- important tasks completed",
              "- tasks completed in time")
    for d, p in zip(data, params):
        print("{0:s} :  {1:3.2f}%".format(p.ljust(40, ' '), d * 100))


def as_they_come(*tasks):
    return tasks


def due_first(*tasks):
    return sorted(tasks, key=lambda x: x.due)


def due_last(*tasks):
    return sorted(tasks, key=lambda x: x.due, reverse=True)


def important_first(*tasks):
    return sorted(tasks, key=lambda x: x.weight, reverse=True)


def easier_first(*tasks):
    return sorted(tasks, key=lambda x: x.duration)


def easier_important_first(*tasks):
    return sorted(tasks, key=lambda x: x.duration / x.weight)


def easier_due_first(*tasks):
    return sorted(tasks, key=lambda x: x.duration / x.due)


# %matplotlib inline
import matplotlib.pyplot as plt


def chart(data, title):
    labels = np.array(['Completed Tasks', 'Important Tasks', 'In Time Tasks'])
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    colors = [
        'blue', 'red', 'green', 'violet', 'blueviolet', 'orange', 'deepskyblue'
    ]
    for d, t, c in zip(data, title, colors):
        fig = plt.figure()
        d = np.concatenate((d, [d[0]]))
        ax = fig.add_subplot(111, polar=True)
        ax.set_title(t, weight='bold', size='large')
        ax.plot(angles, d, 'o-', linewidth=2, color=c)
        ax.fill(angles, d, alpha=0.25, color=c)
        ax.set_thetagrids(angles * 180 / np.pi, labels)
        ax.set_ylim(0, 1.0)
        ax.grid(True)


# deadline ratio
ratio = 0.5
# number of iterations to run
iterations = 20000
# no of tasks
num = 25

algorithms = (as_they_come, due_first, due_last, important_first, easier_first,
              easier_important_first, easier_due_first)

labels = ("Do as they come", "Due tasks first", "Due tasks last",
          "Important tasks first", "Easier tasks first",
          "Easier important tasks first", "Easier due tasks first")

data = []

# run the simulation for each algorithm and print out the results
for algo, label in zip(algorithms, labels):
    d = run(ratio, iterations, num, algo)
    print(label)
    print_results(d)
    data.append(d)
    print()

# also create a radar chart for each algorithm
chart(data, labels)